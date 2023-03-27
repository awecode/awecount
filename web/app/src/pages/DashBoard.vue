<template>
  <div class="q-ma-md">
    <div>
      <q-btn
        icon="add"
        label="Add widget"
        to="/dashboard-widgets/add"
        style="font-size: 0.75rem"
      ></q-btn>
    </div>
    <div class="row q-mt-md">
      <div v-for="widget in fields" :key="widget.id">{{ widget.id }}</div>
    </div>
  </div>
</template>

<script>
import useApi from 'src/composables/useApi'
export default {
  setup() {
    const fields = ref(null)
    return {
      fields,
    }
  },
  created() {
    const endpoint = '/v1/widgets/data/'
    console.log(endpoint)
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ name: '404' })
        }
      })
  },
}
</script>

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
