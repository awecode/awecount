<template>
  <div class="q-pa-md row-con">
    <div>
      <q-card>
        <q-card-section>
          <div>
            <q-input v-model="searchTerm" autofocus debounce="500" label="Search Items..."
              @keypress.enter="enterClicked = true"></q-input>
            <div class="row q-py-sm q-px-md text-subtitle2 q-mt-md">
              <div class="col-7">Name</div>
              <div class="col-5">Rate</div>
            </div>
            <div class="row" style="border-bottom: 1px lightgrey solid; padding: 8px 16px 6px 16px; font-size: 13px;"
              v-for="item in (searchResults?.results ||
                formDefaults.collections?.items.results)" :key="item.id">
              <div class="col-7">
                <router-link v-if="hasItemModifyAccess" style="font-weight: 500; text-decoration: none" class="text-blue"
                  :to="`/items/${item.id}/`">
                  {{ item.name }}
                </router-link>
                <span v-else>{{ item.name }}</span>
              </div>
              <div class="col-5">
                <span class="row items-center q-gutter-x-sm">
                  <span class="col-5">{{ item.rate }}</span>
                  <span class="col-5">
                    <q-icon name="add" class="add-btn" @click="onAddItem(item)" tabindex="0"></q-icon>
                  </span>
                </span>
              </div>
            </div>
          </div>
          <PaginateList class="q-mt-md" @update-page="(page) => currentPage = page"
            v-if="formDefaults.collections?.items.pagination"
            :pagination="searchResults?.pagination || formDefaults.collections?.items.pagination"></PaginateList>
        </q-card-section>
      </q-card>
    </div>
    <div>
      <q-form>
        <q-card>
          <q-card class="q-mx-lg q-pt-md">
            <q-card-section>
              <div class="row q-col-gutter-md">
                <div class="col-12">
                  <div class="row">
                    <div class="col-10">
                      <q-input v-model="fields.customer_name" label="Customer Name" :error-message="errors.customer_name ? errors.customer_name[0] : null
                        " :error="!!errors?.customer_name" v-if="partyMode && fields.mode !== 'Credit'">
                      </q-input>
                      <n-auto-complete v-else v-model="fields.party" :options="partyChoices" label="Party"
                        :error="errors?.party ? errors?.party[0] : null"
                        :modal-component="checkPermissions('PartyCreate') ? PartyForm : null" />
                    </div>
                    <div class="col-2 row justify-center q-py-md">
                      <q-btn flat size="md" @click="() => switchMode(fields)">
                        <q-icon name="mdi-account-group"></q-icon>
                      </q-btn>
                    </div>
                  </div>
                </div>
              </div>
              <div class="row q-col-gutter-md">
                <div class="col-md-6 col-12 row q-col-gutter-md">
                  <div :class="fields.discount_type === 'Amount' ||
                    fields.discount_type === 'Percent'
                    ? 'col-8'
                    : 'col-12'
                    ">
                    <n-auto-complete v-model="fields.discount_type" label="Discount*" :error="errors?.discount_type"
                      :options="discountOptionsComputed"
                      :modal-component="checkPermissions('SalesDiscountCreate') ? SalesDiscountForm : null">
                    </n-auto-complete>
                  </div>
                  <div class="col-4" v-if="fields.discount_type === 'Amount' ||
                    fields.discount_type === 'Percent'
                    ">
                    <q-input v-model.number="fields.discount" label="Discount"
                      :error-message="errors?.discount ? errors.discount[0] : null" :error="!!errors?.discount"></q-input>
                  </div>
                </div>
                <q-select v-model="fields.mode" label="Mode" class="col-12 col-md-6"
                  :error-message="errors?.mode ? errors.mode[0] : null" :error="!!errors?.mode" :options="['Cash'].concat(
                    formDefaults.collections?.bank_accounts
                  )
                    " option-value="id" option-label="name" map-options emit-value>
                  <template v-slot:append>
                    <q-icon v-if="fields.mode !== null" class="cursor-pointer" name="clear"
                      @click.stop.prevent="fields.mode = null" /></template></q-select>
              </div>
              <div class="row"></div>
            </q-card-section>
          </q-card>
          <invoice-table :itemOptions="formDefaults.collections
            ? formDefaults.collections.items.results
            : null
            " :unitOptions="formDefaults.collections ? formDefaults.collections.units : null
    " :discountOptions="discountOptionsComputed" :taxOptions="formDefaults.collections?.tax_schemes"
            v-model="fields.rows" :mainDiscount="{
              discount_type: fields.discount_type,
              discount: fields.discount,
            }" :usedInPos="true" :errors="!!errors?.rows ? errors.rows : null" @deleteRowErr="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)
  "></invoice-table>
          <div class="row q-px-lg">
            <div class="col-12">
              <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow :error="!!errors?.remarks"
                :error-message="errors?.remarks ? errors.remarks[0] : null" />
            </div>
          </div>

          <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md" v-if="fields.rows.length > 0">
            <q-btn @click.prevent="onSubmitClick('Draft')" color="orange-6" label="Save Draft" type="submit" />
            <q-btn @click.prevent="onSubmitClick('Issued')" color="green-8" :label="isEdit ? 'Update' : 'Issue'"
              type="submit" />
          </div>
        </q-card>
      </q-form>
    </div>
  </div>
</template>

<script setup>
import useForm from '/src/composables/useForm'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import useGeneratePosPdf from 'src/composables/pdf/useGeneratePosPdf'
import checkPermissions from 'src/composables/checkPermissions'
import { useLoginStore } from '/src/stores/login-info.js'
const emit = defineEmits([])
const metaData = {
  title: 'POS | Awecount',
}
useMeta(metaData)
const store = useLoginStore()
const endpoint = 'v1/pos/'
const $q = useQuasar()
const searchTerm = ref(null)
const searchResults = ref(null)
const enterClicked = ref(false)
const currentPage = ref(null)
const staticOptions = {
  discount_types: discount_types,
  modes: modes,
}
const { fields, errors, formDefaults, today } = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/pos',
})
const partyChoices = ref([])
useApi('/v1/parties/choices/').then((choices) => {
  partyChoices.value = choices
})
const partyMode = ref(false)
const switchMode = (fields) => {
  if (fields.mode !== 'Credit') {
    partyMode.value = !partyMode.value
  } else
    $q.notify({
      color: 'orange-4',
      message: 'Credit customer must be a party!',
    })
}
const deleteRowErr = (index, errors, deleteObj) => {
  if (deleteObj) {
    if (!fields.value.deleted_rows) {
      fields.value.deleted_rows = []
    }
    fields.value.deleted_rows.push(deleteObj)
  }
  if (!!errors.rows) errors.rows.splice(index, 1)
}
const onSubmitClick = (status) => {
  fields.value.status = status
  if (!partyMode.value) fields.value.customer_name = null
  useApi('/v1/pos/', { method: 'POST', body: fields.value })
    .then((data) => {
      errors.value = {}
      $q.notify({
        color: 'green',
        message: data.status === 'Draft' ? 'Saved As Draft!' : 'Issued!',
        icon: 'check',
      })
      const printData = useGeneratePosPdf(data, getTaxObj(), gePartyObj(), !formDefaults.value.options.show_rate_quantity_in_voucher, fields.value.rows)
      console.log('printData', printData)
      printPdf(printData)
      setTimeout(() => window.history.go(0), 100)
      fields.value.rows = []
    })
    .catch((err) => {
      fields.value.status = null
      if (err.status === 400) {
        errors.value = err.data
        $q.notify({
          color: 'negative',
          message: 'Please fill out the form correctly.',
          icon: 'report_problem',
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
  useApi(`/v1/items/pos/?${searchTerm.value ? `search=${searchTerm.value}` : ''}${`&page=${currentPage.value || 1}`}`)
    .then((data) => {
      (searchResults.value = data)
      if (enterClicked.value) {
        let obj = data.results.find((item) => {
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
      console.log('Error Fetching Search Results')
      enterClicked.value = false
    })
}
watch([searchTerm, currentPage], (newVal, oldVal) => {
  if (newVal[0] !== oldVal[0]) {
    {
      currentPage.value = 1
      fetchResults()
    }
  }
  else { fetchResults() }
}, { deep: true })
watch(() => fields.value.rows, (newVal) => {
  if (formDefaults.value.options.persist_pos_items) {
    store.posData = newVal
  }
}, {
  deep: true
})
// handle Search
const onAddItem = (itemInfo) => {
  const index = fields.value.rows.findIndex(
    (item) => item.item_id === itemInfo.id
  )
  if (index >= 0) {
    fields.value.rows[index].quantity++
  } else {
    fields.value.rows.push({
      quantity: 1,
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
}
const getTaxObj = () => {
  if (fields.value.rows[0].tax_scheme_id) {
    const index =
      formDefaults.value.collections.tax_schemes.findIndex(
        (item) => item.id === fields.value.rows[0].tax_scheme_id
      )

    return formDefaults.value.collections.tax_schemes[index]
  } else return null
}
const gePartyObj = () => {
  // if (formData.fields.value.party && !partyMode) {
  if (fields.value.party && !partyMode.value) {
    const index = partyChoices.value.findIndex((item) => item.id === fields.value.party)
    return partyChoices.value[index]
  } else return null
}
const printPdf = (data) => {
  let ifram = document.createElement('iframe')
  ifram.style = 'display:none; margin: 20px'
  document.body.appendChild(ifram)
  const pri = ifram.contentWindow
  pri.document.open()
  pri.document.write(data)
  pri.document.close()
  pri.focus()
  setTimeout(() => pri.print(), 100)
}
const hasItemModifyAccess = computed(() => {
  return checkPermissions('ItemModify')
})
watch(() => formDefaults.value, () => {
  if (formDefaults.value.options.persist_pos_items) {
    fields.value.rows = store.posData || []
  }
})
const discountOptionsComputed = computed(() => {
  if (formDefaults?.value?.collections?.discounts) {
    return staticOptions.discount_types.concat(
      formDefaults.value.collections.discounts
    )
  } else return staticOptions.discount_types
})
</script>

<style lang="scss" scoped>
.row-con {
  display: grid;
  grid-template-columns: 4fr 6fr;
  grid-gap: 1rem;
}

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
</style>
