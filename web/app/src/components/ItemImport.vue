<template>
    <div class="q-ma-lg">
        <div>
            Import xls from
        </div>
        <q-form @submit="() => onSubmit(file)" autofocus>
            <q-file v-model="file" name="file" @update:model-value="
                onFileChange(file, $event, 'front_image')"></q-file>
            <q-btn type="submit">Upload</q-btn>
        </q-form>
    </div>
</template>

<script setup>
const file = ref(null)
const onSubmit = async (file) => {
    useApi('/v1/items/import/', {
        method: 'POST',
        body: { file: file.value },
    }).then(() => console.log('done')).catch((err) => console.log('error due to', err))
}
const onFileChange = (dct, event, attr) => {
    const file = event
    let reader = new FileReader()
    reader.readAsDataURL(file)
    reader.fileName = file.name
    reader.onload = () => {
        console.log(file)
        file.value = reader.result
    }
    reader.onerror = function (error) {
        console.error('Error: ', error)
    }
}
</script>