<script>
import { useLoginStore } from 'src/stores/login-info'

export default {
  props: {
    item: {
      type: Object,
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
    accounts: {
      type: Object,
      default: () => {
        return {}
      },
    },
    category_accounts: {
      type: Object,
      default: () => {
        return {}
      },
    },
    index: {
      type: [Number, null],
      default: null,
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
  },
  emits: ['updateTotal'],

  setup(props, { emit }) {
    const loginStore = useLoginStore()
    // const expandStatus = ref(true)
    const itemProps = ref({ ...props.item })
    const fieldsArray = ['closing_cr', 'closing_dr', 'opening_cr', 'opening_dr', 'transaction_cr', 'transaction_dr']
    const totalObjectFormat = {
      closing_cr: 0,
      closing_dr: 0,
      opening_cr: 0,
      opening_dr: 0,
      transaction_cr: 0,
      transaction_dr: 0,
    }
    const showTotalObject = ref(totalObjectFormat)
    const newTotalObj = ref(null)
    const activeObjectArray = computed(() => {
      const activeArray = []
      const UpdatedShowTotalObject = totalObjectFormat
      const accountArray = props.category_accounts[props.item.id]
      if (accountArray) {
        accountArray.forEach((item) => {
          const currentObj = props.accounts[item]
          activeArray.push(currentObj)
          fieldsArray.forEach((item) => {
            UpdatedShowTotalObject[item] = UpdatedShowTotalObject[item] + currentObj[item]
          })
          emit('updateTotal', UpdatedShowTotalObject, props.index)
          showTotalObject.value = { ...UpdatedShowTotalObject }
        })
      }
      return activeArray
    })
    const onUpdateTotal = (total, index) => {
      itemProps.value.children[index].total = total
    }
    const calculateNet = (obj, type) => {
      const net = Number.parseFloat((obj[`${type}` + '_cr'] - obj[`${type}` + '_dr']).toFixed(2))
      if (net === 0) {
        return 0
      } else if (net > 0) {
        return `${net}` + ' cr'
      } else {
        return `${net * -1}` + ' dr'
      }
    }
    // check zero trans status
    const checkZeroTrans = () => {
      if (newTotalObj.value) {
        return !!(newTotalObj.value.transaction_cr || newTotalObj.value.transaction_dr)
      } else if (showTotalObject.value) {
        return !!(showTotalObject.value.transaction_cr || showTotalObject.value.transaction_dr)
      } else {
        return true
      }
    }
    watch(
      [itemProps],
      (newValue) => {
        const computedTotal = {
          closing_cr: 0,
          closing_dr: 0,
          opening_cr: 0,
          opening_dr: 0,
          transaction_cr: 0,
          transaction_dr: 0,
        }
        newValue[0].children.forEach((item) => {
          if (item.total) {
            fieldsArray.forEach((field) => {
              computedTotal[field] += item.total[field] || 0
            })
          }
        })
        fieldsArray.forEach((field) => {
          computedTotal[field] += showTotalObject.value[field] || 0
        })
        newTotalObj.value = computedTotal
        emit('updateTotal', computedTotal, props.index)
      },
      { deep: true },
    )
    const changeExpandStatus = (id) => {
      const index = loginStore.trialBalanceCollapseId.indexOf(id)
      if (index >= 0) loginStore.trialBalanceCollapseId.splice(index, 1)
      else loginStore.trialBalanceCollapseId.push(id)
    }
    const expandStatus = computed(() => {
      const newTotalObjStatus = props.item.id && loginStore.trialBalanceCollapseId.includes(props.item.id)
      return !newTotalObjStatus
    })
    return {
      props,
      itemProps,
      activeObjectArray,
      onUpdateTotal,
      showTotalObject,
      newTotalObj,
      calculateNet,
      checkZeroTrans,
      expandStatus,
      changeExpandStatus,
      loginStore,
    }
  },
}
</script>

<template>
  <template v-if="!(props.config.hide_zero_transactions && !checkZeroTrans()) && !props.config.hide_categories">
    <tr v-if="newTotalObj" :class="expandAccountsProps ? '' : 'hidden'">
      <td class="text-blue-6" :class="props.root ? 'text-weight-bold' : ''">
        <span v-for="num in level" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span style="display: inline-block; width: 40px; margin-left: -5px">
          <q-btn
            dense
            flat
            round
            class="expand-btn"
            :class="expandStatus ? 'expanded' : ''"
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
          class="text-blue-6"
          style="text-decoration: none"
          target="_blank"
          :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${item.id}`"
        >
          {{ item.name }}
        </RouterLink>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{ newTotalObj.opening_dr }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ newTotalObj.opening_cr }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ calculateNet(newTotalObj, 'opening') }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">{{ calculateNet(newTotalObj, 'opening') }}</span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">
          {{ $nf(newTotalObj.transaction_dr) }}
        </span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">
          {{ $nf(newTotalObj.transaction_cr) }}
        </span>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{ $nf(newTotalObj.closing_dr) }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ $nf(newTotalObj.closing_cr) }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ calculateNet(newTotalObj, 'closing') }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">
          {{ calculateNet(newTotalObj, 'closing') }}
        </span>
      </td>
    </tr>
    <tr v-else-if="!!(showTotalObject.opening_cr || showTotalObject.opening_dr || showTotalObject.closing_cr || showTotalObject.closing_dr)" :class="expandAccountsProps ? '' : 'hidden'">
      <td class="text-blue-6">
        <span v-for="num in level" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span style="display: inline-block; width: 40px; margin-left: -5px">
          <q-btn
            dense
            flat
            round
            class="expand-btn"
            :class="expandStatus ? 'expanded' : ''"
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
          class="text-blue-6"
          style="text-decoration: none"
          target="_blank"
          :class="props.root ? 'text-weight-bold' : ''"
          :to="`/${$route.params.company}/account/ledgers/?has_balance=true&category=${item.id}`"
        >
          {{ item.name }}
        </RouterLink>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{ showTotalObject.opening_dr }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ showTotalObject.opening_cr }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ calculateNet(showTotalObject, 'opening') }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">{{ calculateNet(showTotalObject, 'opening') }}</span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">{{ $nf(showTotalObject.transaction_dr) }}</span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">{{ $nf(showTotalObject.transaction_cr) }}</span>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{ showTotalObject.closing_dr }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ showTotalObject.closing_cr }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{ calculateNet(showTotalObject, 'closing') }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">{{ calculateNet(showTotalObject, 'closing') }}</span>
      </td>
    </tr>
  </template>
  <template v-if="activeObjectArray && activeObjectArray.length && !props.config.hide_accounts">
    <template v-for="activeObject in activeObjectArray" :key="activeObject.id">
      <tr
        v-if="!(props.config.hide_zero_transactions && !(activeObject.transaction_dr || activeObject.transaction_cr))"
        :class="
          props.config.hide_categories ? ''
          : expandAccountsProps && expandStatus ? ''
            : 'hidden'
        "
      >
        <td class="text-blue-6 text-italic">
          <span v-if="!props.config.hide_categories">
            <span style="display: inline-block; width: 40px; margin-left: -5px"></span>
            <span v-for="num in level + 1" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
          </span>
          <RouterLink
            class="text-blue-7 text-italic text-weight-regular"
            style="text-decoration: none"
            target="_blank"
            :to="`/${$route.params.company}/account/ledgers/${activeObject.account_id}`"
          >
            {{ activeObject.name }}
          </RouterLink>
        </td>
        <template v-if="props.config.show_opening_closing_dr_cr">
          <td>{{ activeObject.opening_dr }}</td>
          <td>{{ activeObject.opening_cr }}</td>
          <td>{{ calculateNet(activeObject, 'opening') }}</td>
        </template>
        <td v-else>
          {{ calculateNet(activeObject, 'opening') }}
        </td>
        <td>{{ $nf(activeObject.transaction_dr) }}</td>
        <td>{{ $nf(activeObject.transaction_cr) }}</td>
        <template v-if="props.config.show_opening_closing_dr_cr">
          <td>{{ activeObject.closing_dr }}</td>
          <td>{{ activeObject.closing_cr }}</td>
          <td>{{ calculateNet(activeObject, 'closing') }}</td>
        </template>
        <td v-else>
          {{ calculateNet(activeObject, 'closing') }}
        </td>
      </tr>
    </template>
  </template>
  <template v-if="item.children && item.children.length">
    <TableNode
      v-for="(child, index) in item.children"
      :key="child.id"
      :accounts="props.accounts"
      :category_accounts="props.category_accounts"
      :config="props.config"
      :expand-accounts-props="expandAccountsProps && expandStatus"
      :index="index"
      :item="child"
      :level="props.level + 1"
      @update-total="onUpdateTotal"
    />
  </template>
</template>
