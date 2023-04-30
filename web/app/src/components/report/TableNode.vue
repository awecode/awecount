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
    <td>
      <span v-if="showTotalObject.opening_cr"
        >{{ showTotalObject.opening_cr }} cr</span
      >
      <span v-else-if="showTotalObject.opening_dr"
        >{{ showTotalObject.opening_dr }} dr</span
      >
      <span v-else>0</span>
    </td>
    <td></td>
    <td></td>
    <td>
      <span v-if="showTotalObject.closing_cr"
        >{{ showTotalObject.closing_cr }} cr</span
      >
      <span v-else-if="showTotalObject.closing_dr"
        >{{ showTotalObject.closing_dr }} dr</span
      >
      <span v-else>0</span>
    </td>
    {{
      propagateTotalObject
    }}
    --totalobj
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
      <td>{{ activeObject.closing_cr || 0 - activeObject.opening_cr || 0 }}</td>
      <td>{{ activeObject.closing_dr || 0 - activeObject.opening_dr || 0 }}</td>
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
      v-for="child in item.children"
      :key="child.id"
      :item="child"
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
  },
  emits: ['updateTotal'],

  setup(props, { emit }) {
    const propagateTotalObject = ref({})
    const showTotalObject = ref({
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
          emit('updateTotal', showTotalObject.value)
        })
      }
      return activeArray
    })
    const activeObject = null
    // TODO: remove
    // watch(
    //   () => activeObjectArray.value,
    //   () => {
    //     // console.log('activeObjectArray updated', activeObjectArray.value)
    //     activeObjectArray.value.forEach((currentObj) => {
    //       console.log('currentObj', currentObj)
    //       ;[
    //         'closing_cr',
    //         'closing_dr',
    //         'opening_cr',
    //         'opening_dr',
    //         'transaction_cr',
    //         'transaction_dr',
    //       ].forEach((item) => {
    //         showTotalObject.value[item] =
    //           showTotalObject.value[item] + currentObj[item]
    //       })
    //     })
    //     emit('updateTotal', showTotalObject.value)
    //   }
    // )
    // to calculate Totals
    // watch(
    //   () => activeObjectArray,
    //   () => {
    //     console.log('value mutated')
    //     // if (activeObjectArray.value && activeObjectArray.value.length) {
    //     //   console.log('abloyt to emit')
    //     //   activeObjectArray.value.forEach((obj) => {
    //     //     ;[
    //     //       'closing_cr',
    //     //       'closing_dr',
    //     //       'opening_cr',
    //     //       'opening_dr',
    //     //       'transaction_cr',
    //     //       'transaction_dr',
    //     //     ].forEach((item) => {
    //     //       totalObject.value[item] = totalObject.value[item] + obj[item]
    //     //     })
    //     //   })
    //     //   emit('updateTotal', totalObject.value)
    //     // }
    //   },
    //   {
    //     deep: true,
    //   }
    // )
    // to calculate Totals
    const onUpdateTotal = (total) => {
      console.log('total updated', total)
      const loppArr = [
        ('closing_cr',
        'closing_dr',
        'opening_cr',
        'opening_dr',
        'transaction_cr',
        'transaction_dr'),
      ]
      // propagateTotalObject.value = {
      //   closing_cr: 0,
      //   closing_dr: 0,
      //   opening_cr: 0,
      //   opening_dr: 0,
      //   transaction_cr: 0,
      //   transaction_dr: 0,
      // }
      loppArr.forEach((item) => {
        propagateTotalObject.value[item] =
          propagateTotalObject.value[item] + total[item]
      })
      emit('updateTotal', propagateTotalObject.value)
    }
    return {
      props,
      activeObject,
      // TODO: remove
      activeObjectArray,
      propagateTotalObject,
      onUpdateTotal,
      showTotalObject,
    }
  },
}
</script>
