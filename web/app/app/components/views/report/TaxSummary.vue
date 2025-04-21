<script lang="ts">
import type { Ref } from 'vue'
import { $nf } from '@/composables/global'

export default defineNuxtComponent({
  setup() {
    const metaData = {
      title: 'Periodic Tax Summary | Awecount',
    }
    const route = useRoute()
    useHead(metaData)
    const reportData: Ref<Record<string, string | object> | null> = ref(null)
    const fields: Ref<Record<string, Date | null>> = ref({
      start_date: null,
      end_date: null,
    })
    const fetchData = () => {
      const endpoint = `/api/company/${route.params.company}/tax-summary/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then(data => (reportData.value = data))
        .catch(err => console.log(err))
      // TODO: add 404 error routing
    }
    // const taxSummaryComputed = computed(() => {
    //   if (reportData) {
    //       const data = {
    //       tax_payable: false,
    //       amonut: 0
    //     }
    //     const netAmount = reportData.value.sales.total_meta_tax - reportData.value.purchase.total_meta_tax
    //     if (netAmount > -1) {
    //       data.tax_payable = true
    //       data.amonut = netAmount
    //     } else {
    //       data.tax_payable = false
    //       data.amonut = reportData.value.purchase.total_meta_tax - reportData.value.sales.total_meta_tax
    //     }
    //     return data
    //   }
    //   else return null
    // })
    return { reportData, fetchData, fields, $nf }
  },
})
</script>

<template>
  <q-card class="q-ma-md q-px-md">
    <q-card-section>
      <div>
        <div class="row q-gutter-x-md items-center">
          <div class="q-mx-md">
            <DateRangePicker v-model:end-date="fields.end_date" v-model:start-date="fields.start_date" :hide-btns="true" />
          </div>
          <q-btn
            v-if="fields.start_date || fields.end_date"
            class="f-reset-btn"
            color="red"
            icon="close"
            @click="fields = { start_date: null, end_date: null }"
          />
          <q-btn
            class="f-submit-btn"
            color="green"
            label="fetch"
            :disable="!fields.start_date && !fields.end_date ? true : false"
            @click="fetchData"
          />
        </div>
      </div>
      <div v-if="reportData">
        <q-card class="q-mt-md">
          <q-markup-table>
            <thead>
              <tr>
                <th class="text-left"></th>
                <th class="text-center">
                  Transaction Amount
                </th>
                <th class="text-center">
                  Tax on Purchase
                </th>
                <th class="text-center">
                  Tax on Sales
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th class="text-left subHeading">
                  1. Sales
                </th>
              </tr>
              <tr>
                <td class="text-left">
                  1.1 Taxable Sales
                </td>
                <td class="text-center">
                  {{ $nf(reportData.sales.total_meta_taxable) }}
                </td>
                <td class="text-center"></td>
                <td class="text-center">
                  {{ $nf(reportData.sales.total_meta_tax) }}
                </td>
              </tr>
              <tr>
                <td class="text-left">
                  1.2 Export
                </td>
                <td class="text-center">
                  {{ $nf(reportData.sales.total_export) }}
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <td class="text-left">
                  1.3 Non-taxable Sales
                </td>
                <td class="text-center">
                  {{ $nf(reportData.sales.total_meta_non_taxable) }}
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <th class="text-left subHeading">
                  2. Purchase
                </th>
              </tr>
              <tr>
                <td class="text-left">
                  2.1 Taxable Purchase
                </td>
                <td class="text-center">
                  {{ $nf(reportData.purchase.total_meta_taxable) }}
                </td>
                <td class="text-center">
                  {{ $nf(reportData.purchase.total_meta_tax) }}
                </td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <td class="text-left">
                  2.2 Taxable Import
                </td>
                <td class="text-center">
                  {{ $nf(reportData.import.total_meta_taxable) }}
                </td>
                <td class="text-center">
                  {{ $nf(reportData.import.total_meta_tax) }}
                </td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <td class="text-left">
                  2.3 Non-taxable Purchase
                </td>
                <td class="text-center">
                  {{ $nf(reportData.purchase.total_meta_non_taxable) }}
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <td class="text-left">
                  2.4 Non-taxable Import
                </td>
                <td class="text-center">
                  {{ $nf(reportData.import.total_meta_non_taxable) }}
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <td class="text-center text-black" colspan="2">
                  <span class="text-center" style="color: black">
                    Tax Payable
                  </span>
                </td>
                <td class="text-center text-weight-bold" colspan="2">
                  <span class="text-center" style="color: black">
                    {{ $nf(reportData.sales.total_meta_tax - reportData.purchase.total_meta_tax) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card>
      </div>
    </q-card-section>
  </q-card>
</template>

<style scoped>
.subHeading {
  padding: 0;
}

th,
td {
  font-size: 15px;
}
</style>
