<template>
  <div style="line-height: 0.5rem">
    <router-link :to="'/account/?has_balance=true&category=' + data.id" target="_blank" style="text-decoration: none; display: flex; align-items: center" class="text-blue">
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

<script lang="ts">
export default {
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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props) {
    return
  },
}
</script>
