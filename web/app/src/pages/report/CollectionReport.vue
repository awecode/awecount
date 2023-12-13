<template>
  <q-card class="q-ma-md q-px-md">
    <q-card-section>
      <div>
        <div class="flex gap-8 items-center">
          <div>
            <DateRangePicker
              v-model:startDate="fields.start_date"
              v-model:endDate="fields.end_date"
              :hide-btns="true"
            />
          </div>
          <q-btn
            v-if="fields.start_date || fields.end_date"
            color="red"
            icon="close"
            @click="fields = { start_date: null, end_date: null }"
            class="f-reset-btn"
          ></q-btn>
          <q-btn
            :disable="!fields.start_date && !fields.end_date ? true : false"
            color="green"
            label="fetch"
            @click="fetchData"
            class="f-submit-btn"
          ></q-btn>
        </div>
      </div>
      <div v-if="reportData">
        <q-card class="q-mt-md">
          <div>
            <div class="row q-pa-md" style="border-bottom: 2px solid lightgray">
              <div class="col-6 text-weight-medium text-grey-8">
                Sales Agent
              </div>
              <div class="col-6 text-weight-medium text-grey-8">Amount</div>
            </div>
            <div
              v-for="row in reportData.values"
              :key="row.invoices__sales_agent_id"
              class="row q-pa-md"
              style="border-bottom: 2px solid lightgray"
            >
              <div class="col-6 text-grey-8">
                <router-link
                  :to="`/payment-receipt/list?start_date=${fields.start_date}&end_date=${fields.end_date}&sales_agent=${row.invoices__sales_agent_id}`"
                  target="_blank"
                  style="text-decoration: none"
                  class="text-blue"
                >
                  {{ row.invoices__sales_agent__name }}
                </router-link>
              </div>
              <div class="col-6 text-grey-8">
                <router-link
                  :to="`/payment-receipt/list?start_date=${fields.start_date}&end_date=${fields.end_date}&sales_agent=${row.invoices__sales_agent_id}`"
                  target="_blank"
                  style="text-decoration: none"
                  class="text-blue"
                >
                  {{ row.total_amount }}
                </router-link>
              </div>
            </div>
            <div class="row q-pa-md">
              <div class="col-6 text-weight-medium text-grey-9">Total</div>
              <div class="col-6 text-weight-medium text-grey-9">
                {{ reportData.total }}
              </div>
            </div>
          </div>
        </q-card>
        <q-card class="q-mt-sm" v-if="reportData.excluded.length">
          <q-card-section>
            <div class="text-grey-9">
              <strong>Excluded Payment Receipts:</strong>
            </div>
            <div class="row q-gutter-x-md q-mt-sm">
              <span
                v-for="item in reportData.excluded"
                :key="item.id"
                class="q-py-xs q-px-md bg-red-5 text-weight-medium text-white rounded-borders"
                ># {{ row.id }}</span
              >
            </div>
            <!-- TODO: check if this works -->
          </q-card-section>
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
    const metaData = {
      title: 'Collection Report | Awecount',
    }
    useMeta(metaData)
    const fetchData = () => {
      const endpoint = `/v1/payment-receipt/collection-report/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => (reportData.value = data))
        .catch((err) => console.log(err))
      // TODO: add 404 error routing
    }
    return { reportData, fetchData, fields }
  },
}
</script>
