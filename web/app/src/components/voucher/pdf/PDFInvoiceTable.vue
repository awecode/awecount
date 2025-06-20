<script setup lang="ts">
import numberToText from 'src/composables/numToText'
import { formatNumber, formatNumberWithComma, formatRowDescription } from 'src/utils/pdf'

interface CompanyInfo {
  name: string
  organization_type: string
  address: string
  tax_identification_number: string
  logo_url: string
  contact_no: string
  config_template: string
  emails: string[]
}

interface InvoiceInfo {
  party: boolean
  customer_name?: string
  party_name?: string
  address?: string
  tax_identification_number?: string
  voucher_no?: string
  fiscal_year?: string
  reference?: string
  remarks?: string
  date: string
  total_amount?: number
  mode?: string
  status?: string
  party_contact_no?: string
  rows: Array<{
    hs_code?: string
    item_name: string
    description?: string
    quantity: number
    unit_name?: string
    rate: number
    tax_scheme?: { name?: string, rate?: number }
  }>
  voucher_meta: {
    sub_total: number
    discount?: number
    tax?: number
    grand_total: number
  }
}

defineProps<{
  companyInfo: CompanyInfo
  showTaxColumn: boolean
  emptyRows: boolean
  showTaxRateBeforeName: boolean
  invoiceInfo: InvoiceInfo
  hideRowQuantity: boolean
  voucherType: string
  sameTax: boolean
  taxIndex: number
}>()
</script>

<template>
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
        <th v-if="showTaxColumn" style="text-align: left; padding: 5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">
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
        <th v-if="showTaxColumn" style="width: 20%; text-align: left; font-weight: 400; padding: 5px; border-right: #b9b9b9 solid 2px;">
          {{ row.tax_scheme ? row.tax_scheme.name : '' }}
        </th>
        <th style="text-align: right; font-weight: 400; padding: 5px;">
          {{ formatNumberWithComma(row.quantity * row.rate) }}
        </th>
      </tr>
      <tr v-if="emptyRows" style="color: grey; font-weight: 400;">
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
          v-if="invoiceInfo.voucher_meta.discount"
          style="margin: 5px 0; border-bottom: 2px solid #b9b9b9; display: flex; justify-content: space-between; padding: 5px 0;"
        >
          <span style="font-weight: 600; color: lightgray;">DISCOUNT</span>
          <span>{{ formatNumberWithComma(invoiceInfo.voucher_meta.discount) }}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 2px solid #b9b9b9;">
          <span style="font-weight: 600; color: lightgray;">
            {{ sameTax && invoiceInfo.rows[taxIndex]?.tax_scheme ? (showTaxRateBeforeName ? `${invoiceInfo.rows[taxIndex].tax_scheme.rate} % ${invoiceInfo.rows[taxIndex].tax_scheme.name}` : `${invoiceInfo.rows[taxIndex].tax_scheme.name} ${invoiceInfo.rows[taxIndex].tax_scheme.rate} %`) : 'TAX' }}
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
</template>
