<template>
  <div class="q-pa-lg" v-if="fields">
    <div class="text-h6">
      Journal Entries for {{ fields[0]?.voucher_type }} #{{
        fields[0]?.voucher_no
      }}
    </div>
    <q-card class="q-mt-md" v-for="(field, index) in fields" :key="index">
      <q-card-section>
        <div class="q-pa-md">
          <div class="q-pb-md q-mb-md text-subtitle">
            Date: <span class="text-bold">{{ field?.date }}</span>
          </div>

          <div>
            <!-- Head -->
            <div class="row text-bold q-px-md q-mb-md text-subtitle">
              <div class="col-4">Account</div>
              <div class="col-4">DR.</div>
              <div class="col-4">CR.</div>
            </div>

            <!-- Body -->
            <div v-for="(row, index) in field?.transactions" :key="row.id">
              <div class="row q-py-sm q-px-md">
                <div class="col-4">{{ row.account.name }}</div>
                <div class="col-4">{{ row.dr_amount || '-' }}</div>
                <div class="col-4">{{ row.cr_amount || '-' }}</div>
              </div>
              <hr v-if="field.transactions?.length !== index + 1" />
            </div>

            <!-- Sub Total -->
            <div class="row q-py-md bg-grey-4 q-px-md text-bold q-mt-sm">
              <div class="col-4">Sub-total</div>
              <div class="col-4">
                {{
                  field?.transactions.reduce(
                    (accum, item) => accum + Number(item.dr_amount),
                    0
                  ) || 0
                }}
              </div>
              <div class="col-4">
                {{
                  field?.transactions.reduce(
                    (accum, item) => accum + Number(item.cr_amount),
                    0
                  ) || 0
                }}
              </div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-card class="q-mt-md bg-grey-3 text-bold">
      <q-card-section>
        <div class="row">
          <div class="col-4">Total</div>
          <div class="col-4">
            {{
              fields[0]?.transactions.reduce(function (acc, transaction) {
                return acc + (transaction.dr_amount || 0)
              }, 0) || 0
            }}
          </div>
          <div class="col-4">
            {{
              fields[0]?.transactions.reduce(function (acc, transaction) {
                return acc + (transaction.cr_amount || 0)
              }, 0) || 0
            }}
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import useApi from 'src/composables/useApi'
const $q = useQuasar()
const route = useRoute()
console.log(route.params.slug)
const fields = ref(null)
useApi(`/v1/${route.params.slug}/${route.params.id}/journal-entries/`)
  .then((data) => {
    fields.value = data
  })
  .catch(() => {
    $q.notify({
      color: 'negative',
      message: 'Error',
      icon: 'report_problem',
    })
  })

// TODO: add useCase for multiple journal voucher
</script>
