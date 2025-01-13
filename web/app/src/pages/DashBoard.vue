<script>
import { useMeta } from 'quasar'
import useApi from 'src/composables/useApi'

export default {
  setup() {
    const metaData = {
      title: 'Dashboard',
      titleTemplate: title => `${title} | Awecount`,
    }
    useMeta(metaData)
    const fields = ref(null)
    return {
      fields,
    }
  },
  created() {
    const endpoint = '/v1/widgets/data/'
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
      })
      .catch(error => console.log(error))
  },
}
</script>

<template>
  <div class="q-ma-md">
    <div>
      <q-btn
        icon="add"
        label="Add widget"
        style="font-size: 0.75rem"
        to="/dashboard-widgets/add"
      />
    </div>
    <div class="q-mt-md grid-con">
      <div v-for="widget in fields" :key="widget.id">
        <q-card class="q-py-sm q-px-md" style="height: 100%">
          <div>
            <div class="row no-wrap justify-between q-my-sm">
              <h5 styl class="q-my-none text-h6 text-grey-8" e="flex-grow: 1">
                {{ widget.name }}
              </h5>
              <span style="flex-grow: 0; flex-shrink: 0">
                <q-btn
                  flat
                  class="text-grey-8"
                  icon="edit"
                  size="sm"
                  :to="`/dashboard-widgets/${widget.id}`"
                />
              </span>
            </div>
            <div>
              <div v-if="widget.data.type === 'table'">
                <q-markup-table flat>
                  <thead>
                    <tr>
                      <th v-for="value in widget.data.labels" :key="value" class="text-left">
                        {{ value }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in widget.data.datasets" :key="index">
                      <td v-for="(value, index) in row" :key="index" class="text-left">
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
