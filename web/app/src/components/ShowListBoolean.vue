<template>
  <q-icon v-if="props.value" color="green-5" name="mdi-checkbox-marked-circle" size="sm">
    <q-tooltip>True</q-tooltip></q-icon>
  <q-icon v-else color="red-5" name="mdi-close-circle" size="sm"><q-tooltip>False</q-tooltip></q-icon>
</template>

<script setup lang="ts">
const props = defineProps({
  value: {
    required: true,
    type: Boolean
  }
})
</script>
