<template>
  <q-form class="q-pa-lg" v-if="fields">
    <q-dialog v-model="htmlDialogOpen">
      <q-card style="size: a4; min-width: 60%; max-width: 90vw;">
        <q-card-section>
          <div v-html="selectedHtml"></div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Invoice Settings</span>
        </div>
      </q-card-section>

      <q-card-section>
        <div class="mb-4">
          <div class="text-h6 mb-2">Available Templates</div>
          <div class="flex flex-wrap gap-4">
            <div v-for="template in templateOptions" :key="template.id" class="q-mb-md"
              @click="openHtmlDialog(template.html)">
              <div>{{ template.label }}</div>
              <div class="relative w-[200px] h-[125px] cursor-pointer overflow-hidden">
                <div v-html="template.html" class="w-full h-full" style="zoom: 0.2"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="row q-ml-sm">
          <div class="col-12 col-sm-6">
            <q-select map-options emit-value v-model="fields.invoice_template" option-value="value" option-label="label"
              :options="templateOptions" label="Invoicing Template" />
          </div>
        </div>
        <div class="q-ma-md row q-pb-lg">
          <q-btn @click.prevent="() => onUpdateClick(fields)" color="green" label="Update" type="submit"
            :loading="formLoading" />
        </div>
      </q-card-section>
    </q-card>
  </q-form>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useLoginStore } from 'src/stores/login-info'
import useGeneratePdf from 'src/composables/pdf/useGeneratePdf'

useMeta({
  title: 'Invoice Settings | Awecount',
})

const $q = useQuasar()
const loginStore = useLoginStore()
const fields = ref({
  invoice_template: loginStore.companyInfo.invoice_template,
})
const formLoading = ref(false)

const data = {
  'party_name': 'Random Party Name',
  'party_contact_no': 'jkjrkgjjr84787847',
  'voucher_meta': {
    'sub_total': 500.0,
    'sub_total_after_row_discounts': 500.0,
    'discount': 0.0,
    'non_taxable': 500.0,
    'taxable': 0.0,
    'tax': 0.0,
    'grand_total': 500.0
  },
  'rows': [
    {
      'item_name': 'Demo 1',
      'unit_name': 'Kg',
      'tax_scheme': {
        'id': 3,
        'default': false,
        'friendly_name': 'exempt',
        'name': 'Exempt',
        'short_name': 'exempt',
        'description': 'exempt',
        'rate': 0.0,
        'recoverable': false,
        'receivable': null,
        'payable': 56
      },
      'hs_code': 100120,
      'selected_item_obj': {
        'id': 3090,
        'name': 'Demo 1',
        'unit_id': 387,
        'rate': null,
        'tax_scheme_id': 3,
        'code': 'Demo 1',
        'description': null,
        'is_trackable': true,
        'default_unit_obj': {
          'name': 'kg',
          'id': 387
        }
      },
      'selected_unit_obj': {
        'name': 'kg',
        'id': 387
      },
      'description': null,
      'quantity': 1,
      'rate': 500.0,
      'discount': 0.0,
      'discount_type': null,
      'trade_discount': false,
      'discount_amount': 0.0,
      'tax_amount': 0.0,
      'net_amount': 500.0
    }
  ],
  'tax_registration_number': null,
  'enable_row_description': true,
  'payment_receipts': [],
  'options': {
    'show_rate_quantity_in_voucher': true,
  },
  'fiscal_year': 'FY 81-82',
  'invoice_footer_text': 'test',
  'challan_numbers': [],
  'meta_sub_total': 500.0,
  'meta_sub_total_after_row_discounts': 500.0,
  'meta_discount': 0.0,
  'meta_non_taxable': 500.0,
  'meta_taxable': 0.0,
  'meta_tax': 0.0,
  'voucher_no': 133,
  'customer_name': null,
  'address': 'Bhaktapur',
  'email': null,
  'issue_datetime': '2024-12-05T09:57:38.085706+05:45',
  'date': '2024-12-05',
  'due_date': '2024-12-05',
  'payment_date': null,
  'status': 'Issued',
  'discount': 0.0,
  'discount_type': null,
  'trade_discount': true,
  'mode': 'Credit',
  'remarks': null,
  'is_export': false,
  'total_amount': 500.0,
  'print_count': 8,
  'party': 48,
  'payment_mode': null,
  'challans': [],
  'can_update_issued': true,
  'available_payment_modes': [
    {
      'name': 'paypal',
      'id': 13
    },
    {
      'name': 'aramex',
      'id': 16
    },
    {
      'name': 'cash',
      'id': 17
    }
  ],
}

const generateHtml = async (template) => {
  return useGeneratePdf('salesVoucher', false, data, false, loginStore.companyInfo, template)
}

const templateOptions = ref([
  { label: 'Template 1', value: 1, html: '' },
  { label: 'Template 2', value: 2, html: '' },
  { label: 'Template 3', value: 3, html: '' },
])

templateOptions.value.forEach(async (template) => template.html = await generateHtml(template.value))

const htmlDialogOpen = ref(false)
const selectedHtml = ref('')

const openHtmlDialog = (html) => {
  selectedHtml.value = html
  htmlDialogOpen.value = true
}

const onUpdateClick = async (fields) => {
  formLoading.value = true
  const endpoint = 'v1/invoice-setting-update/'
  useApi(endpoint, {
    method: 'PATCH',
    body: { invoice_template: fields.invoice_template },
  })
    .then(() => {
      $q.notify({
        color: 'green',
        message: 'Saved!',
        icon: 'check',
      })
      loginStore.companyInfo.invoice_template = fields.invoice_template
    })
    .catch(() => {
      $q.notify({
        color: 'red-6',
        message: 'Server Error Please Contact!',
        icon: 'report_problem',
        position: 'top-right',
      })
    }).finally(() => {
      formLoading.value = false
    })
}
</script>
