<script setup lang="ts">
const props = defineProps({
  accounts: {
    type: Array,
    required: true,
  },
})
const openState = ref(false)
</script>

<template>
  <!-- style="height: 40px; overflow-y: hidden;" -->
  <div v-if="props.accounts.length > 2">
    <div class="transition" :class="`${openState ? '' : 'max-h-[40px]'} overflow-y-hidden accounts-con`">
      <div v-for="(account, index) in props.accounts" :key="index">
        <router-link class="text-blue block" style="font-weight: 500; text-decoration: none" :to="`/${$route.params.company}/account/${account.id}/view/`">
          {{ account.name }}
        </router-link>
      </div>
    </div>
    <div class="hover:bg-gray-200 text-center" @click="openState = !openState">
      <q-icon
        class="transition-transform"
        color="blue"
        name="mdi-chevron-down"
        size="sm"
        :class="openState ? 'rotate-180' : ''"
      />
    </div>
  </div>
  <div v-else>
    <div v-for="(account, index) in props.accounts" :key="index">
      <router-link class="text-blue block" style="font-weight: 500; text-decoration: none" :to="`/${$route.params.company}/account/${account.id}/view/`">
        {{ account.name }}
      </router-link>
    </div>
  </div>
</template>

<style scoped>
@media print {
  .accounts-con {
    max-height: none !important;
  }
}
</style>
