<template>
  <tr>
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
      <td>
        <span v-if="newTotalObj.opening_cr"
          >{{ newTotalObj.opening_cr }} cr</span
        >
        <span v-else-if="newTotalObj.opening_dr"
          >{{ newTotalObj.opening_dr }} dr</span
        >
        <span v-else>0</span>
      </td>
      <td>
        {{ newTotalObj.transaction_dr }}
      </td>
      <td>
        {{ newTotalObj.transaction_cr }}
      </td>
      <td>
        <span>{{ calculateNet(newTotalObj, 'closing') }}</span>
      </td>
    </template>
    <template v-else>
      <td>
        <span v-if="showTotalObject.opening_cr"
          >{{ showTotalObject.opening_cr }} cr</span
        >
        <span v-else-if="showTotalObject.opening_dr"
          >{{ showTotalObject.opening_dr }} dr</span
        >
        <span v-else>0</span>
      </td>
      <td>
        {{ showTotalObject.transaction_dr }}
      </td>
      <td>
        {{ showTotalObject.transaction_cr }}
      </td>
      <td>
        <span v-if="showTotalObject.closing_cr"
          >{{ showTotalObject.closing_cr }} cr</span
        >
        <span v-else-if="showTotalObject.closing_dr"
          >{{ showTotalObject.closing_dr }} dr</span
        >
        <span v-else>0</span>
      </td>
    </template>
  </tr>
  <template v-if="activeObjectArray && activeObjectArray.length">
    <tr v-for="activeObject in activeObjectArray" :key="activeObject.id">
      <td>
        <span
          v-for="num in level + 1"
          :key="num"
          style="width: 20px; display: inline-block"
        ></span
        ><span class="text-blue-6">{{ activeObject.name }}</span>
      </td>
      <td v-if="activeObject">
        <span v-if="activeObject.opening_cr"
          >{{ activeObject.opening_cr }} cr</span
        >
        <span v-else-if="activeObject.opening_dr"
          >{{ activeObject.opening_dr }} dr</span
        >
        <span v-else>0</span>
      </td>
      <td v-else></td>
      <td>{{ activeObject.transaction_cr }}</td>
      <td>{{ activeObject.transaction_dr }}</td>
      <td>
        <span v-if="activeObject.closing_cr"
          >{{ activeObject.closing_cr }} cr</span
        >
        <span v-else-if="activeObject.closing_dr"
          >{{ activeObject.closing_dr }} dr</span
        >
        <span v-else>0</span>
      </td>
    </tr>
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
  },
  emits: ['updateTotal'],

  setup(props, { emit }) {
    const itemProps = ref({ ...props.item })
    const showTotalObject = ref({
      closing_cr: 0,
      closing_dr: 0,
      opening_cr: 0,
      opening_dr: 0,
      transaction_cr: 0,
      transaction_dr: 0,
    })
    const newTotalObj = ref({
      closing_cr: 0,
      closing_dr: 0,
      opening_cr: 0,
      opening_dr: 0,
      transaction_cr: 0,
      transaction_dr: 0,
    })
    const activeObjectArray = computed(() => {
      const activeArray = []
      showTotalObject.value = {
        closing_cr: 0,
        closing_dr: 0,
        opening_cr: 0,
        opening_dr: 0,
        transaction_cr: 0,
        transaction_dr: 0,
      }
      const accountArray = props.category_accounts[props.item.id]
      if (accountArray) {
        accountArray.forEach((item) => {
          const currentObj = props.accounts[item]
          activeArray.push(currentObj)
          ;[
            'closing_cr',
            'closing_dr',
            'opening_cr',
            'opening_dr',
            'transaction_cr',
            'transaction_dr',
          ].forEach((item) => {
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
      console.log('net', type)
      const net = parseFloat(
        (obj[`${type}` + '_cr'] - obj[`${type}` + '_dr']).toFixed(2)
      )
      console.log('net', net)
      if (net === 0) {
        return 0
      } else if (net > 0) {
        return `${net}` + ' cr'
      } else {
        return `${net}` + ' dr'
      }
    }
    watch(
      itemProps,
      (newValue) => {
        const computedTotal = {
          closing_cr: 0,
          closing_dr: 0,
          opening_cr: 0,
          opening_dr: 0,
          transaction_cr: 0,
          transaction_dr: 0,
        }
        newValue.children.forEach((item) => {
          if (item.total) {
            ;[
              'closing_cr',
              'closing_dr',
              'opening_cr',
              'opening_dr',
              'transaction_cr',
              'transaction_dr',
            ].forEach((field) => {
              computedTotal[field] += item.total[field] || 0
            })
          }
        })
        newTotalObj.value = computedTotal
        emit('updateTotal', computedTotal, props.index)
      },
      { deep: true }
    )
    return {
      props,
      itemProps,
      activeObject,
      activeObjectArray,
      onUpdateTotal,
      showTotalObject,
      newTotalObj,
      calculateNet,
    }
  },
}
</script>
