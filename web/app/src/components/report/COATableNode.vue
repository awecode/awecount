<template>
  <tr class="hover:bg-gray-50">
    <td
      class="flex items-center"
      :style="`padding-left: ${15 + 30 * (row.level || 0)}px;`"
    >
      <RouterLink
        style="text-decoration: none"
        target="_blank"
        :to="`/account/?has_balance=true&category=${row.id}`"
        class="text-blue-6"
        :class="props.root ? 'text-weight-bold' : ''"
        >{{ row.name }}</RouterLink
      >
      <q-btn
        dense
        flat
        round
        class="expand-btn"
        :class="expandedRows[row.id] ? 'expanded' : ''"
        @click="$emit('toggle-expand', row.id)"
        v-if="row.isExpandable"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="32"
          height="32"
          viewBox="0 0 24 24"
          class="text-grey-7"
        >
          <path
            fill="currentColor"
            d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z"
          />
        </svg>
      </q-btn>
    </td>
    <td></td>
    <td></td>
    <td></td>
    <td>{{ row.code }}</td>
    <td>{{ row.system_code }}</td>
    <td>{{ row.total_transactions }}</td>
  </tr>
  <template v-if="expandedRows[row.id]">
    <COATableNode
      v-for="child in row.children"
      :key="child.id"
      :row="child"
      :expandedRows="expandedRows"
      @toggle-expand="$emit('toggle-expand', $event)"
    />
    <tr v-for="account in row.accounts" :key="account.id">
      <td
        :style="`padding-left: ${15 + 30 * ((row.level || 0) + 1)}px`"
        colspan="3"
      >
        <RouterLink
          target="_blank"
          style="text-decoration: none"
          :to="`/account/${account.id}/view/`"
          class="text-blue-7 text-italic text-weight-regular"
          >{{ account.name }}</RouterLink
        >
      </td>
      <td></td>
      <td></td>
      <td></td>
      <td>{{ account.code }}</td>
      <td>{{ account.system_code }}</td>
      <td>{{ account.total_transactions }}</td>
    </tr>
  </template>
</template>

<script setup lang="ts">
import { PropType } from 'vue'

interface Account {
  id: number
  name: string
  code: string
  system_code: string | null
  category_id: number
  total_transactions: number
}

interface CategoryTree {
  id: number
  name: string
  children: CategoryTree[]
  code: string | null
  system_code: string | null
  total_transactions?: number
  accounts?: Account[]
  level?: number
  isExpandable?: boolean
}

defineEmits(['toggle-expand'])

const props = defineProps({
  row: {
    type: Object as PropType<CategoryTree>,
    required: true,
  },
  expandedRows: {
    type: Object as PropType<Record<number, boolean>>,
    required: true,
  },
  root: {
    type: Boolean,
    default: false,
  },
})
</script>
