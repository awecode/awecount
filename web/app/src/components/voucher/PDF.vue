<script setup lang="ts">
import DateConverter from 'src/components/date/VikramSamvat.js'
import numberToText from 'src/composables/numToText'
import { useLoginStore } from 'src/stores/login-info'
import { computed } from 'vue'

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
  party?: boolean
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
  organization_type?: string
  logo_url?: string
  website?: string
  invoice_template?: number
  config_template?: string
}

const props = defineProps<{
  voucherType: 'salesVoucher' | 'creditNote' | 'debitNote'
  onlyBody?: boolean
  invoiceInfo: InvoiceInfo
  hideRowQuantity?: boolean
  companyInfo?: Partial<CompanyInfo>
  template?: number
}>()

const loginStore = useLoginStore()
const companyInfo = computed(() => ({
  ...loginStore.companyInfo,
  ...props.companyInfo,
}))
const invoiceTemplate = computed(() => props.template || companyInfo.value.invoice_template || 1)

// Tax calculation logic
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

const formatRowDescription = (str?: string) => {
  if (!str) return ''
  const dataArray = str.split('\n')
  return dataArray.map(data => `<div>${data}</div>`).join(' ')
}

const formatNumberWithComma = (num: number) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatNumber = (num: number) => {
  return formatNumberWithComma(Number(num).toFixed(2))
}
</script>

<template>
  <div>
    <template v-if="!onlyBody">
      <div v-if="[2, 3].includes(invoiceTemplate)">
        <div style="position: relative; margin-bottom: 10px;">
          <img
            alt="Company Logo"
            style="height: 110px; object-fit: contain; max-width: 160px; position: absolute;"
            :src="companyInfo.logo_url"
            :style="{ display: companyInfo.logo_url ? 'block' : 'none', left: invoiceTemplate === 3 ? '40px' : '0' }"
          />
          <div style="text-align: center; padding-left: 10px;">
            <h1 style="line-height: normal; margin: 5px 0; font-size: 35px; font-weight: 700;">
              {{ companyInfo.name }}
              {{ companyInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.' : ['public_limited', 'corporation'].includes(companyInfo.organization_type) ? 'Ltd.' : '' }}
            </h1>
            <div>{{ companyInfo.address }}</div>
            <div style="font-size: 14px;">
              <div style="display: flex; justify-content: center; flex-direction: column;">
                <div style="display: flex; align-items: center; justify-content: center;">
                  <span>Email: {{ companyInfo.emails?.join(', ') || '' }}</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: center;">
                  <span>Tel: {{ companyInfo.contact_no }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div style="display: flex; justify-content: end; font-family: Arial, Helvetica, sans-serif;">
          <div style="display: flex; flex-direction: column; gap: 3px; align-items: flex-end;">
            <div style="font-size: 14px;">
              VAT No. <strong>{{ companyInfo.tax_identification_number }}</strong>
            </div>
            <div v-if="companyInfo.website" style="display: flex; align-items: center;">
              <img alt="Website" src="/icons/web-fill.svg" style="margin-right: 10px; width: 14px;" />
              <span style="color: skyblue;">{{ companyInfo.website }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif;">
        <div>
          <h1 style="margin: 5px 0; font-size: 35px; font-weight: 700;">
            {{ companyInfo.name }}
            {{ companyInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.' : ['public_limited', 'corporation'].includes(companyInfo.organization_type) ? 'Ltd.' : '' }}
          </h1>
          <div>{{ companyInfo.address }}</div>
          <div>Tax Reg. No. <strong>{{ companyInfo.tax_identification_number }}</strong></div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 5px; align-items: flex-end;">
          <div style="margin-bottom: 5px;">
            <img
              alt="Company Logo"
              style="height: 70px; max-width: 200px; object-fit: contain;"
              :src="companyInfo.logo_url"
              :style="{ display: companyInfo.logo_url ? 'block' : 'none' }"
            />
          </div>
          <div style="display: flex; align-items: center;">
            <img alt="Email" src="/icons/telephone-fill.svg" style="margin-right: 10px; width: 14px;" />
            <span style="color: skyblue;">{{ companyInfo.contact_no }}</span>
          </div>
          <div style="display: flex; align-items: center;">
            <img alt="Call" src="/icons/envelope-fill.svg" style="margin-right: 10px; width: 14px;" />
            <span style="color: skyblue;">{{ companyInfo.emails?.join(', ') || '' }}</span>
          </div>
        </div>
      </div>
      <hr style="margin: 20px 0;" />
    </template>

    <div
      :style="{
        'margin-top': onlyBody && voucherType === 'salesVoucher' ? '80px' : onlyBody ? '80px' : '20px',
        'margin-bottom': voucherType === 'salesVoucher' ? '20px' : '0',
        'font-family': 'Arial, Helvetica, sans-serif',
      }"
    >
      <template v-if="voucherType === 'salesVoucher'">
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
        <div style="display: flex; justify-content: space-between;">
          <div style="display: flex; flex-direction: column; gap: 2px;">
            <div style="font-weight: 600; color: grey;">
              Billed To:
            </div>
            <div>{{ invoiceInfo.party ? invoiceInfo.customer_name || invoiceInfo.party_name : invoiceInfo.customer_name || '' }}</div>
            <div v-if="invoiceInfo.address">
              {{ invoiceInfo.address }}
            </div>
            <div v-if="[2, 3].includes(invoiceTemplate) && invoiceInfo.party_contact_no">
              {{ invoiceInfo.party_contact_no }}
            </div>
            <div v-if="invoiceInfo.tax_identification_number" style="font-weight: 600; color: grey;">
              Tax reg. No. {{ invoiceInfo.tax_identification_number }}
            </div>
          </div>
          <div style="display: flex; flex-direction: column; gap: 2px; text-align: right;">
            <div v-if="invoiceInfo.voucher_no">
              <span style="font-weight: 600; color: grey;">INV No.: </span>
              {{ invoiceInfo.fiscal_year }}-<span style="font-weight: bold;">{{ invoiceInfo.voucher_no }}</span>
            </div>
            <div v-if="invoiceInfo.reference">
              <span style="font-weight: 600; color: grey;">Reference: </span> {{ invoiceInfo.reference }}
            </div>
            <div>
              <span style="font-weight: 600; color: grey;">Date: </span> {{ invoiceInfo.date }}
            </div>
            <div>
              <span style="font-weight: 600; color: grey;">Miti: </span> {{ DateConverter.getRepresentation(invoiceInfo.date, 'bs') }}
            </div>
            <div>
              <span style="font-weight: 600; color: grey;">Mode: </span>
              {{ invoiceInfo.mode }} {{ invoiceInfo.status === 'Draft' ? '(Draft)' : invoiceInfo.status === 'Paid' ? '(Paid)' : '' }}
            </div>
          </div>
        </div>
      </template>
      <template v-else>
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
      </template>

      <div>
        <table style="width: 100%; font-family: Arial, Helvetica, sans-serif; border: 2px solid #b9b9b9;">
          <tr style="color: grey; font-weight: 500;">
            <th style="width: 40px; padding: 5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">
              SN
            </th>
            <th style="white-space: nowrap; padding: 5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">
              H.S. Code
            </th>
            <th style="width: 40%; text-align: left; padding-left: 20px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">
              Particular
            </th>
            <th style="text-align: left; padding: 5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">
              Qty
            </th>
            <th style="text-align: left; padding: 5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">
              Rate
            </th>
            <th v-if="invoiceTemplate === 4" style="text-align: left; padding: 5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">
              Tax
            </th>
            <th style="text-align: right; padding: 5px; border-bottom: #b9b9b9 solid 2px;">
              Amount({{ companyInfo.config_template === 'np' ? 'NRS' : 'N/A' }})
            </th>
          </tr>
          <tr v-for="(row, index) in invoiceInfo.rows" :key="index" style="color: grey; font-weight: 400;">
            <th style="width: 20px; padding: 10px 0; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;">
              {{ index + 1 }}
            </th>
            <th style="width: 20px; padding: 10px 0; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;">
              {{ row.hs_code ?? '' }}
            </th>
            <th style="width: 50%; font-weight: 400; text-align: left; padding-left: 20px; border-right: #b9b9b9 solid 2px;">
              {{ row.item_name }}
              <br />
              <div
                class="text-grey-8"
                style="font-size: 12px; padding: 5px;"
                :style="{ display: row.description ? 'block' : 'none' }"
                v-html="formatRowDescription(row.description)"
              ></div>
            </th>
            <th style="text-align: left; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;">
              <span :style="{ display: hideRowQuantity ? 'none' : 'inline' }">
                {{ row.quantity }}<span style="font-size: 13px; color: gray; margin-left: 2px;">{{ row.unit_name }}</span>
              </span>
            </th>
            <th style="text-align: left; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;">
              <span :style="{ display: hideRowQuantity ? 'none' : 'inline' }">{{ formatNumber(row.rate) }}</span>
            </th>
            <th v-if="invoiceTemplate === 4" style="width: 20%; text-align: left; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;">
              {{ row.tax_scheme ? row.tax_scheme.name : '' }}
            </th>
            <th style="text-align: right; font-weight: 400; padding: 5px;">
              {{ formatNumberWithComma(row.quantity * row.rate) }}
            </th>
          </tr>
          <tr v-if="[2, 3].includes(invoiceTemplate)" style="color: grey; font-weight: 400;">
            <th
              style="width: 20px; padding: 10px 0; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;"
              :style="{ height: `${80 * (5 - invoiceInfo.rows.length)}px` }"
            ></th>
            <th style="padding: 10px 0; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;"></th>
            <th style="width: 50%; font-weight: 400; text-align: left; padding-left: 20px; border-right: #b9b9b9 solid 2px;"></th>
            <th style="text-align: left; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;"></th>
            <th style="text-align: left; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;"></th>
            <th style="text-align: right; font-weight: 400; padding: 5px;"></th>
          </tr>
        </table>
        <div style="display: flex; justify-content: space-between; align-items: center; font-family: Arial, Helvetica, sans-serif; border: 2px solid #b9b9b9; border-top: none; padding: 20px; padding-top: 0;">
          <div>
            <template v-if="voucherType === 'salesVoucher'">
              <div style="font-weight: 600; margin-bottom: 10px;">
                In words:
              </div>
              <div>{{ numberToText(invoiceInfo.voucher_meta.grand_total) }}</div>
            </template>
          </div>
          <div style="width: 250px; padding: 10px 0; padding-left: 10px; border-left: 2px solid #b9b9b9; margin-top: 15px;">
            <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 2px solid #b9b9b9;">
              <span style="font-weight: 600; color: lightgray;">SUB TOTAL</span>
              <span>{{ formatNumberWithComma(invoiceInfo.voucher_meta.sub_total) }}</span>
            </div>
            <div
              style="margin: 5px 0; border-bottom: 2px solid #b9b9b9;"
              :style="{ display: invoiceInfo.voucher_meta.discount ? 'flex' : 'none' }"
            >
              <span style="font-weight: 600; color: lightgray;">DISCOUNT</span>
              <span>{{ formatNumberWithComma(invoiceInfo.voucher_meta.discount) }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 2px solid #b9b9b9;">
              <span style="font-weight: 600; color: lightgray;">
                {{ sameTax && invoiceInfo.rows[taxIndex]?.tax_scheme ? ([2, 3].includes(invoiceTemplate) ? `${invoiceInfo.rows[taxIndex].tax_scheme.rate} % ${invoiceInfo.rows[taxIndex].tax_scheme.name}` : `${invoiceInfo.rows[taxIndex].tax_scheme.name} ${invoiceInfo.rows[taxIndex].tax_scheme.rate} %`) : 'TAX' }}
              </span>
              <span>{{ formatNumberWithComma(invoiceInfo.voucher_meta.tax) }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;">
              <span style="font-weight: 600; color: gray;">GRAND TOTAL</span>
              <span>{{ formatNumberWithComma(invoiceInfo.voucher_meta.grand_total) }}</span>
            </div>
          </div>
        </div>
        <template v-if="voucherType === 'creditNote' || voucherType === 'debitNote'">
          <div style="font-weight: 600; margin-bottom: 10px; font-family: Arial, Helvetica, sans-serif;">
            In words: {{ numberToText(invoiceInfo.total_amount) }}
          </div>
          <div style="margin: 20px 0;">
            <span style="font-weight: 600;">Remarks:</span> {{ invoiceInfo.remarks }}
          </div>
        </template>
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
