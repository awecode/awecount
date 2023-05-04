<template>
  <tr
    v-if="
      !(props.config.hide_zero_transactions && !checkZeroTrans()) &&
      !props.config.hide_categories
    "
  >
    <td>
      <span
        v-for="num in level"
        :key="num"
        style="width: 20px; display: inline-block"
      ></span
      ><span
        class="text-blue-6"
        :class="props.root ? 'text-weight-bold' : ''"
        >{{ item.name }}</span
      >
    </td>
    <template v-if="newTotalObj">
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
          {{ calculateNet(newTotalObj, 'closing') }}</span
        >
      </td>
    </template>
    <template v-else>
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
    </template>
  </tr>
  <template
    v-if="
      activeObjectArray &&
      activeObjectArray.length &&
      !props.config.hide_accounts
    "
  >
    <template v-for="activeObject in activeObjectArray" :key="activeObject.id">
      <tr
        v-if="
          !(
            props.config.hide_zero_transactions &&
            !(activeObject.transaction_dr || activeObject.transaction_cr)
          )
        "
      >
        <td>
          <span v-if="!props.config.hide_categories">
            <span
              v-for="num in level + 1"
              :key="num"
              style="width: 20px; display: inline-block"
            ></span></span
          ><span class="text-blue-6">{{ activeObject.name }}</span>
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
    <TableNode
      v-for="(child, index) in item.children"
      :key="child.id"
      :item="child"
      :index="index"
      :level="props.level + 1"
      :accounts="props.accounts"
      :category_accounts="props.category_accounts"
      @updateTotal="onUpdateTotal"
      :config="props.config"
    ></TableNode>
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
  },
  emits: ['updateTotal'],

  setup(props, { emit }) {
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
    }
  },
}
</script>
