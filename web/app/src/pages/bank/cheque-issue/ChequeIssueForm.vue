<template>
  <q-form class="q-pa-lg" autofocus>
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
              <n-auto-complete v-model="fields.bank_account" :options="formDefaults.collections?.bank_accounts"
                label="Bank Account *" :disabled="isEdit" :error="errors?.bank_account"
                @update:modelValue="updateBankAccount" />
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
              <n-auto-complete v-if="!showDrAccount" v-model="fields.party" :options="formDefaults.collections?.parties"
                label="Party *" :error="errors?.party" />
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
              <n-auto-complete v-model="fields.dr_account" :options="formDefaults.collections?.accounts"
                label="Dr Account" :modal-component="BenefactorForm" :error="errors?.dr_account" />
            </div>
          </div>
        </q-card-section>
        <div class="q-pr-md q-pb-lg row justify-between">
          <div class="row q-gutter-md">
            <q-btn @click="exportPDF" v-if="fields?.status === 'Issued' || fields?.status === 'Cleared'" color="green"
              outline class="q-px-lg q-py-sm" style="display: inline-block;">Print Pdf</q-btn>
            <q-btn @click="onChequePrint" v-if="fields?.status === 'Issued' || fields?.status === 'Cleared'" color="green"
              outline class="q-px-lg q-py-sm" style="display: inline-block;" label="Print Cheque"></q-btn>
            <q-btn v-if="['Issued', 'Cleared'].includes(fields.status) && checkPermissions('ChequeIssueCancel')"
              @click.prevent="cancelForm" icon="block" color="red" :label="'Cancel'" class="q-ml-md" />
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
</template>

<script>
import useForm from '/src/composables/useForm'
import BenefactorForm from 'src/pages/account/ledger/LedgerForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
import useGenerateChequePdf from 'src/composables/pdf/useGenerateChequePdf'
import formatNumberWithCommas from 'src/composables/formatNumberWithComma'
// const $q = useQuasar()

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/cheque-issue/'
    const showDrAccount = ref(false)
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/cheque-issue/list/',
    })
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
      // console.log('print cheque')
      let ifram = document.createElement('iframe')
      ifram.style = 'display:none; margin: 20px'
      document.body.appendChild(ifram)
      const pri = ifram.contentWindow
      pri.document.open()
      pri.document.write(useGenerateChequePdf(formData.fields.value))
      // pri.document.body.firstElementChild.prepend()
      pri.document.close()
      pri.focus()
      setTimeout(() => pri.print(), 100)
    }
    const onChequePrint = () => {
      import("jspdf").then(({ jsPDF }) => {
        const doc = new jsPDF({
          orientation: "landscape",
          unit: "in",
          format: [7.5, 3.5]
        })
        const amt = formData.fields.value.amount_in_words + ' only'
        const amountArray = splitString(amt, 45)
        doc.setFontSize(13)
        const dateArray = (formData.fields.value.date.replaceAll('-', '')).split('')
        const dateString = dateArray.join('   ')
        doc.text(dateString, 5.45, 0.5)
        doc.text(formData.fields.value.payee, 1.8, 0.925)
        doc.text(`${formatNumberWithCommas(formData.fields.value.amount)}` + '/-', 5.5, 1.35)
        doc.text(amountArray[0], 1, 1.2)
        if (amountArray[1]) {
          doc.text(amountArray[1], 0.75, 1.45)
        }
        doc.save("a4.pdf")
      })
    }
    const updateBankAccount = (newValue) => {
      const { bank_account } = formData.fields.value
      const bank_accounts = formData.formDefaults.value.collections.bank_accounts
      if (bank_accounts && bank_account && !formData.fields.value.id) {
        const selected = bank_accounts.find((account) => {
          return bank_account === account.id;
        });
        if (selected.hasOwnProperty("cheque_no")) {
          if (selected.cheque_no) {
            // this.$set(this.fields, "cheque_no", selected.cheque_no);
            formData.fields.value.cheque_no = selected.cheque_no
          } else {
            formData.fields.value.cheque_no = ''
          }
        }
      }
    }
    // function splitString(str, chunkSize) {
    //   const chunks = [];
    //   for (let i = 0; i < str.length; i += chunkSize) {
    //     chunks.push(str.slice(i, i + chunkSize));
    //   }
    //   return chunks;
    // }
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


    return {
      ...formData,
      showDrAccount,
      BenefactorForm,
      toggleDrAccount,
      checkPermissions,
      exportPDF,
      updateBankAccount,
      onChequePrint,
    }
  },
}
</script>