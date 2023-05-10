<template>
  <!-- {{ props.expandAccountsProps }}--expandAccountsProps -->
  <!-- {{ expandStatus }} --expandstatus -->
  <template v-if="!(props.config.hide_zero_transactions && !checkZeroTrans()) &&
    !props.config.hide_categories
    ">
    <tr v-if="newTotalObj" :class="expandAccountsProps ? '' : 'hidden'">
      <!-- <td>{{ expandStatus }}--expandStatus</td> -->
      <td>
        <span v-for="num in level" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span style="display: inline-block; width: 40px; margin-left: -5px;">
          <q-btn class="expand-btn" dense flat :class="expandStatus ? 'expanded' : ''"
            @click="expandStatus = !expandStatus">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" class="text-grey-7">
              <path fill="currentColor" d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z" />
            </svg>
          </q-btn>
        </span>
        <RouterLink style="text-decoration: none" target="_blank" :to="`/account/?has_balance=true&category=${item.id}`"
          class="text-blue-6" :class="props.root ? 'text-weight-bold' : ''">{{ item.name }}</RouterLink>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{
            newTotalObj.opening_dr
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            newTotalObj.opening_cr
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            calculateNet(newTotalObj, 'opening')
          }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">{{
          calculateNet(newTotalObj, 'opening')
        }}</span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">
          {{ parseFloat(newTotalObj.transaction_dr.toFixed(2)) }}
        </span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">
          {{ parseFloat(newTotalObj.transaction_cr.toFixed(2)) }}
        </span>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{
            parseFloat(newTotalObj.closing_dr.toFixed(2))
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            parseFloat(newTotalObj.closing_cr.toFixed(2))
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            calculateNet(newTotalObj, 'closing')
          }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">
          {{ calculateNet(newTotalObj, 'closing') }}</span>
      </td>
    </tr>
    <tr v-else-if="!!(
      showTotalObject.opening_cr ||
      showTotalObject.opening_dr ||
      showTotalObject.closing_cr ||
      showTotalObject.closing_dr
    )
      " :class="expandAccountsProps ? '' : 'hidden'">
      <td>
        <!-- {{ expandAccountsProps && expandStatus }} -->
        <span v-for="num in level" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span style="display: inline-block; width: 40px; margin-left: -5px;">
          <q-btn class="expand-btn" dense flat :class="expandStatus ? 'expanded' : ''"
            @click="expandStatus = !expandStatus">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" class="text-grey-7">
              <path fill="currentColor" d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z" />
            </svg>
          </q-btn>
        </span>
        <RouterLink style="text-decoration: none" target="_blank" :to="`/account/?has_balance=true&category=${item.id}`"
          class="text-blue-6" :class="props.root ? 'text-weight-bold' : ''">{{ item.name }}</RouterLink>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{
            showTotalObject.opening_dr
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            showTotalObject.opening_cr
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            calculateNet(showTotalObject, 'opening')
          }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">{{
          calculateNet(showTotalObject, 'opening')
        }}</span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">{{
          parseFloat(showTotalObject.transaction_dr.toFixed(2))
        }}</span>
      </td>
      <td>
        <span v-if="!props.config.hide_sums">{{
          parseFloat(showTotalObject.transaction_cr.toFixed(2))
        }}</span>
      </td>
      <template v-if="props.config.show_opening_closing_dr_cr">
        <td>
          <span v-if="!props.config.hide_sums">{{
            showTotalObject.closing_dr
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            showTotalObject.closing_cr
          }}</span>
        </td>
        <td>
          <span v-if="!props.config.hide_sums">{{
            calculateNet(showTotalObject, 'closing')
          }}</span>
        </td>
      </template>
      <td v-else>
        <span v-if="!props.config.hide_sums">{{
          calculateNet(showTotalObject, 'closing')
        }}</span>
      </td>
    </tr>
  </template>
  <template v-if="activeObjectArray &&
      activeObjectArray.length &&
      !props.config.hide_accounts
      ">
    <template v-for="activeObject in activeObjectArray" :key="activeObject.id">
      <tr v-if="!(
        props.config.hide_zero_transactions &&
        !(activeObject.transaction_dr || activeObject.transaction_cr)
      )
        " :class="expandAccountsProps && expandStatus ? '' : 'hidden'">
        <td>
          <span v-if="!props.config.hide_categories">
            <span style="display: inline-block; width: 40px; margin-left: -5px;"></span>
            <!-- <span class="expand-btn" style="display: inline-block;">
            </span> -->
            <span v-for="num in level + 1" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span>
          <RouterLink target="_blank" style="text-decoration: none" :to="`/account/${activeObject.account_id}/view/`"
            class="text-blue-7 text-italic text-weight-regular">{{ activeObject.name }}</RouterLink>
        </td>
        <template v-if="props.config.show_opening_closing_dr_cr">
          <td>{{ activeObject.opening_dr }}</td>
          <td>{{ activeObject.opening_cr }}</td>
          <td>{{ calculateNet(activeObject, 'opening') }}</td>
        </template>
        <td v-else>
          {{ calculateNet(activeObject, 'opening') }}
        </td>
        <td>{{ parseFloat(activeObject.transaction_dr.toFixed(2)) }}</td>
        <td>{{ parseFloat(activeObject.transaction_cr.toFixed(2)) }}</td>
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
    <TableNode v-for="(child, index) in item.children" :key="child.id" :item="child" :index="index"
      :level="props.level + 1" :accounts="props.accounts" :category_accounts="props.category_accounts"
      @updateTotal="onUpdateTotal" :config="props.config" :expandAccountsProps="expandAccountsProps && expandStatus">
    </TableNode>
  </template>
</template>

<script>
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
      default: () => true
    }
  },
  emits: ['updateTotal'],

  setup(props, { emit }) {
    const expandStatus = ref(true)
    const itemProps = ref({ ...props.item })
    const fieldsArray = [
      'closing_cr',
      'closing_dr',
      'opening_cr',
      'opening_dr',
      'transaction_cr',
      'transaction_dr',
    ]
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
      showTotalObject.value = totalObjectFormat
      const accountArray = props.category_accounts[props.item.id]
      if (accountArray) {
        accountArray.forEach((item) => {
          const currentObj = props.accounts[item]
          activeArray.push(currentObj)
          fieldsArray.forEach((item) => {
            showTotalObject.value[item] =
              showTotalObject.value[item] + currentObj[item]
          })
          emit('updateTotal', showTotalObject.value, props.index)
        })
      }
      return activeArray
    })
    const activeObject = null
    const onUpdateTotal = (total, index) => {
      itemProps.value.children[index].total = total
    }
    const calculateNet = (obj, type) => {
      const net = parseFloat(
        (obj[`${type}` + '_cr'] - obj[`${type}` + '_dr']).toFixed(2)
      )
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
        return !!(
          newTotalObj.value.transaction_cr || newTotalObj.value.transaction_dr
        )
      } else if (showTotalObject.value) {
        return !!(
          showTotalObject.value.transaction_cr ||
          showTotalObject.value.transaction_dr
        )
      } else return true
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
      { deep: true }
    )
    // watch([newTotalObj, showTotalObject], () => {

    // })
    return {
      props,
      itemProps,
      activeObject,
      activeObjectArray,
      onUpdateTotal,
      showTotalObject,
      newTotalObj,
      calculateNet,
      checkZeroTrans,
      expandStatus,
    }
  },
}
</script>


<style lang="scss">
.expand-btn {
  position: relative;
  width: 35px;

  svg {
    transition: all 0.2s ease-in;
  }

  &.expanded {
    svg {
      transform: rotate(-90deg);
    }
  }

}
</style>