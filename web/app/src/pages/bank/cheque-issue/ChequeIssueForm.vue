<template>
  <div>
    <q-form class="q-pa-lg print-hide" autofocus>
      <q-card>
        <q-card-section class="bg-green text-white">
          <div class="text-h6">
            <span v-if="!isEdit">New Cheque Issue</span>
            <span v-else>Update Cheque | #{{ fields.cheque_no }}</span>
          </div>
        </q-card-section>

        <q-card class="q-mt-none q-ml-lg q-mr-lg q-mb-lg">
          <q-card-section>
            <div class="row q-col-gutter-md">
              <div class="col-md-6 col-12">
                <n-auto-complete-v2 v-model="fields.bank_account" endpoint="v1/cheque-issue/create-defaults/bank_accounts"
                 :options="formDefaults.collections?.bank_accounts" label="Bank Account *" :disabled="isEdit"
                 :staticOption="fields.selected_bank_account_obj" :error="errors?.bank_account" @update:modelValue="updateBankAccount" />
              </div>
              <date-picker v-model="fields.date" class="col-md-6 col-12" label="Date *" :error-message="errors.date"
                :error="!!errors.date"></date-picker>
            </div>
            <div class="row q-col-gutter-md">
              <q-input v-model="fields.cheque_no" label="Cheque Number" class="col-md-6 col-12"
                :error-message="errors.cheque_no" :error="!!errors.cheque_no" :disable="isEdit" type="number" />
              <q-input v-model="fields.amount" label="Amount *" class="col-md-6 col-12" :error-message="errors.amount"
                type="number" :error="!!errors.amount" />
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-8">
                <n-auto-complete-v2 v-if="!showDrAccount" v-model="fields.party" :options="formDefaults.collections?.parties"
                  :staticOption="fields.selected_party_obj" endpoint="`v1/${route.params.company}cheque-issue/create-defaults/parties`" label="Party *" :error="errors?.party" />
                <div class="row" v-else>
                  <q-input v-model="fields.issued_to" label="Issued To" class="col-12" :error-message="errors.issued_to"
                    :error="!!errors.issued_to" />
                </div>
              </div>
              <div>
                <q-btn @click.prevent="toggleDrAccount" square icon="groups_2" class="q-mt-md" />
              </div>
            </div>
            <div class="row q-col-gutter-md" v-if="showDrAccount">
              <div class="col-8">
                <n-auto-complete-v2 v-model="fields.dr_account" :options="formDefaults.collections?.accounts"
                  :staticOption="fields.selected_dr_account_obj" endpoint="v1/cheque-issue/create-defaults/accounts" label="Dr Account" :modal-component="BenefactorForm" :error="errors?.dr_account" />
              </div>
            </div>
          </q-card-section>
          <div class="q-pr-md q-pb-lg row justify-between">
            <div class="row q-gutter-md">
              <q-btn @click="exportPDF" v-if="fields?.status === 'Issued' || fields?.status === 'Cleared'" color="green"
                outline class="q-px-lg q-py-sm" style="display: inline-block;">Print Pdf</q-btn>
              <q-btn @click="onChequePrint" v-if="fields?.status === 'Issued' || fields?.status === 'Cleared'"
                color="green" outline class="q-px-lg q-py-sm" style="display: inline-block;" label="Print Cheque"></q-btn>
              <q-btn v-if="['Issued', 'Cleared'].includes(fields.status) && checkPermissions('ChequeIssueCancel')"
                @click.prevent="isDeleteOpen = true" icon="block" color="red" label="Cancel" class="q-ml-md" />
            </div>
            <div>
              <q-btn v-if="checkPermissions('ChequeIssueCreate') && !isEdit" @click.prevent="submitForm" color="green"
                label="Create" class="q-ml-auto" type="submit" />
              <q-btn v-if="checkPermissions('ChequeIssueModify') && isEdit" @click.prevent="submitForm" color="green"
                label="Update" class="q-ml-auto" type="submit" />
            </div>
          </div>
        </q-card>
      </q-card>
    </q-form>
    <div class="print-only">
      <div class="cheque-con" id="cheque-con">
        <div class="date">
          {{ (fields.date.replaceAll('-', '')).split('').join('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;') }}
        </div>
        <div class="payee">
          {{ fields.payee }}
        </div>
        <div class="amt1">
          {{ amtArrayComputed[0] }}
        </div>
        <div class="amt2">
          {{ amtArrayComputed[1] }}
        </div>
        <div class="amt-num">
          {{ formatNumberWithCommas(fields.amount) + '/-' }}
        </div>
      </div>
    </div>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 400px)">
        <q-card-section class="bg-red-6 q-py-md flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense v-close-popup />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500;">
            Are you sure?
          </div>
          <div class=" text-blue">
            <div class="row justify-end">
              <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)"></q-btn>
              <q-btn flat class="text-red" label="Yes"
                @click="cancelForm"></q-btn>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import BenefactorForm from 'src/pages/account/ledger/LedgerForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
import useGenerateChequePdf from 'src/composables/pdf/useGenerateChequePdf'
import formatNumberWithCommas from 'src/composables/formatNumberWithComma'
// const $q = useQuasar()

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint =  `/v1/${route.params.company}cheque-issue/`
    const showDrAccount = ref(false)
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/cheque-issue/list/',
    })
    const isDeleteOpen = ref(false)
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value ? 'Update Cheque' : 'Issue Cheque') +
          ' | Awecount',
      }
    })
    formData.fields.value.date = formData.fields.value.date || formData.today
    const toggleDrAccount = () => {
      showDrAccount.value = !showDrAccount.value
      formData.fields.value.issued_to = null
      formData.fields.value.dr_account = null
      formData.fields.value.party = null
    }
    if (formData.fields.value.issued_to || formData.fields.value.dr_account) {
      showDrAccount.value = true
    }

    watch(formData.fields, (a) => {
      if (a.issued_to || a.dr_account) {
        showDrAccount.value = true
      }
    })

    const exportPDF = () => {
      const printData = useGenerateChequePdf(formData.fields.value)
      usePrintPdfWindow(printData)
    }
    const onChequePrint = () => {
      import('jspdf').then(({ jsPDF }) => {
        const doc = new jsPDF({
          orientation: 'landscape',
          unit: 'in',
          format: [7.5, 3.5]
        })
        const amt = formData.fields.value.amount_in_words + ' only'
        const amountArray = splitString(amt, 50)
        doc.setFontSize(13)
        const dateArray = (formData.fields.value.date.replaceAll('-', '')).split('')
        const dateString = dateArray.join('   ')
        doc.text(dateString, 5.45, 0.5)
        doc.text(formData.fields.value.payee, 1.7, 0.925)
        doc.text(`${formatNumberWithCommas(formData.fields.value.amount)}` + '/-', 5.5, 1.35)
        doc.text(amountArray[0], 1, 1.2)
        if (amountArray[1]) {
          doc.text(amountArray[1], 0.75, 1.45)
        }
        doc.save('a4.pdf')
      })
    }
    const updateBankAccount = () => {
      const { bank_account } = formData.fields.value
      const bank_accounts = formData.formDefaults.value.collections.bank_accounts.results
      if (bank_accounts && bank_account && !formData.fields.value.id) {
        const selected = bank_accounts.find((account) => {
          return bank_account === account.id;
        });
        if (selected.hasOwnProperty('cheque_no')) {
          if (selected.cheque_no) {
            formData.fields.value.cheque_no = selected.cheque_no
          } else {
            formData.fields.value.cheque_no = ''
          }
        }
      }
    }

    function splitString(str, chunkSize) {
      const chunks = [];
      let start = 0;

      while (start < str.length) {
        let end = start + chunkSize;
        if (end >= str.length) {
          end = str.length;
        } else {
          // Find the closest space before the end index
          while (end > start && str[end] !== ' ' && str[end] !== undefined) {
            end--;
          }
        }
        chunks.push(str.slice(start, end).trim()); // Remove leading/trailing spaces
        start = end + 1; // Move start to the next character after the space
      }

      return chunks;
    }
    const amtArrayComputed = computed(() => {
      if (formData.fields.value.amount_in_words) {
        return splitString(formData.fields.value.amount_in_words + ' only', 50)
      }
      else return []
    })

    return {
      ...formData,
      showDrAccount,
      BenefactorForm,
      toggleDrAccount,
      checkPermissions,
      exportPDF,
      updateBankAccount,
      onChequePrint,
      amtArrayComputed,
      formatNumberWithCommas,
      isDeleteOpen
    }
  },
}
</script>

<style scoped>
.cheque-con {
  width: 720px;
  height: 336px;
  box-sizing: border-box;
  position: relative;
  font-size: 13px;
}

.cheque-con .date {
  position: absolute;
  top: 34px;
  right: 20px;
}

.cheque-con .payee {
  position: absolute;
  left: 151px;
  top: 75px;
}

.cheque-con .amt1 {
  position: absolute;
  left: 56px;
  top: 102px;
}

.cheque-con .amt2 {
  position: absolute;
  left: 50px;
  top: 128px;
}

.cheque-con .amt-num {
  position: absolute;
  left: 528px;
  top: 117px;
}

@media print {
  .cheque-con {
    position: absolute;
    top: 0;
  }
}
</style>
