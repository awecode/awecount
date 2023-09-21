<template>
  <div class="q-ma-lg">
    <q-card>
      <q-card-section class="bg-blue text-white">
        <div class="text-h6">
          <span>Import Items From XLS</span>
        </div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit()" autofocus>
          <q-file
            v-model="file"
            name="file"
            accept=".xml,,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          ></q-file>
          <q-btn color="blue" type="submit" class="q-mt-lg">Upload</q-btn>
        </q-form>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
const $q = useQuasar()
const file = ref(null)
const emit = defineEmits('modalClose')
const onSubmit = async () => {
  const formData = new FormData()
  formData.append('file', file.value)
  useApi('/v1/items/import/', {
    method: 'POST',
    body: formData,
  })
    .then(() => {
      emit('modalClose')
      $q.notify({
        color: 'green-6',
        message: 'Items Imported!',
        icon: 'check_circle',
        position: 'top-right',
      })
    })
    .catch((err) => {
      $q.notify({
        color: 'red-6',
        message:
          err.status !== '400'
            ? 'Server Error! Please contact us with the problem.'
            : `${err.message}`,
        icon: 'report_problem',
        position: 'top-right',
      })
    })
}
</script>
