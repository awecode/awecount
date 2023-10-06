<template>
    <!-- style="height: 40px; overflow-y: hidden;" -->
    <div>
        <div v-for="(account, index) in props.accounts" :key="account.id">
            <router-link v-if="account.id !== accountId && showAllAccounts || index < 3" :to="`/account/${account.id}/view/`"
                style="font-weight: 500; text-decoration: none" class="text-blue" :title="`${account.name}`">
                {{ account.name }}
            </router-link>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps({
    accounts: {
        type: Array,
        required: true
    },
    accountId: {
        type: Number,
        required: true
    }
})
const showAllAccounts = ref(false)
</script>