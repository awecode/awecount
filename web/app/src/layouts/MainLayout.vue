<script setup lang="ts">
import type { EssentialLinkProps } from 'components/EssentialLink.vue'

import { $api } from 'src/composables/api'
import { useBreadcrumbItems } from 'src/composables/breadcrumb.js'
import { useAuthStore } from 'src/stores/auth'
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useLoginStore } from 'src/stores/login-info'

const route = useRoute()
const router = useRouter()

const miniState = ref(false)
const store = useLoginStore()

const companies = ref([])
const activeCompany = computed(() => route.params.company as string)

const { hasPermission, logout, hasAnyRole, switchCompany } = useAuthStore()

const fetchCompanies = async () => {
  try {
    companies.value = await $api('/api/me/companies/', { method: 'GET' })
  } catch (error) {
    console.error('Error fetching companies:', error)
  }
}

const essentialLinks: EssentialLinkProps[] = [
  {
    title: 'Dashboard',
    icon: 'mdi-view-dashboard',
    link: `/${activeCompany.value}/dashboard`,
  },
  {
    title: 'Inventory',
    icon: 'mdi-clipboard-outline',
    children: [
      {
        title: 'Items',
        icon: 'mdi-view-headline',
        link: `/${activeCompany.value}/inventory/items`,
        hide: !hasPermission('item'),
      },
      {
        title: 'Units',
        icon: 'mdi-scale-balance',
        link: `/${activeCompany.value}/inventory/units`,
        hide: !hasPermission('unit'),
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: `/${activeCompany.value}/inventory/categories`,
        hide: !hasPermission('category'),
      },
      {
        title: 'Brands',
        icon: 'mdi-domain',
        link: `/${activeCompany.value}/inventory/brands`,
        hide: !hasPermission('brand'),
      },
      {
        title: 'Inventory Ledger',
        icon: 'inventory',
        link: `/${activeCompany.value}/inventory/ledgers`,
        hide: !hasPermission('inventoryaccount'),
      },
      {
        title: 'Opening Stock',
        icon: 'edit_note',
        link: `/${activeCompany.value}/inventory/opening-stock`,
        hide: !hasPermission('accountopeningbalance'),
      },
      {
        title: 'Inventory Adjustment',
        icon: 'mdi-swap-horizontal',
        link: `/${activeCompany.value}/inventory/adjustments`,
        hide: !hasPermission('inventoryadjustmentvoucher'),
      },
      {
        title: 'Bill of Material',
        icon: 'mdi-receipt',
        link: `/${activeCompany.value}/inventory/bill-of-materials`,
        hide: !hasPermission('BillOfMaterialView'),
      },
      {
        title: 'Inventory Conversion',
        icon: 'mdi-shuffle-variant',
        link: `/${activeCompany.value}/inventory/conversions`,
        hide: !hasPermission('InventoryConversionVoucherView'),
      },
    ],
  },
  {
    title: 'Sales',
    icon: 'mdi-point-of-sale',
    children: [
      {
        title: 'Sales Invoices',
        icon: 'mdi-point-of-sale',
        link: `/${activeCompany.value}/sales/vouchers`,
        hide: !hasPermission('sales'),
      },
      {
        title: 'Credit Notes',
        icon: 'mdi-clipboard-arrow-down',
        link: `/${activeCompany.value}/sales/credit-notes`,
        hide: !hasPermission('creditnote'),
      },
      {
        title: 'Challans',
        icon: 'mdi-clipboard-arrow-right',
        link: `/${activeCompany.value}/sales/challans`,
        hide: !hasPermission('challan'),
      },
      {
        title: 'Payment Receipts',
        icon: 'mdi-receipt',
        link: `/${activeCompany.value}/payment-receipts`,
        hide: !hasPermission('paymentreceipt'),
      },
      {
        title: 'Sales Discounts',
        icon: 'mdi-sale',
        link: `/${activeCompany.value}/sales/discounts`,
        hide: !hasPermission('salesdiscount'),
      },
      {
        title: 'Sales Book',
        icon: 'mdi-book-open-page-variant',
        link: `/${activeCompany.value}/sales/sales-book`,
        hide: !hasPermission('sales'),
      },
      {
        title: 'Recurring Templates',
        icon: 'mdi-repeat',
        link: `/${activeCompany.value}/sales/vouchers/recurring-templates`,
        hide: !hasPermission('sales'),
      },
    ],
  },
  {
    title: 'Purchase',
    icon: 'local_mall',
    children: [
      {
        title: 'Purchases/Expenses',
        icon: 'shopping_cart',
        link: `/${activeCompany.value}/purchase/vouchers`,
        hide: !hasPermission('purchasevoucher'),
      },
      {
        title: 'Debit Notes',
        icon: 'mdi-clipboard-arrow-up',
        link: `/${activeCompany.value}/purchase/debit-notes`,
        hide: !hasPermission('debitnote'),
      },
      {
        title: 'Purchase Order',
        icon: 'mdi-clipboard-arrow-left',
        link: `/${activeCompany.value}/purchase/purchase-orders`,
        hide: !hasPermission('debitnote'),
      },
      {
        title: 'Purchase Discounts',
        icon: 'mdi-sale',
        link: `/${activeCompany.value}/purchase/discounts`,
        hide: !hasPermission('purchasediscount'),
      },
      {
        title: 'Purchase Book',
        icon: 'book',
        link: `/${activeCompany.value}/purchase/purchase-book`,
        hide: !hasPermission('purchasevoucher'),
      },
      {
        title: 'Recurring Templates',
        icon: 'mdi-repeat',
        link: `/${activeCompany.value}/purchase/vouchers/recurring-templates`,
        hide: !hasPermission('purchasevoucher'),
      },
    ],
  },
  {
    title: 'Accounts',
    icon: 'mdi-notebook-multiple',
    children: [
      {
        title: 'Ledgers',
        icon: 'mdi-book-open',
        link: `/${activeCompany.value}/account/ledgers`,
        hide: !hasPermission('accountledger'),
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: `/${activeCompany.value}/account/categories`,
        hide: !hasPermission('category'),
      },
      {
        title: 'Journal Vouchers',
        icon: 'mdi-book-plus',
        link: `/${activeCompany.value}/account/journal-vouchers`,
        hide: !hasPermission('journalvoucher'),
      },
      {
        title: 'Opening Balances',
        icon: 'mdi-cash',
        link: `/${activeCompany.value}/account/opening-balances`,
        hide: !hasPermission('accountopeningbalance'),
      },
    ],
  },
  {
    title: 'Reports',
    icon: 'mdi-file-chart',
    children: [
      {
        title: 'Categories Tree',
        icon: 'mdi-file-tree',
        link: `/${activeCompany.value}/reports/category-tree`,
        hide: !hasPermission('category'),
      },
      {
        title: 'Periodic Tax Summary',
        icon: 'mdi-currency-usd-off',
        link: `/${activeCompany.value}/reports/tax-summary`,
        hide: !hasPermission('taxpayment'),
      },
      {
        title: 'Collection Report',
        icon: 'mdi-receipt',
        link: `/${activeCompany.value}/reports/collection`,
      },
      {
        title: 'Trial Balance',
        icon: 'mdi-shuffle',
        link: `/${activeCompany.value}/reports/trial-balance`,
      },
      {
        title: 'Stock Trial Balance',
        icon: 'mdi-shuffle',
        link: `/${activeCompany.value}/reports/stock-trial-balance`,
      },
      {
        title: 'Income Statement',
        icon: 'mdi-chart-gantt',
        link: `/${activeCompany.value}/reports/income-statement`,
      },
      {
        title: 'Balance Sheet',
        icon: 'mdi-clipboard-text',
        link: `/${activeCompany.value}/reports/balance-sheet`,
      },
      {
        title: 'Ratio Analysis',
        icon: 'mdi-chart-arc',
        link: `/${activeCompany.value}/reports/ratio-analysis`,
      },
      {
        title: 'Transactions',
        icon: 'mdi-reorder-horizontal',
        link: `/${activeCompany.value}/reports/transactions`,
        hide: !hasPermission('transaction'),
      },
      {
        title: 'Day Book',
        icon: 'mdi-reorder-vertical',
        link: `/${activeCompany.value}/reports/day-book`,
        hide: !hasPermission('transaction'),
      },
      {
        title: 'Customer Ageing Report',
        icon: 'mdi-chart-gantt',
        link: `/${activeCompany.value}/reports/ageing-report`,
      },
      {
        title: 'Stock Movement',
        icon: 'mdi-chart-gantt',
        link: `/${activeCompany.value}/reports/stock-movement`,
      },
    ],
  },
  {
    title: 'Banks & Wallets',
    icon: 'mdi-bank',
    children: [
      {
        title: 'Bank Accounts',
        icon: 'mdi-bank',
        link: `/${activeCompany.value}/banking/bank-accounts`,
        hide: !hasPermission('bankaccount'),
      },
      {
        title: 'Cheque Issues',
        icon: 'mdi-checkbook',
        link: `/${activeCompany.value}/banking/cheque-issues`,
        hide: !hasPermission('chequeissue'),
      },
      {
        title: 'Cheque Deposits',
        icon: 'mdi-ballot',
        link: `/${activeCompany.value}/banking/cheque-deposits`,
        hide: !hasPermission('chequedeposit'),
      },
      {
        title: 'Cash Deposits',
        icon: 'mdi-cash',
        link: `/${activeCompany.value}/banking/cash-deposits`,
        hide: !hasPermission('bankcashdeposit'),
      },
      {
        title: 'Funds Transfers',
        icon: 'mdi-bank-transfer',
        link: `/${activeCompany.value}/banking/fund-transfers`,
        hide: !hasPermission('fundtransfer'),
      },
      {
        title: 'Reconciliation',
        icon: 'mdi-bank-transfer',
        link: `/${activeCompany.value}/banking/reconciliation`,
        hide: !hasPermission('fundtransfer'),
      },
    ],
  },
  {
    title: 'Taxes',
    icon: 'mdi-currency-usd-off',
    children: [
      {
        title: 'Tax Schemes',
        icon: 'mdi-file-percent',
        link: `/${activeCompany.value}/tax/schemes`,
        hide: !hasPermission('taxscheme'),
      },
      {
        title: 'Tax Payments',
        icon: 'mdi-cash-marker',
        link: `/${activeCompany.value}/tax/payments`,
        hide: !hasPermission('taxpayment'),
      },
      {
        title: 'Periodic Summary',
        icon: 'mdi-file-chart',
        link: `/${activeCompany.value}/reports/tax-summary`,
        hide: !hasPermission('taxpayment'),
      },
    ],
  },
  {
    title: 'CRM',
    icon: 'mdi-account-group',
    children: [
      {
        title: 'Parties',
        icon: 'mdi-account-group',
        link: `/${activeCompany.value}/crm/parties`,
        hide: !hasPermission('party'),
      },
      {
        title: 'Customers',
        icon: 'mdi-domain',
        link: `/${activeCompany.value}/crm/customers`,
        hide: !hasPermission('party'),
      },
      {
        title: 'Suppliers',
        icon: 'mdi-account',
        link: `/${activeCompany.value}/crm/suppliers`,
        hide: !hasPermission('party'),
      },
      {
        title: 'Sales Agent',
        icon: 'mdi-face-agent',
        link: `/${activeCompany.value}/sales/agents`,
        hide: !hasPermission('salesagent'),
      },
    ],
  },
  {
    title: 'Settings',
    icon: 'settings',
    children: [
      {
        title: 'Company Settings',
        icon: 'mdi-office-building-cog',
        link: `/${activeCompany.value}/settings/company`,
        hide: !hasAnyRole(['superuser', 'admin']),
      },
      {
        title: 'Audit Logs',
        icon: 'mdi-view-list',
        link: `/${activeCompany.value}/settings/audit-logs`,
        hide: !hasPermission('logentry'),
      },
      {
        title: 'Import/Export',
        icon: 'mdi-database-import',
        link: `/${activeCompany.value}/settings/import-export`,
        hide: !hasAnyRole(['superuser', 'admin']),
      },
      {
        title: 'Dashboard Widgets',
        icon: 'mdi-widgets',
        link: `/${activeCompany.value}/settings/dashboard-widgets`,
        hide: !hasPermission('widget'),
      },
      {
        title: 'Payment Modes',
        icon: 'mdi-cash',
        link: `/${activeCompany.value}/settings/payment-modes`,
        hide: !hasPermission('paymentmode'),
      },
      {
        title: 'Sales Settings',
        icon: 'mdi-point-of-sale',
        link: `/${activeCompany.value}/settings/sales`,
        hide: !hasPermission('salessetting'),
      },
      {
        title: 'Purchase Settings',
        icon: 'mdi-shopping',
        link: `/${activeCompany.value}/settings/purchase`,
        hide: !hasPermission('purchasesetting'),
      },
      {
        title: 'Inventory Settings',
        icon: 'mdi-calendar-multiple-check',
        link: `/${activeCompany.value}/settings/inventory`,
      },
      {
        title: 'Item Merge',
        icon: 'mdi-call-merge',
        link: `/${activeCompany.value}/settings/item-merge`,
      },
    ],
  },
  {
    title: 'POS',
    icon: 'mdi-cart-arrow-right',
    link: `/${activeCompany.value}/sales/pos`,
    hide: !hasPermission('SalesCreate') && !hasPermission('sales'),
  },
]

const leftDrawerOpen = ref(false)

// function toggleLeftDrawer() {
//   leftDrawerOpen.value = !leftDrawerOpen.value
// }

onMounted(() => {
  fetchCompanies()
})

const breadcrumbs = useBreadcrumbItems()
</script>

<template>
  <q-layout view="lHh Lpr lFf">
    <!-- <q-header elevated class="bg-grey-1 text-grey-9"> -->
    <q-header bordered class="bg-white text-grey-8 d-print-none print-hide q-py-xs">
      <q-toolbar>
        <q-btn
          dense
          flat
          round
          aria-label="Menu"
          icon="mdi-menu"
          @click="miniState = !miniState"
        />

        <q-toolbar-title class="flex items-center" style="gap: 16px">
          <RouterLink v-if="store.companyInfo?.logo_url" style="max-width: 60px; max-height: 40px" :to="`/${$route.params.company}/dashboard`">
            <img alt="Company Logo" style="max-width: 60px; max-height: 40px; object-fit: contain" :src="store.companyInfo.logo_url" />
          </RouterLink>
          <q-breadcrumbs class="gt-xs" gutter="sm">
            <q-breadcrumbs-el v-for="breadcrumb in breadcrumbs.slice(1)" :key="breadcrumb.to" v-bind="breadcrumb" />
            <!-- :class="breadCrums?.length - 1 === index cursor-pointer" -->
          </q-breadcrumbs>
        </q-toolbar-title>
        <div>
          <!-- <q-btn @click="confirmSignOut" square color="red" icon="power_settings_new" />
             -->
          <div class="row btns-Con">
            <q-btn class="gt-sm">
              {{ store.companyInfo?.current_fiscal_year }}
              <q-tooltip :delay="1000" :offset="[0, 10]">
                Fiscal Year
              </q-tooltip>
            </q-btn>
            <q-btn v-if="store.companyInfo?.config_template === 'np'" class="dateSwitcher bg-grey-7 text-grey-2" @click="store.isCalendarInAD = !store.isCalendarInAD">
              {{ activeDateFormat }}
              <q-tooltip :delay="1000" :offset="[0, 10]">
                Change Date Format
              </q-tooltip>
            </q-btn>

            <q-btn-dropdown flat>
              <template #label>
                <q-avatar size="32px">
                  <img src="https://cdn.quasar.dev/img/boy-avatar.png" />
                </q-avatar>
              </template>

              <q-list>
                <q-item v-close-popup clickable @click="router.push('/settings/profile')">
                  <q-item-section avatar>
                    <q-icon name="manage_accounts" />
                  </q-item-section>
                  <q-item-section>Manage Account</q-item-section>
                </q-item>

                <q-separator />

                <q-item v-close-popup clickable @click="logoutDiologueOpen = true">
                  <q-item-section avatar>
                    <q-icon name="logout" />
                  </q-item-section>
                  <q-item-section>Logout</q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
            <q-dialog v-model="logoutDiologueOpen">
              <q-card style="min-width: min(40vw, 450px)">
                <div style="margin: 20px 30px 10px">
                  <div class="text-h6 text-grey-9">
                    <span>Are you sure you want to logout?</span>
                  </div>
                  <div class="q-mb-md" style="margin-top: 40px">
                    <div class="text-right text-blue-6 row justify-end q-gutter-x-lg">
                      <q-btn
                        flat
                        class="text-grey-8"
                        label="Cancel"
                        @click="logoutDiologueOpen = false"
                      />
                      <q-btn
                        flat
                        class="text-red"
                        label="Yes"
                        @click="() => logout()"
                      />
                    </div>
                  </div>
                </div>
              </q-card>
            </q-dialog>
          </div>
        </div>
      </q-toolbar>
    </q-header>
    <q-drawer
      v-model="leftDrawerOpen"
      bordered
      drawer
      persistent
      show-if-above
      :mini="miniState"
    >
      <q-list class="icon-grey d-print-none print-hide">
        <q-btn-dropdown
          flat
          class="full-width q-pa-md"
          style="margin-top: 2px"
          :disable="miniState"
          :label="companies.find((c) => c.slug === activeCompany)?.name || 'Select Company'"
        >
          <q-list>
            <template v-for="company in companies" :key="company.slug">
              <q-item
                v-close-popup
                clickable
                :active="company.slug === activeCompany"
                @click="switchCompany(company.slug)"
              >
                <q-item-section avatar>
                  <q-avatar size="28px">
                    <img v-if="company.logo" :src="company.logo" />
                    <!-- <div v-else class="text-h6 text-white bg-primary flex items-center justify-center" style="width: 28px; height: 28px">
                      {{ company.name.split(' ').map((w) => w.charAt(0)).slice(0, 2).join('') }}
                    </div> -->
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ company.name }}</q-item-label>
                </q-item-section>
                <q-item-section v-if="company.slug === activeCompany" side>
                  <q-icon color="primary" name="check" />
                </q-item-section>
              </q-item>
            </template>

            <template v-if="hasAnyRole(['superuser', 'admin'])">
              <q-separator />

              <q-item v-close-popup clickable @click="router.push('/settings/company')">
                <q-item-section avatar>
                  <q-icon name="settings" />
                </q-item-section>
                <q-item-section>Company settings</q-item-section>
              </q-item>

              <q-item v-close-popup clickable @click="router.push('/settings/invite')">
                <q-item-section avatar>
                  <q-icon name="person_add" />
                </q-item-section>
                <q-item-section>Invite colleague or accountant</q-item-section>
              </q-item>

              <q-item v-close-popup clickable @click="router.push('/company/create/')">
                <q-item-section avatar>
                  <q-icon name="add" />
                </q-item-section>
                <q-item-section>Add company</q-item-section>
              </q-item>
            </template>
          </q-list>
        </q-btn-dropdown>

        <q-separator />

        <div class="q-mb-md"></div>
        <template v-for="link in essentialLinks" :key="link.title">
          <EssentialLink v-if="!link.hide" v-bind="link" />
        </template>
      </q-list>
    </q-drawer>
    <q-page-container>
      <!-- <template v-if="store.isLoading">
        <div class="absolute bg-white/80 h-screen w-full left-0 top-0 flex items-center justify-center text-black z-10">
          <q-spinner color="primary" size="3em" />
        </div>
      </template>
      <RouterView /> -->
      <div v-if="store.isLoading" class="relative">
        <div class="bg-white q-pa-lg -mt-2 transition-all absolute top-0 left-0 w-full h-full">
          <q-card class="mt-2">
            <q-skeleton square class="bg-green" height="64px" />
            <q-card class="q-mx-lg q-pt-md pb-8 px-3">
              <div class="grid lg:grid-cols-2 grid-cols-1 gap-y-12 gap-x-6 py-6">
                <div class="flex gap-4">
                  <div class="flex grow gap-1">
                    <q-skeleton class="grow" height="45px" type="rect" />
                    <q-skeleton
                      square
                      height="45px"
                      type="QBtn"
                      width="45px"
                    />
                  </div>
                  <q-skeleton
                    square
                    height="45px"
                    type="QBtn"
                    width="65px"
                  />
                </div>
                <q-skeleton height="45px" type="QInput" />
                <q-skeleton height="45px" type="QInput" />
                <q-skeleton height="45px" type="QInput" />
                <div class="flex gap-4">
                  <q-skeleton class="grow" height="45px" type="rect" />
                  <q-skeleton
                    square
                    height="45px"
                    type="QBtn"
                    width="65px"
                  />
                </div>
                <div></div>
                <q-skeleton height="45px" type="QInput" />
                <div></div>
              </div>
              <div class="pb-10">
                <q-card>
                  <q-card-section class="q-pa-lg">
                    <div class="pt-8 pb-6">
                      <hr class="h-[2px] bg-gray-300 b-0" />
                    </div>
                    <div class="grid grid-cols-12 gap-6">
                      <div class="flex grow gap-1 col-span-5">
                        <q-skeleton class="grow" height="45px" type="rect" />
                        <q-skeleton
                          square
                          height="45px"
                          type="QBtn"
                          width="45px"
                        />
                      </div>
                      <div class="col-span-2">
                        <q-skeleton height="45px" type="rect" />
                      </div>
                      <div class="col-span-2">
                        <q-skeleton height="45px" type="rect" />
                      </div>
                      <div class="col-span-2">
                        <q-skeleton height="45px" type="rect" />
                      </div>
                      <div class="col-span-1 grid grid-cols-2 gap-2">
                        <q-skeleton type="rect" />
                        <q-skeleton type="rect" />
                      </div>
                    </div>
                    <div class="sm:grid grid-cols-8 py-8">
                      <div class="col-span-5"></div>
                      <div class="col-span-3 grid grid-cols-2 gap-x-4">
                        <q-skeleton class="w-" height="30px" type="text" />
                        <q-skeleton class="w-" height="30px" type="text" />
                        <q-skeleton class="w-" height="30px" type="text" />
                        <q-skeleton class="w-" height="30px" type="text" />
                        <q-skeleton class="w-" height="30px" type="text" />
                        <q-skeleton class="w-" height="30px" type="text" />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="flex justify-right">
                <q-skeleton class="bg-green" height="36px" type="QBtn" />
              </div>
            </q-card>
          </q-card>
        </div>
      </div>
      <Suspense>
        <RouterView class="transition-all" :class="store.isLoading ? 'opacity-0' : ''" />
      </Suspense>
    </q-page-container>
  </q-layout>
</template>

<style scoped>
.icon-grey i {
  color: #757575;
}

.dateSwitcher {
  width: 40px;
}

.btns-Con {
  column-gap: 15px;
}

@media (min-width: 1000px) {
  .container-padding-left {
    padding-left: 60px;
  }
}
</style>
