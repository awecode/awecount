<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import useGeneratePosPdf from 'src/composables/pdf/useGeneratePosPdf'
import useForm from 'src/composables/useForm'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import { useLoginStore } from 'src/stores/login-info.js'

const metaData = {
  title: 'POS | Awecount',
}
const totalTableData = ref({
  subTotal: 0,
  discount: 0,
  total: 0,
  totalTax: 0,
  taxName: 'Tax',
  taxRate: null,
  taxableAmount: 0,
  addTotal: 0,
})
useMeta(metaData)
const store = useLoginStore()
const route = useRoute()
const endpoint = `/api/company/${route.params.company}/pos/`
const $q = useQuasar()
const searchTerm = ref(null)
const searchResults = ref(null)
const enterClicked = ref(false)
const currentPage = ref(null)
const partyMode = ref(false)
const staticOptions = {
  discount_types,
  modes,
}
const { fields, errors, formDefaults, today } = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/pos',
})
const partyChoices = ref([])
useApi(`/api/company/${route.params.company}/parties/choices/`).then((choices) => {
  partyChoices.value = choices
})
const switchMode = (fields) => {
  if (fields.mode !== 'Credit') {
    partyMode.value = !partyMode.value
  } else {
    $q.notify({
      color: 'orange-4',
      message: 'Credit customer must be a party!',
    })
  }
}
const deleteRowErr = (index, errors, deleteObj) => {
  if (deleteObj) {
    if (!fields.value.deleted_rows) {
      fields.value.deleted_rows = []
    }
    fields.value.deleted_rows.push(deleteObj)
  }
  if (errors && Array.isArray(errors.rows)) {
    errors.rows.splice(index, 1)
  }
}
const onSubmitClick = (status, noPrint) => {
  if (!fields.value?.rows || !(fields.value.rows.length > 0)) return

  fields.value.status = status
  fields.value.noPrint = noPrint
  if (!partyMode.value) fields.value.customer_name = null
  useApi(`/api/company/${route.params.company}/pos/`, { method: 'POST', body: fields.value })
    .then((data) => {
      handleSubmitSuccess(data, fields.value.noPrint)
    })
    .catch((err) => {
      if (err.status === 400) {
        delete fields.value.status
        delete fields.value.noPrint
        errors.value = err.data
        $q.notify({
          color: 'negative',
          message: 'Please fill out the form correctly.',
          icon: 'report_problem',
        })
      } else if (err.status === 422) {
        useHandleCancelInconsistencyError(`/api/company/${route.params.company}/pos/`, err, fields.value, $q)
          .then((data) => {
            handleSubmitSuccess(data, fields.value.noPrint)
          })
          .catch((error) => {
            delete fields.value.status
            delete fields.value.noPrint
            if (error.status !== 'cancel') {
              $q.notify({
                color: 'negative',
                message:
                  'Server Error! Please contact us with the problem.',
                icon: 'report_problem',
              })
            }
          })
      }
    })
}
fields.value.date = today
fields.value.is_export = false
fields.value.mode = 'Cash'
fields.value.party = ''
fields.value.rows = []
fields.value.due_date = today
// handle Search
const fetchResults = async () => {
  useApi(
    `/api/company/items/pos/?${searchTerm.value ? `search=${searchTerm.value}` : ''}${`&page=${currentPage.value || 1}`}`,
  )
    .then((data) => {
      searchResults.value = data
      if (enterClicked.value) {
        const obj = data.results.find((item) => {
          if (item.code === searchTerm.value) {
            return item
          }
        })
        if (obj) {
          onAddItem(obj)
          searchTerm.value = ''
        }
      }
      enterClicked.value = false
    })
    .catch(() => {
      enterClicked.value = false
    })
}
watch(
  [searchTerm, currentPage],
  (newVal, oldVal) => {
    if (newVal[0] !== oldVal[0]) {
      {
        currentPage.value = 1
        fetchResults()
      }
    } else {
      fetchResults()
    }
  },
  { deep: true },
)
watch(
  () => fields.value.rows,
  (newVal) => {
    if (formDefaults.value.options.persist_pos_items) {
      store.posData = newVal
    }
  },
  {
    deep: true,
  },
)
// handle Search
const onAddItem = (itemInfo) => {
  const index = fields.value.rows.findIndex(
    item => item.item_id === itemInfo.id,
  )
  if (index >= 0) {
    fields.value.rows[index].quantity++
  } else {
    fields.value.rows.push({
      quantity: 1,
      name: itemInfo.name,
      rate: itemInfo.rate,
      item_id: itemInfo.id,
      unit_id: itemInfo.unit_id,
      description: '',
      discount: 0,
      discount_type: null,
      tax_scheme_id: itemInfo.tax_scheme_id,
      discount_id: null,
    })
  }
  searchTerm.value = null
}
const getPartyObj = () => {
  if (fields.value.party && !partyMode.value) {
    const index = partyChoices.value.findIndex(
      item => item.id === fields.value.party,
    )
    return partyChoices.value[index]
  } else {
    return null
  }
}

const hasItemModifyAccess = computed(() => {
  return checkPermissions('ItemModify')
})
watch(
  () => formDefaults.value,
  () => {
    if (formDefaults.value.options.persist_pos_items) {
      fields.value.rows = store.posData || []
    }
  },
)
const discountOptionsComputed = computed(() => {
  if (formDefaults?.value?.collections?.discounts) {
    return staticOptions.discount_types.concat(
      formDefaults.value.collections.discounts,
    )
  } else {
    return staticOptions.discount_types
  }
})

const handleSubmitSuccess = (data, noPrint) => {
  errors.value = {}
  $q.notify({
    color: 'green',
    message: data.status === 'Draft' ? 'Saved As Draft!' : 'Issued!',
    icon: 'check',
  })
  if (data.status !== 'Draft' && !noPrint) {
    const printData = useGeneratePosPdf(
      data,
      getPartyObj(),
      !formDefaults.value.options.show_rate_quantity_in_voucher,
      formDefaults.value.collections.tax_schemes,
    )
    usePrintPdfWindow(printData)
  }
  fields.value.rows = []
  fields.value.mode = 'Cash'
  partyMode.value = false
  fields.value.party = ''
  delete fields.value.status
  delete fields.value.noPrint
  delete fields.value.customer_name
  delete fields.value.discount_type
  delete fields.value.discount
  delete fields.value.remarks
}

const handleKeyDown = (event) => {
  if (event.ctrlKey && event.keyCode === 68) {
    event.preventDefault()
    onSubmitClick('Draft', true)
  } else if (event.ctrlKey && event.keyCode === 83) {
    event.preventDefault()
    onSubmitClick('Issued', true)
  } else if (event.ctrlKey && event.keyCode === 73) {
    event.preventDefault()
    onSubmitClick('Issued')
  }
}
onMounted(() => {
  if (window) {
    window.addEventListener('keydown', handleKeyDown)
  }
})

const modeOptionsComputed = computed(() => {
  const obj = {
    results: ['Cash'],
    pagination: {},
  }
  if (formDefaults.value?.collections?.bank_accounts?.results) {
    obj.results = obj.results.concat(formDefaults.value.collections.bank_accounts.results)
    Object.assign(obj.pagination, formDefaults.value.collections.bank_accounts.pagination)
  }
  return obj
})
</script>

<template>
  <div class="md:grid md:grid-cols-12">
    <div class="border border-r border-black col-span-3">
      <div>
        <q-input
          v-model="searchTerm"
          autofocus
          debounce="250"
          label="&nbsp;&nbsp;Search Items..."
          input-class="pl-2 bg-red-200 focus:bg-green-200"
          class="search-input"
          color="green-8"
          @keypress.enter="enterClicked = true"
        />
        <!-- <div class="row q-py-sm q-px-md text-subtitle2">
              <div class="col-8">Name</div>
              <div class="col-4">Rate</div>
            </div> -->
        <div
          v-for=" item in
            searchResults?.results
            || formDefaults.collections?.items.results
          "
          :key="item.id"
          class="row"
          style="
            border-bottom: 1px lightgrey solid;
            padding: 8px 16px 6px 16px;
            font-size: 13px;
          "
        >
          <div class="col-8">
            <router-link
              v-if="hasItemModifyAccess"
              style="text-decoration: none"
              class="text-blue"
              target="_blank"
              :title="item.code"
              :to="`/items/${item.id}/`"
            >
              {{ item.name }}
            </router-link>
            <span v-else>{{ item.name }}</span>
          </div>
          <div class="col-4">
            <span class="row items-center">
              <span class="col-9" title="Rate">{{ item.rate }}</span>
              <span class="col-3">
                <q-icon name="add" class="add-btn" tabindex="0" @click="onAddItem(item)" />
              </span>
            </span>
          </div>
        </div>
      </div>
      <PaginateList
        v-if="formDefaults.collections?.items.pagination"
        class="q-mt-md"
        :pagination="searchResults?.pagination
          || formDefaults.collections?.items.pagination
        "
        @update-page="(page) => (currentPage = page)"
      />
    </div>
    <div class="col-span-9">
      <q-form>
        <PosInvoiceTable
          v-model="fields.rows"
          :unit-options="formDefaults.collections ? formDefaults.collections.units : null"
          :discount-options="discountOptionsComputed"
          :tax-options="formDefaults.collections?.tax_schemes"
          :main-discount="{
            discount_type: fields.discount_type,
            discount: fields.discount,
          }
          "
          :errors="!!errors?.rows ? errors.rows : null"
          @delete-row-err="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)
          "
          @update-table-data="(val) => totalTableData = val"
        />
        <q-card class="fixed md:w-[calc(75%-32px)] lg:w-[calc(75%-76px)] w-[100%] md:right-4 right-0 bottom-4 border border-solid border-gray-200">
          <div style="width: 100%;">
            <div class="py-4 px-6 w-full bg-white">
              <div class="row justify-between">
                <div class="text-center text-left pt-2">
                  <div v-if="fields.rows.reduce((accumulator, currentDict) => (accumulator + currentDict.quantity), 0)">
                    <div class="font-medium text-gray-500">
                      Rows &nbsp; {{ fields.rows.length }}
                    </div>
                    <div class="font-medium text-gray-500">
                      Items &nbsp;
                      {{ fields.rows.reduce((accumulator, currentDict) => (accumulator + currentDict.quantity), 0)
                      }}
                    </div>
                  </div>
                </div>
                <div class="text-weight-bold text-grey-8 min-w-[250px]">
                  <div class="row mb-1">
                    <div class="col-6 text-right">
                      Sub Total
                    </div>
                    <div class="col-6 q-pl-md" data-testid="computed-subtotal">
                      {{ $nf(totalTableData.subTotal) }}
                    </div>
                  </div>
                  <div v-if="totalTableData.discount" class="row mb-1">
                    <div class="col-6 text-right">
                      Discount
                    </div>
                    <div class="col-6 q-pl-md" data-testid="computed-final-discount">
                      {{ $nf(totalTableData.discount) }}
                    </div>
                  </div>
                  <div v-if="totalTableData.totalTax" class="row mb-1">
                    <div class="col-6 text-right" data-testid="computed-tax-name">
                      {{ totalTableData.taxName }}
                    </div>
                    <div class="col-6 q-pl-md" data-testid="computed-total-tax">
                      {{ $nf(totalTableData.totalTax) }}
                    </div>
                  </div>
                  <div class="row">
                    <div class="col-6 text-right">
                      Total
                    </div>
                    <div class="col-6 q-pl-md" data-testid="computed-total">
                      {{ $nf(totalTableData.total) }}
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <div class="flex -my-2 items-center gap-x-8">
                  <div class="flex-grow min-w-[225px]">
                    <n-auto-complete-v2
                      v-model="fields.mode"
                      label="Mode"
                      class="col-12 col-md-6"
                      :error-message="errors?.mode ? errors.mode[0] : null"
                      :error="!!errors?.mode"
                      :options="modeOptionsComputed"
                      :endpoint="`v1/${route.params.company}/pos/create-defaults/bank_accounts`"
                      option-value="id"
                      option-label="name"
                      map-options
                      emit-value
                    >
                      <template #append>
                        <q-icon
                          v-if="fields.mode !== null"
                          class="cursor-pointer"
                          name="clear"
                          @click.stop.prevent="fields.mode = null"
                        />
                      </template>
                    </n-auto-complete-v2>
                  </div>
                  <div class="flex items-center gap-x-8 gap-y-4">
                    <q-btn class="f-open-btn" icon="mdi-menu">
                      <q-menu>
                        <div class="q-ma-lg config-options">
                          <div class="row -mt-4">
                            <div class="col-12">
                              <div class="row">
                                <div class="col-10">
                                  <q-input
                                    v-if="partyMode && fields.mode !== 'Credit'"
                                    v-model="fields.customer_name"
                                    label="Customer Name"
                                    :error-message="errors.customer_name
                                      ? errors.customer_name[0]
                                      : null
                                    "
                                    :error="!!errors?.customer_name"
                                  />
                                  <n-auto-complete-v2
                                    v-else
                                    v-model="fields.party"
                                    :options="partyChoices"
                                    label="Party"
                                    :endpoint="`v1/${route.params.company}/parties/choices/`"
                                    :error="errors?.party ? errors?.party[0] : null"
                                    :modal-component="checkPermissions('PartyCreate')
                                      ? PartyForm
                                      : null
                                    "
                                  />
                                </div>
                                <div class="col-2 row justify-center q-py-md">
                                  <q-btn flat size="md" @click="() => switchMode(fields)">
                                    <q-icon name="mdi-account-group" />
                                  </q-btn>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div class="row q-col-gutter-md">
                            <div class="col-12 row q-col-gutter-md">
                              <div
                                :class="fields.discount_type === 'Amount'
                                  || fields.discount_type === 'Percent'
                                  ? 'col-8'
                                  : 'col-12'
                                "
                              >
                                <n-auto-complete
                                  v-model="fields.discount_type"
                                  label="Discount*"
                                  :error="errors?.discount_type"
                                  :options="discountOptionsComputed"
                                  :modal-component="checkPermissions('SalesDiscountCreate')
                                    ? SalesDiscountForm
                                    : null
                                  "
                                />
                              </div>
                              <div
                                v-if="fields.discount_type === 'Amount'
                                  || fields.discount_type === 'Percent'
                                "
                                class="col-4"
                              >
                                <q-input
                                  v-model.number="fields.discount"
                                  label="Discount"
                                  :error-message="errors?.discount ? errors.discount[0] : null
                                  "
                                  :error="!!errors?.discount"
                                />
                              </div>
                            </div>
                          </div>
                          <div class="col-12 -mt-4">
                            <q-input
                              v-model="fields.remarks"
                              label="Remarks"
                              type="textarea"
                              autogrow
                              :error="!!errors?.remarks"
                              :error-message="errors?.remarks ? errors.remarks[0] : null
                              "
                            />
                          </div>
                        </div>
                      </q-menu>
                    </q-btn>
                    <div v-if="fields.rows.length > 0" class="flex items-center justify-end gap-4">
                      <q-btn color="orange-6" label="Save Draft" type="submit" @click.prevent="onSubmitClick('Draft')" />
                      <q-btn color="green-8" label="Issue" type="submit" @click.prevent="onSubmitClick('Issued')" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </q-card>
        <div class="h-[180px]"></div>
      </q-form>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.add-btn {
  // background-color: aqua;
  padding: 4px 8px;
  box-shadow: 0 0 3px rgb(109, 109, 109);
  border: 1px solid lightgray;
}

.add-btn:hover {
  background-color: lightgrey;
  cursor: pointer;
}

.config-options {
  min-width: min(450px, 90vw);
}

.q-field__control-container {
  background-color: black;
}
</style>
