<script setup lang="ts">
interface CompanyInfo {
  name: string
  organization_type: string
  address: string
  tax_identification_number: string
  logo_url: string
  contact_no: string
  emails: string[]
  website?: string
}

defineProps<{
  companyInfo: CompanyInfo
  logoStyle?: Record<string, string>
}>()
</script>

<template>
  <div>
    <div style="position: relative; margin-bottom: 10px;">
      <img
        alt="Company Logo"
        style="height: 110px; object-fit: contain; max-width: 160px; position: absolute;"
        :src="companyInfo.logo_url"
        :style="logoStyle"
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
</template>
