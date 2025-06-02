<script setup lang="ts">
import HeaderOne from 'src/components/voucher/pdf/PDFHeaderOne.vue'
import HeaderTwo from 'src/components/voucher/pdf/PDFHeaderTwo.vue'
import InvoiceMetadata from 'src/components/voucher/pdf/PDFInvoiceMetadata.vue'
import InvoiceTable from 'src/components/voucher/pdf/PDFInvoiceTable.vue'
import { useLoginStore } from 'src/stores/login-info'
import { computed, defineProps } from 'vue'

interface Row {
  hs_code?: string
  item_name: string
  description?: string
  quantity: number
  unit_name: string
  rate: number
  tax_scheme?: { id: number, name: string, rate: number }
}

interface VoucherMeta {
  sub_total: number
  discount?: number
  tax: number
  grand_total: number
}

interface InvoiceInfo {
  rows: Row[]
  voucher_meta: VoucherMeta
  date: string
  status?: string
  voucher_no?: string
  fiscal_year?: string
  customer_name?: string
  party_name?: string
  party: boolean
  address?: string
  party_contact_no?: string
  tax_identification_number?: string
  reference?: string
  mode?: string
  print_count: number
  invoice_footer_text?: string
  total_amount?: number
  remarks?: string
  invoice_data?: { voucher_no: string }[]
}

interface CompanyInfo {
  name: string
  address: string
  contact_no: string
  emails?: string[]
  tax_identification_number: string
  organization_type: string
  logo_url?: string
  website?: string
  invoice_template?: number
  config_template: string
  invoice_footer_text?: string
}

const props = defineProps<{
  voucherType: 'salesVoucher' | 'creditNote' | 'debitNote'
  onlyBody?: boolean
  invoiceInfo: InvoiceInfo
  hideRowQuantity?: boolean
  companyInfo?: CompanyInfo
  template?: number
}>()

const loginStore = useLoginStore()
const companyInfo = computed(() => ({
  ...loginStore.companyInfo,
  ...props.companyInfo,
}))
const invoiceTemplate = computed(() => props.template || companyInfo.value.invoice_template || 1)

// Tax calculation logic
// @ts-expect-error fix this later
const { sameTax, taxIndex } = computed(() => {
  let isTaxSame: number | boolean | null = null
  let taxIndex: number | null = null
  props.invoiceInfo.rows.forEach((row, index) => {
    if (isTaxSame !== false && row.tax_scheme && row.tax_scheme.rate !== 0) {
      if (isTaxSame === null) {
        isTaxSame = row.tax_scheme.id
        taxIndex = index
      } else if (isTaxSame !== row.tax_scheme.id) {
        isTaxSame = false
      }
    }
  })
  return { sameTax: isTaxSame, taxIndex }
})
</script>

<template>
  <div>
    <template v-if="!onlyBody">
      <HeaderTwo
        v-if="[2, 3].includes(invoiceTemplate)"
        :company-info="companyInfo"
        :logo-style="
          invoiceTemplate === 3 ? {
            left: '40px',
          } : undefined"
      />
      <HeaderOne v-else :company-info="companyInfo" />
      <hr style="margin: 20px 0;" />
    </template>

    <div
      :style="{
        'margin-top': onlyBody && voucherType === 'salesVoucher' ? '80px' : onlyBody ? '80px' : '20px',
        'margin-bottom': voucherType === 'salesVoucher' ? '20px' : '0',
        'font-family': 'Arial, Helvetica, sans-serif',
      }"
    >
      <div
        v-if="voucherType === 'salesVoucher'"
        :style="onlyBody ? 'margin-top: 80px; margin-bottom: 20px' : 'margin-top: 20px; margin-bottom: 20px'"
      >
        <div style="display: flex; align-items: center; gap: 11px; flex-direction: column;">
          <h4 style="margin: 0; font-size: 1.4rem;">
            {{ invoiceInfo.status === 'Issued' || invoiceInfo.status === 'Paid' || invoiceInfo.status === 'Partially Paid' ? 'TAX INVOICE' : invoiceInfo.status === 'Draft' ? 'PRO FORMA INVOICE' : invoiceInfo.status === 'Cancelled' ? 'TAX INVOICE (CANCELLED)' : '' }}
          </h4>
        </div>
        <div
          style="text-align: center;"
          :style="{ display: invoiceInfo.print_count > 1 && ['Issued', 'Paid', 'Partially Paid'].includes(invoiceInfo.status) ? 'block' : 'none' }"
        >
          COPY {{ invoiceInfo.print_count - 1 }} OF ORIGINAL (PRINT COUNT: {{ invoiceInfo.print_count }})
        </div>
        <InvoiceMetadata
          :company-info="companyInfo"
          :invoice-info="invoiceInfo"
          :show-party-contact-no="[2, 3].includes(invoiceTemplate)"
        />
      </div>
      <div
        v-else
        :style="`font-family: Arial, Helvetica, sans-serif; ${onlyBody ? 'margin-top: 80px;' : ''}`"
      >
        <div style="display: flex; align-items: center; gap: 11px; flex-direction: column; margin-bottom: 15px;">
          <h4 style="margin: 0; font-size: 1.4rem;">
            {{ voucherType === 'creditNote' ? 'Credit Note' : 'Debit Note' }}
          </h4>
          <span
            style="text-align: center; font-size: 1rem;"
            :style="{ display: invoiceInfo.print_count > 1 && ['Issued', 'Paid', 'Partially Paid'].includes(invoiceInfo.status) ? 'block' : 'none' }"
          >
            COPY {{ invoiceInfo.print_count - 1 }} OF ORIGINAL (PRINT COUNT: {{ invoiceInfo.print_count }})
          </span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <div style="display: flex; flex-direction: column; gap: 5px;">
            <div>
              <span style="font-weight: 600; color: dimgray;">{{ voucherType === 'creditNote' ? 'Credit Note No:' : 'Debit Note No:' }}</span>
              {{ invoiceInfo.voucher_no || '-' }}
            </div>
            <div v-if="invoiceInfo.party_name">
              <span style="font-weight: 600; color: dimgray;">Party:</span> {{ invoiceInfo.party_name }}
            </div>
            <div v-if="invoiceInfo.customer_name">
              <span style="font-weight: 600; color: dimgray;">Customer:</span> {{ invoiceInfo.customer_name }}
            </div>
            <div v-if="invoiceInfo.address">
              <span style="font-weight: 600; color: dimgray;">Address:</span> {{ invoiceInfo.address }}
            </div>
            <div v-if="invoiceInfo.tax_identification_number">
              <span style="font-weight: 600; color: dimgray;">Tax Reg.:</span> {{ invoiceInfo.tax_identification_number || '-' }}
            </div>
            <div style="font-weight: 600;">
              Ref. Invoice No.: # {{ invoiceInfo?.invoice_data?.length > 0 ? invoiceInfo.invoice_data[0]?.voucher_no : '-' }}
            </div>
          </div>
          <div>
            <div><span style="font-weight: 600; color: dimgray;">Date:</span> {{ invoiceInfo.date }}</div>
          </div>
        </div>
        <hr style="border: 0.5px solid #b9b9b9; height: 0; margin: 20px 0;" />
      </div>

      <InvoiceTable
        :company-info="companyInfo"
        :empty-rows="[2, 3].includes(invoiceTemplate)"
        :hide-row-quantity="props.hideRowQuantity"
        :invoice-info="invoiceInfo"
        :same-tax="sameTax"
        :show-tax-column="invoiceTemplate === 4"
        :show-tax-rate-before-name="[2, 3].includes(invoiceTemplate)"
        :tax-index="taxIndex"
        :voucher-type="props.voucherType"
      />

      <div v-if="invoiceInfo.received_by" style="margin-top: 20px;  white-space:pre; font-size: 14px;">
        <span style="font-weight: 600;">Received By:</span>
        <br />
        <span>{{ invoiceInfo.received_by }}</span>
      </div>

      <div style="margin-top: 20px;"></div>

      <div style="font-size: 14px; text-align: right;">
        <div
          v-if="voucherType === 'salesVoucher' && invoiceInfo.invoice_footer_text"
          style="margin-bottom: 20px; text-align: left;"
          v-html="invoiceInfo.invoice_footer_text"
        ></div>
        <div style="margin-bottom: 5px;">
          Generated by {{ loginStore.username || 'system' }} for {{ companyInfo.name }}
          {{ companyInfo.organization_type === 'private_limited' ? 'Private Limited' : '' }}.
        </div>
        <div v-if="!onlyBody">
          This is a computer generated invoice, produced using awecount.com - IRD Approval No. 7600405
        </div>
      </div>
    </div>
  </div>
</template>
