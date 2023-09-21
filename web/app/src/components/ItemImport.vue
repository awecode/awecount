<template>
    <div class="q-ma-lg">
        <div>
            Import xls from
        </div>
        <q-form @submit="() => onSubmit(file)" autofocus>
            <q-input type="file" v-model="file" name="file"></q-input>
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
</script>