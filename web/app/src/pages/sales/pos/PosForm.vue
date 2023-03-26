<template>
  <q-form class="q-pa-md row-con">
    <div>
      <q-card>
        <q-card-section>
          <div>
            <q-input
              v-model="searchTerm"
              debounce="300"
              label="Search Items..."
            ></q-input>
            <q-markup-table flat bordered>
              <thead>
                <q-tr class="text-left">
                  <q-th> Name </q-th>
                  <q-th> Rate </q-th>
                </q-tr>
              </thead>
              <tbody class="text-left">
                <q-tr
                  v-for="item in searchResults ||
                  formDefaults.collections?.items.results"
                  :key="item.id"
                >
                  <q-td>
                    {{ item.name }}
                  </q-td>
                  <q-td>
                    <span class="row items-center q-gutter-x-sm">
                      <span class="col-5">{{ item.rate }}</span>
                      <span class="col-5"
                        ><q-btn @click="onAddItem(item)" size="sm q-px-xs"
                          >+</q-btn
                        ></span
                      >
                    </span>
                  </q-td>
                </q-tr>
              </tbody>
            </q-markup-table>
          </div>
        </q-card-section>
      </q-card>
    </div>
    <q-card>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <div class="row">
                <div class="col-10">
                  <q-input
                    v-model="fields.customer_name"
                    label="Customer Name"
                    :error-message="errors.customer_name"
                    :error="!!errors.customer_name"
                    v-if="partyMode && fields.mode !== 'Credit'"
                  >
                  </q-input>
                  <n-auto-complete
                    v-else
                    v-model="fields.party"
                    :options="partyChoices"
                    label="Party"
                    :error="errors?.party ? errors?.party : null"
                    :modal-component="PartyForm"
                  />
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
              <div
                :class="
                  fields.discount_type === 'Amount' ||
                  fields.discount_type === 'Percent'
                    ? 'col-8'
                    : 'col-12'
                "
              >
                <n-auto-complete
                  v-model="fields.discount_type"
                  label="Discount*"
                  :error="errors.discount_type"
                  :options="
                    formDefaults.collections
                      ? staticOptions.discount_types.concat(
                          formDefaults?.collections.discounts
                        )
                      : staticOptions.discount_types
                  "
                  :modal-component="SalesDiscountForm"
                >
                </n-auto-complete>
              </div>
              <div
                class="col-4"
                v-if="
                  fields.discount_type === 'Amount' ||
                  fields.discount_type === 'Percent'
                "
              >
                <q-input
                  v-model.number="fields.discount"
                  label="Discount"
                  :error-message="errors.discount"
                  :error="!!errors.discount"
                ></q-input>
              </div>
            </div>
            <q-select
              v-model="fields.mode"
              label="Mode"
              class="col-12 col-md-6"
              :error-message="errors.mode"
              :error="!!errors.mode"
              :options="
                staticOptions.modes.concat(
                  formDefaults.collections?.bank_accounts
                )
              "
              option-value="id"
              option-label="name"
              map-options
              emit-value
            >
              <template v-slot:append>
                <q-icon
                  v-if="fields.mode !== null"
                  class="cursor-pointer"
                  name="clear"
                  @click.stop.prevent="fields.mode = null" /></template
            ></q-select>
          </div>
          <div class="row"></div>
        </q-card-section>
      </q-card>
      <invoice-table
        :itemOptions="
          formDefaults.collections
            ? formDefaults.collections.items.results
            : null
        "
        :unitOptions="
          formDefaults.collections ? formDefaults.collections.units : null
        "
        :discountOptions="
          formDefaults.collections
            ? staticOptions.discount_types.concat(
                formDefaults?.collections.discounts
              )
            : staticOptions.discount_types
        "
        :taxOptions="formDefaults.collections?.tax_schemes"
        v-model="fields.rows"
        :mainDiscount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }"
        :usedInPos="true"
        :errors="!!errors.rows ? errors.rows : null"
        @deleteRowErr="
          (index, deleteObj) => deleteRowErr(index, errors, deleteObj)
        "
      ></invoice-table>
      <div class="row q-px-lg">
        <div class="col-12">
          <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
            autogrow
            :error="!!errors?.remarks"
            :error-message="errors?.remarks"
          />
        </div>
      </div>

      <div
        class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md"
        v-if="fields.rows.length > 0"
      >
        <q-btn
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
          color="orange-6"
          label="Save Draft"
        />
        <q-btn
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)"
          color="green-8"
          :label="isEdit ? 'Update' : 'Issue'"
        />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import InvoiceTable from 'src/components/voucher/InvoiceTable.vue'
import { discount_types, modes } from 'src/helpers/constants/invoice'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = 'v1/pos/'
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const searchTerm = ref(null)
    const searchResults = ref(null)
    const staticOptions = {
      discount_types: discount_types,
      modes: modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/pos',
    })
    const partyChoices = ref(false)
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
        if (!formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows = []
        }
        formData.fields.value.deleted_rows.push(deleteObj)
      }
      if (!!errors.rows) errors.rows.splice(index, 1)
    }
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    formData.fields.value.date = formData.today
    formData.fields.value.is_export = false
    formData.fields.value.mode = 'Credit'
    formData.fields.value.party = ''
    formData.fields.value.rows = []
    // handle Search
    const fetchResults = () => {
      if (searchTerm.value) {
        useApi(`/v1/items/pos/?search=${searchTerm.value}`)
          .then((data) => (searchResults.value = data.results))
          .catch(() => console.log('Error Fetching Search Results'))
      } else searchResults.value = null
    }
    watch(searchTerm, () => fetchResults())
    // handle Search
    const onAddItem = (itemInfo) => {
      console.log(itemInfo)
      formData.fields.value.rows.push({
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
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      SalesDiscountForm,
      openDatePicker,
      staticOptions,
      InvoiceTable,
      partyMode,
      switchMode,
      deleteRowErr,
      onSubmitClick,
      searchTerm,
      searchResults,
      onAddItem,
      partyChoices,
    }
  },
  created() {
    useApi('/v1/parties/choices/')
      .then((res) => {
        this.partyChoices = res
      })
      .catch((err) => {
        console.log('error fetching choices due to', err)
      })
  },
}
</script>

<style lang="scss" scoped>
.row-con {
  display: grid;
  grid-template-columns: 4fr 6fr;
  grid-gap: 1rem;
}
</style>
