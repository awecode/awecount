<script setup lang="ts">
import type { PropType } from 'vue'
import { useLoginStore } from 'src/stores/login-info'

interface Account {
  id: number
  name: string
  transaction_data: Transaction[]
}
interface Item {
  id: number
  name?: string
  code?: string
  children: Item[]
  system_code?: string | null
  accounts?: Account[]
  total: { closing_dr: number, closing_cr: number }[]
}
const props = defineProps({
  item: {
    type: Object as PropType<Item>,
    default: () => {
      return {}
    },
  },
  root: {
    type: Boolean,
    default: () => false,
  },
  level: {
    type: Number,
    default: () => 0,
  },
  index: {
    type: Number,
    default: () => null,
  },
  config: {
    type: Object,
    default: () => {
      return {}
    },
  },
  expandAccountsProps: {
    type: Boolean,
    default: () => true,
  },
  isBalanceSheet: {
    type: Boolean,
    default: () => false,
  },
  parent: {
    type: Object,
    default: () => {
      return {}
    },
  },
  unlinkParent: {
    type: Boolean,
    default: () => false,
  },
  name: {
    type: String,
    default: () => '',
  },
  hideEmptyCategories: {
    type: Boolean,
    default: () => true,
  },
})
const loginStore = useLoginStore()
interface Transaction {
  closing_cr: number
  closing_dr: number
}
const calculateBalance = (obj: Transaction) => {
  const net = obj.closing_cr - obj.closing_dr
  if (net === 0) {
    return 0
  } else if (net > 0) {
    return `${net.toFixed(2)}` + ' cr'
  } else {
    return `${(net * -1).toFixed(2)}` + ' dr'
  }
}
const hasNoBalance = (account: Account) => {
  return account.transaction_data?.every(obj => obj.closing_cr - obj.closing_dr === 0)
}
// // check zero trans status
const hasZeroBalance = () => {
  if (props.item?.children?.length) {
    return props.item.total?.every((obj: Transaction) => obj.closing_cr - obj.closing_dr === 0)
  } else {
    return props.item.accounts?.every((account: Account) => hasNoBalance(account))
  }
}
const changeExpandStatus = (id: number) => {
  if (props.isBalanceSheet) {
    const index = loginStore.balanceSheetCollapseId.indexOf(id)
    if (index >= 0) loginStore.balanceSheetCollapseId.splice(index, 1)
    else loginStore.balanceSheetCollapseId.push(id)
  } else {
    const index = loginStore.incomeStatementCollapseId.indexOf(id)
    if (index >= 0) loginStore.incomeStatementCollapseId.splice(index, 1)
    else loginStore.incomeStatementCollapseId.push(id)
  }
}
const expandStatus = computed(() => {
  let newTotalArrayStatus = false
  if (props.isBalanceSheet) {
    newTotalArrayStatus = props.item.id && loginStore.balanceSheetCollapseId.includes(props.item.id)
  } else {
    newTotalArrayStatus = props.item.id && loginStore.incomeStatementCollapseId.includes(props.item.id)
  }
  return !newTotalArrayStatus
})
</script>

<template>
  <template v-if="(!config.hide_categories && (item.children.length || item.accounts?.length) && !(hideEmptyCategories && hasZeroBalance())) || name">
    <tr :class="{ hidden: !expandAccountsProps }">
      <td class="text-blue-6" :class="props.root ? 'text-weight-bold bg-green-500' : ''">
        <span v-for="num in level" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span style="display: inline-block; width: 40px; margin-left: -5px">
          <q-btn
            dense
            flat
            round
            class="expand-btn"
            :class="expandStatus ? 'rotate-90' : ''"
            @click="changeExpandStatus(item.id)"
          >
            <svg
              class="text-grey-7"
              height="32"
              viewBox="0 0 24 24"
              width="32"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z" fill="currentColor" />
            </svg>
          </q-btn>
        </span>
        <RouterLink
          v-if="!unlinkParent"
          class="text-blue-6"
          style="text-decoration: none"
          target="_blank"
          :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${item.id}`"
        >
          {{ name || item.name }}
        </RouterLink>
        <span v-else class="text-gray-800">
          {{ name || item.name }}
        </span>
      </td>

      <td v-for="(transaction, index) in item.total" :key="index">
        <span v-if="!props.config.hide_sums">
          {{ calculateBalance(transaction) }}
        </span>
      </td>
    </tr>
  </template>
  <slot v-if="expandAccountsProps && expandStatus" name="custom"></slot>

  <template v-if="item.accounts && item.accounts.length && !props.config.hide_accounts && (!props.config.hide_zero_balance || !hasZeroBalance())">
    <template v-for="account in item.accounts" :key="account.id">
      <tr v-if="!(props.config.hide_zero_balance && hasNoBalance(account))" :class="expandAccountsProps && expandStatus ? '' : 'hidden'">
        <td class="text-blue-6 text-italic">
          <span>
            <span style="display: inline-block; width: 40px; margin-left: -5px"></span>
            <span v-for="num in level + 1" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
          </span>
          <RouterLink
            class="text-blue-7 text-italic text-weight-regular"
            style="text-decoration: none"
            target="_blank"
            :to="`/account/${account.id}/view/`"
          >
            {{ account.name }}
          </RouterLink>
        </td>

        <td v-for="(transaction, index) in account.transaction_data" :key="index">
          {{ calculateBalance(transaction) }}
        </td>
      </tr>
    </template>
  </template>

  <template v-if="item.children && item.children.length">
    <AccountBalanceTableNode
      v-for="(child, index) in item.children"
      :key="child.id"
      :config="props.config"
      :expand-accounts-props="expandAccountsProps && expandStatus"
      :hide-empty-categories="hideEmptyCategories"
      :index="index"
      :item="child"
      :level="props.level + 1"
      :parent="item"
    />
  </template>
</template>

<style scoped>
/* write in css */
.expand-btn {
  width: 20px;
}
</style>
