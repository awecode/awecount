<template>
  <tr>
    <td>Hiome</td>
    <td>loajsga</td>
  </tr>
  {{ props.item }} --props
</template>

<script setup>
const props = defineProps('item', 'root', 'cat-map', 'accounts', 'config')
</script>
