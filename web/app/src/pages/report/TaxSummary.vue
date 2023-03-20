<template>
  <q-card class="q-ma-md q-px-md">
    <q-card-section>
      <div>
        <div class="row q-gutter-x-md items-end">
          <q-input v-model="fields.start_date" label="Date">
            <template v-slot:append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy
                  cover
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <q-date
                    v-model="fields.start_date"
                    today-btn
                    mask="YYYY-MM-DD"
                  >
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
          <q-input v-model="fields.end_date" label="Date">
            <template v-slot:append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy
                  cover
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <q-date v-model="fields.end_date" today-btn mask="YYYY-MM-DD">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
          <q-btn
            v-if="fields.start_date || fields.end_date"
            color="red"
            icon="close"
            @click="fields = { start_date: null, end_date: null }"
          ></q-btn>
          <q-btn
            :disable="!fields.start_date && !fields.end_date ? true : false"
            color="green"
            label="fetch"
            @click="fetchData"
          ></q-btn>
        </div>
      </div>
      <div v-if="reportData">
        <q-card class="q-mt-md">
          <q-markup-table>
            <thead>
              <tr>
                <th class="text-left"></th>
                <th class="text-center">Transaction Amount</th>
                <th class="text-center">Tax on Purchase</th>
                <th class="text-center">Tax on Sales</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><th class="text-left subHeading">1. Sales</th></td>
              </tr>
              <tr>
                <td class="text-left">1.1 Taxable Sales</td>
                <td class="text-center">
                  {{ reportData.sales.total_meta_taxable }}
                </td>
                <td class="text-center"></td>
                <td class="text-center">
                  {{ reportData.sales.total_meta_tax }}
                </td>
              </tr>
              <tr>
                <td class="text-left">1.2 Export</td>
                <td class="text-center">
                  {{ reportData.sales.total_export || 0 }}
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <td class="text-left">1.3 Non-taxable Sales</td>
                <td class="text-center">
                  {{ reportData.sales.total_meta_non_taxable || 0 }}
                </td>
                <td class="text-center"></td>
                <td class="text-center"></td>
              </tr>
              <tr>
                <td><th class="text-left subHeading">2. Purchase</th></td>
              </tr>
              <tr>
                <td class="text-left">2.1 Taxable Purchase</td>
                <td class="text-center">
                  {{ reportData.purchase.total_meta_taxable }}
                </td>
                <td class="text-center">
                  {{ reportData.purchase.total_meta_tax }}
                </td>
                <td class="text-center">
                </td>
              </tr>
              <tr>
                <td class="text-left">2.2 Taxable Import</td>
                <td class="text-center">
                  {{ reportData.import.total_meta_taxable || 0 }}
                </td>
                <td class="text-center">
                  {{ reportData.import.total_meta_tax || 0 }}
                </td>
                <td class="text-center">
                </td>
              </tr>
              <tr>
                <td class="text-left">2.3 Non-taxable Purchase</td>
                <td class="text-center">
                  {{ reportData.purchase.total_meta_non_taxable || 0 }}
                </td>
                <td class="text-center">
                </td>
                <td class="text-center">
                </td>
              </tr>
              <tr>
                <td class="text-left">2.4 Non-taxable Import</td>
                <td class="text-center">
                  {{ reportData.import.total_meta_non_taxable || 0 }}
                </td>
                <td class="text-center">
                </td>
                <td class="text-center">
                </td>
              </tr>
              <tr>
                <td colspan="2" class="text-center text-black"><span class="text-center" style="color: black;"><th>Tax Payable</th></span></td>
                <td colspan="2" class="text-center text-weight-bold"><span class="text-center" style="color: black;"><th>{{ parseFloat((reportData.sales.total_meta_tax - reportData.purchase.total_meta_tax).toFixed(2)) }}</th></span></td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-card>
      </div>
    </q-card-section>
  </q-card>
</template>

<script lang="ts">
import { Ref } from 'vue'
export default {
  setup() {
    const reportData: Ref<Record<string, string | object> | null> = ref(null)
    const fields: Ref<Record<string, Date | null>> = ref({
      start_date: null,
      end_date: null,
    })
    const fetchData = () => {
      const endpoint = `/v1/tax-summary/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => (reportData.value = data))
        .catch((err) => console.log(err))
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
    return { reportData, fetchData, fields }
  },
}
</script>

<style scoped>
.subHeading {
  padding: 0;
}
th, td {
  font-size: 15px;
}
</style>
