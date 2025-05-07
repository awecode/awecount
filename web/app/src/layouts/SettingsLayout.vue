<script setup lang="ts">
const route = useRoute()
const activeCompany = computed(() => route.params.company as string)

const menuItems = computed(() => [
  {
    section: 'Basic',
    items: [
      {
        icon: 'business',
        label: 'General',
        to: `/${activeCompany.value}/settings`,
      },
      {
        icon: 'group',
        label: 'Members',
        to: `/${activeCompany.value}/settings/members`,
      },
      {
        icon: 'security',
        label: 'Permissions',
        to: `/${activeCompany.value}/settings/permissions`,
      },
      {
        icon: 'key',
        label: 'API Tokens',
        to: `/${activeCompany.value}/settings/api-tokens`,
      },
    ],
  },
  {
    section: 'Advanced',
    items: [
      {
        icon: 'inventory',
        label: 'Inventory Settings',
        to: `/${activeCompany.value}/settings/inventory`,
      },
      {
        icon: 'settings',
        label: 'Purchase Settings',
        to: `/${activeCompany.value}/settings/purchase`,
      },
      {
        icon: 'settings',
        label: 'Sales Settings',
        to: `/${activeCompany.value}/settings/sales`,
      },
      {
        icon: 'receipt_long',
        label: 'Quotation Settings',
        to: `/${activeCompany.value}/settings/quotation`,
      },
      {
        icon: 'receipt',
        label: 'Invoice Settings',
        to: `/${activeCompany.value}/settings/invoice`,
      },
    ],
  },
])
</script>

<template>
  <div class="row no-wrap">
    <!-- Sidebar -->
    <div class="bg-white" style="width: 240px; height: calc(100vh - 64px); border-right: 1px solid #e5e7eb">
      <div class="column full-height">
        <!-- Navigation Links -->
        <div class="q-px-md q-mt-md">
          <q-list>
            <template v-for="section in menuItems" :key="section.section">
              <div class="text-subtitle text-grey-7 q-mb-sm q-px-md">
                {{ section.section }}
              </div>

              <q-item
                v-for="item in section.items"
                :key="item.to"
                v-ripple
                clickable
                exact
                :to="item.to"
              >
                <q-item-section avatar>
                  <q-icon :name="item.icon" />
                </q-item-section>
                <q-item-section>{{ item.label }}</q-item-section>
              </q-item>

              <div class="q-mb-md"></div>
            </template>
          </q-list>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="col" style="height: calc(100vh - 64px); overflow-y: auto;">
      <div class="q-pa-md q-px-lg">
        <div class="row justify-start">
          <div class="col-12">
            <router-view />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-white {
  background: white;
}

/* Update active item style to match Plane */
:deep(.q-item.active) {
  color: var(--q-primary);
  background: #EEF2FF;
  font-weight: 500;
}

/* Reduce item padding */
:deep(.q-item) {
  padding: 8px 12px;
  min-height: 36px;
  border-radius: 4px;
  font-size: 14px;
}

/* Reduce avatar size */
:deep(.q-item__section--avatar) {
  min-width: 24px;
  padding-right: 12px;
}

/* Style for icons */
:deep(.q-icon) {
  font-size: 20px;
}
</style>
