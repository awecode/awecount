<template>
    <!-- style="height: 40px; overflow-y: hidden;" -->
    <div>
        <div v-for="(id, index) in props.account_ids" :key="index">
            <router-link :to="`/account/${id}/view/`" style="font-weight: 500; text-decoration: none"
                class="text-blue block" :title="`${accountNamesArray[index]}`">
                {{ accountNamesArray[index] }}
            </router-link>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps({
    account_ids: {
        type: Array,
        required: true
    },
    account_names: {
        type: String,
        required: true
    },
    accountId: {
        type: Number,
        required: true
    }
})
const accountNamesArray = computed(() => {
    return props.account_names.split('\u0283')
})
</script>