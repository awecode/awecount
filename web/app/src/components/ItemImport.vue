<template>
    <div class="q-ma-lg">
        <q-card>
            <q-card-section class="bg-green text-white">
                <div class="text-h6">
                    <span>Import Items From Excel Sheet</span>
                </div>
            </q-card-section>
            <q-card-section>
                <q-form @submit="onSubmit()" autofocus>
                    <q-file v-model="file" name="file" style="max-width: 400px;"
                        accept=".xml,,application/vnd.openxmlformats-officedocument.wordprocessingml.document" label="Select File" ></q-file>
                    <q-btn :loading="loading" color="green" type="submit" class="q-mt-lg">Upload</q-btn>
                    <!-- <q-spinner v-else color="blue" size="2em" :thickness="6" class="q-mt-lg"/> -->
                </q-form>
            </q-card-section>
        </q-card>
    </div>
</template>

<script setup>
const $q = useQuasar()
const file = ref(null)
const loading = ref(false)
const emit = defineEmits('modalClose')
const onSubmit = async () => {
    const formData = new FormData()
    formData.append('file', file.value)
    loading.value = true
    useApi('/v1/items/import/', {
        method: 'POST',
        body: formData,
    })
        .then(() => {
            loading.value = false
            emit('modalClose')
            $q.notify({
                color: 'green-6',
                message: 'Items Imported!',
                icon: 'check_circle',
                position: 'top-right',
            })
        })
        .catch((err) => {
            loading.value = false
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
