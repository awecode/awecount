<script setup lang="ts">
import DateConverter from 'src/components/date/VikramSamvat.js'

interface CompanyInfo {
  name: string
  organization_type: string
  address: string
  tax_identification_number: string
  logo_url: string
  contact_no: string
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
  date: string
  mode?: string
  status?: string
  party_contact_no?: string
}
defineProps<{
  companyInfo: CompanyInfo
  invoiceInfo: InvoiceInfo
  showPartyContactNo: boolean
}>()
</script>

<template>
  <div style="display: flex; justify-content: space-between;">
    <div style="display: flex; flex-direction: column; gap: 2px;">
      <div style="font-weight: 600; color: grey;">
        Billed To:
      </div>
      <div>{{ invoiceInfo.party ? invoiceInfo.customer_name || invoiceInfo.party_name : invoiceInfo.customer_name || '' }}</div>
      <div v-if="invoiceInfo.address">
        {{ invoiceInfo.address }}
      </div>
      <div v-if="invoiceInfo.party_contact_no && showPartyContactNo">
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
