<script setup lang="ts">
export interface EssentialLinkProps {
  title: string
  caption?: string
  link?: string
  icon?: string
  children?: EssentialLinkProps[]
  level?: number
  hide?: boolean
}

const props = withDefaults(defineProps<EssentialLinkProps>(), {
  caption: '',
  link: '#',
  icon: '',
  level: 0,
})

const hideParent = ref(false)

if (props.level === 0 && props.children && props.children.length > 0) {
  const hideStatus = props.children.some(child => !child.hide)
  if (!hideStatus) hideParent.value = true
} else {
  hideParent.value = false
}
</script>

<template>
  <q-expansion-item v-if="children && !hideParent" :icon="icon || 'menu_open'" :label="title">
    <template v-for="child in children" :key="child.title">
      <EssentialLink
        v-if="!child.hide"
        :level="level + 1"
        v-bind="child"
        :style="`padding-left:${level * 2 + 3}em !important`"
      />
    </template>
  </q-expansion-item>
  <!-- <q-item v-else clickable :to="link" :style="style"> -->
  <q-item v-else-if="!hideParent" clickable :to="link">
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
      <q-item-label caption>
        {{ caption }}
      </q-item-label>
    </q-item-section>
  </q-item>
</template>
