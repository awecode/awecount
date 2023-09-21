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
                    <q-file v-model="file" name="file" accept=".xml,,application/vnd.openxmlformats-officedocument.wordprocessingml.document"></q-file>
                    <q-btn color="blue" type="submit" class="q-mt-lg">Upload</q-btn>
                </q-form>
            </q-card-section>
        </q-card>
    </div>
</template>

<script setup>
const file = ref(null)
const onSubmit = async () => {
    const formData = new FormData()
    formData.append('file',file.value)
    useApi('/v1/items/import/', {
        method: 'POST',
        body: formData,
    }).then(() => console.log('done')).catch((err) => console.log('error due to', err))
}
</script>