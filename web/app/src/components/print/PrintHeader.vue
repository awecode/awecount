<script setup>
import { useLoginStore } from 'src/stores/login-info'

const store = useLoginStore()
</script>

<template>
  <div class="print-only">
    <div v-if="store.companyInfo.invoice_template == 1">
      <div style="position: relative; margin-bottom: 10px">
        <img
          v-if="store.companyInfo.logo_url"
          alt="Company Logo"
          style="height: 110px; object-fit: contain; max-width: 160px; position: absolute"
          :src="store.companyInfo.logo_url"
        />
        <div style="text-align: center; padding-left: 10px">
          <h1 style="line-height: normal; margin: 5px 0; font-size: 35px; font-weight: 500">
            {{ store.companyInfo.name }}
            {{
              store.companyInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.'
              : ['public_limited', 'corporation'].includes(store.companyInfo.organization_type) ? 'Ltd.'
                : ''
            }}
          </h1>
          <div>{{ store.companyInfo.address }}</div>
          <div style="font-size: 14px">
            <div style="display: flex; justify-content: center; flex-direction: column">
              <div style="display: flex; align-items: center; justify-content: center">
                <span>Email: {{ store.companyInfo.emails && store.companyInfo.emails.length ? store.companyInfo.emails.join(',&nbsp;') : '' }}</span>
              </div>
              <div style="display: flex; align-items: center; justify-content: center">
                <span>Tel: {{ store.companyInfo.contact_no }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div style="display: flex; justify-content: end; font-family: Arial, Helvetica, sans-serif">
        <div style="display: flex; flex-direction: column; gap: 3px; align-items: flex-end">
          <div style="font-size: 14px">
            VAT No.
            <strong>{{ store.companyInfo.tax_identification_number }}</strong>
          </div>
          <div v-if="store.companyInfo.website" class="flex items-center">
            <img alt="Website" src="/icons/web-fill.svg" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ store.companyInfo.website }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="store.companyInfo.invoice_template == 2">
      <div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif">
        <div>
          <h1 style="margin: 5px 0; font-size: 35px; font-weight: 500">
            {{ store.companyInfo.name }}
            {{
              store.companyInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.'
              : ['public_limited', 'corporation'].includes(store.companyInfo.organization_type) ? 'Ltd.'
                : ''
            }}
          </h1>
          <div v-if="store.companyInfo.address">
            {{ store.companyInfo.address }}
          </div>
          <div v-if="store.companyInfo.tax_identification_number">
            Tax Reg. No.
            <strong>
              {{ store.companyInfo.tax_identification_number }}
            </strong>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 5px; align-items: flex-end">
          <div style="margin-bottom: 5px">
            <img alt="Company Logo" style="height: 70px; max-width: 200px; object-fit: contain" :src="store.companyInfo.logo_url" />
          </div>
          <div style="display: flex; align-items: center">
            <img alt="Telephone" src="/icons/telephone-fill.svg" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ store.companyInfo.contact_no }}</span>
          </div>
          <div style="display: flex; align-items: center">
            <img alt="Email" src="/icons/envelope-fill.svg" style="margin-right: 10px; width: 14px" />
            <span style="color: skyblue">{{ store.companyInfo.emails && store.companyInfo.emails.length ? store.companyInfo.emails.join(',&nbsp;') : '' }}</span>
          </div>
        </div>
      </div>
    </div>
    <hr style="margin: 20px 0" />
  </div>
</template>
