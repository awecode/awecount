<script setup lang="ts">
import { useMeta } from 'quasar'
import { $api } from 'src/composables/api'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

useMeta({
  title: 'Dashboard',
  titleTemplate: (title: string) => `${title} | Awecount`,
})

const route = useRoute()
const fields = ref(null)

const endpoint = `/api/company/${route.params.company}/widgets/data/`
const res = await $api(endpoint, { method: 'GET', protected: true })
fields.value = res
</script>

<template>
  <div class="q-ma-md">
    <div>
      <q-btn
        icon="add"
        label="Add widget"
        :to="`/${route.params.company}/settings/dashboard-widgets/add`"
        style="font-size: 0.75rem"
      />
    </div>
    <div class="q-mt-md grid-con">
      <div v-for="widget in fields" :key="widget.id">
        <q-card class="q-py-sm q-px-md" style="height: 100%">
          <div>
            <div class="row no-wrap justify-between q-my-sm">
              <h5 class="q-my-none text-h6 text-grey-8">
                {{ widget.name }}
              </h5>
              <span style="flex-grow: 0; flex-shrink: 0">
                <q-btn
                  flat
                  icon="edit"
                  :to="`/${route.params.company}/settings/dashboard-widgets/${widget.id}/edit`"
                  size="sm"
                  class="text-grey-8"
                />
              </span>
            </div>
            <div>
              <div v-if="widget.data.type === 'table'">
                <q-markup-table flat>
                  <thead>
                    <tr>
                      <th
                        v-for="value in widget.data.labels"
                        :key="value"
                        class="text-left"
                      >
                        {{ value }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(row, index) in widget.data.datasets"
                      :key="index"
                    >
                      <td
                        v-for="(value, index) in row"
                        :key="index"
                        class="text-left"
                      >
                        {{ value }}
                      </td>
                    </tr>
                  </tbody>
                </q-markup-table>
              </div>
              <div v-else>
                <ChartsView :data="widget.data" />
              </div>
            </div>
          </div>
        </q-card>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.grid-con {
  display: grid;
  grid-gap: 1rem;
  grid-template-columns: 1fr 1fr;
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}
</style>
