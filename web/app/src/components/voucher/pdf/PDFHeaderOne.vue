<script setup lang="ts">
interface CompanyInfo {
  name: string
  organization_type: string
  address: string
  tax_identification_number: string
  logo_url: string
  contact_no: string
  emails: string[]
}

defineProps<{
  companyInfo: CompanyInfo
}>()
</script>

<template>
  <div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif;">
    <div>
      <h1 style="margin: 5px 0; font-size: 35px; font-weight: 700;">
        {{ companyInfo.name }}
        {{ companyInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.' : ['public_limited', 'corporation'].includes(companyInfo.organization_type) ? 'Ltd.' : '' }}
      </h1>
      <div v-if="companyInfo.address">
        {{ companyInfo.address }}
      </div>
      <div v-if="companyInfo.tax_identification_number">
        Tax Reg. No. <strong>{{ companyInfo.tax_identification_number }}</strong>
      </div>
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
</template>
