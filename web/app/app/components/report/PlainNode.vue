<script lang="ts">
export default defineNuxtComponent({
  props: {
    data: {
      type: Object,
      default: () => {
        return {}
      },
    },
    root: {
      type: Boolean,
      default: () => {
        return false
      },
    },
  },
  setup() {
    return {}
  },
})
</script>

<template>
  <div style="line-height: 0.5rem">
    <router-link
      class="text-blue"
      style="text-decoration: none"
      target="_blank"
      :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${data.id}`"
    >
      <strong v-if="root">{{ data.name }}</strong>
      <span v-else>{{ data.name }}</span>
    </router-link>

    <hr />
    <div v-if="data.children && data.children.length">
      <div v-for="child in data.children" :key="child.id" style="margin-left: 2em">
        <PlainNode :data="child" />
      </div>
    </div>
  </div>
</template>
