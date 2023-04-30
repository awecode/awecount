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
    <!-- <td>{{ category_accounts }}</td>
    <td>{{ activeObject }}</td> -->
    <td></td>
    <td></td>
    <td v-if="activeObject">
      <span v-if="activeObject.closing_cr"
        >{{ activeObject.closing_cr }} cr</span
      >
      <span v-else-if="activeObject.closing_dr"
        >{{ activeObject.closing_dr }} dr</span
      >
      <span v-else>0</span>
    </td>
    <td v-else></td>
  </tr>
  <tr v-if="activeObject">
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
    <!-- <td>{{ category_accounts }}</td>
    <td>{{ activeObject }}</td> -->
    <td>{{ activeObject.closing_cr || 0 - activeObject.opening_cr || 0 }}</td>
    <td>{{ activeObject.closing_dr || 0 - activeObject.opening_dr || 0 }}</td>
    <td>
      <span v-if="activeObject.cc">{{ activeObject.cc }} cr</span>
      <span v-else-if="activeObject.cd">{{ activeObject.cd }} dr</span>
      <span v-else>0</span>
    </td>
  </tr>
  <!-- {{ props.level }} --level -->
  <TableNode
    v-for="child in item.children"
    :key="child.id"
    :item="child"
    :level="props.level + 1"
    :accounts="props.accounts"
    :category_accounts="props.category_accounts"
  ></TableNode>
  <!-- {{ props }} --props -->
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
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const activeObject = computed(
      () => props.accounts[props.category_accounts[props.item.id]]
    )
    const totalObject = ref({
      oc: 0,
      od: 0,
      cc: 0,
      cd: 0,
    })

    return {
      props,
      activeObject,
    }
  },
}
</script>
