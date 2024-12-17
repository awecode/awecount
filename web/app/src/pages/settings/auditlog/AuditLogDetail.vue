<script>
import useApi from 'src/composables/useApi'

export default {
  setup() {
    const fields = ref(null)
    useMeta(() => {
      return {
        title:
          `${fields.value?.content_type_name
            ? fields.value.content_type_name
            : 'Audit Logs Details'} | Awecount`,
      }
    })
    return {
      fields,
    }
  },
  created() {
    const endpoint = `/api/company/${this.$route.params.company}/log-entries/${this.$route.params.id}/`
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ path: '/ErrorNotFound' })
        }
      })
  },
}
</script>

<template>
  <div v-if="fields">
    <q-card class="q-ma-lg text-grey-8">
      <h5 class="text-h6 text-grey-9 text-weight-medium q-ma-none q-py-sm q-px-md bg-grey-4">
        {{ fields.content_type_name }}
      </h5>
      <q-card-section>
        <div class="q-mb-sm text-h6 text-grey-8">
          {{ fields.action }}
        </div>
        <div>
          <span class="text-weight-medium text-grey-9">User: </span>
          <span>{{ fields.actor }}</span>
        </div>
        <div>
          <span class="text-weight-medium text-grey-9">Datetime: </span>
          <span>{{ fields.datetime }}</span>
        </div>
        <div>
          <span class="text-weight-medium text-grey-9">Remote Address: </span>
          <span>{{ fields.remote_addr }}</span>
        </div>
        <q-markup-table flat bordered class="q-mt-md">
          <thead>
            <q-tr class="text-left">
              <q-th> Field </q-th>
              <q-th> Original </q-th>
              <q-th> Changed </q-th>
            </q-tr>
          </thead>
          <tbody class="text-left">
            <q-tr
              v-for="(value, key, index) in fields?.changes_obj"
              :key="index"
            >
              <q-td>
                {{ key }}
              </q-td>
              <q-td>
                {{ value[0] }}
              </q-td>
              <q-td>
                {{ value[1] }}
              </q-td>
            </q-tr>
          </tbody>
        </q-markup-table>
      </q-card-section>
    </q-card>
  </div>
</template>

<style>
.search-bar {
  display: flex;
  width: 100%;
  column-gap: 20px;
}

.search-bar-wrapper {
  width: 100%;
}

.filterbtn {
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
