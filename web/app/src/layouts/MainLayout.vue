<script setup lang="ts">
import type { EssentialLinkProps } from 'components/EssentialLink.vue'
import type { Ref } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useLoginStore } from '../stores/login-info.js'

const miniState = ref(false)
const router = useRouter()
const route = useRoute()
const breadCrumbs: Ref<Array<string | null>> = ref([])
const store = useLoginStore()
// const router = useRouter()
const activeDateFormat = computed(() => (store.isCalendarInAD ? 'AD' : 'BS'))
const logoutDiologueOpen = ref(false)

const { hasPermission, logout } = useAuthStore()

const essentialLinks: EssentialLinkProps[] = [
  {
    title: 'Dashboard',
    icon: 'mdi-view-dashboard',
    link: '/dashboard/',
  },
  {
    title: 'Items',
    icon: 'mdi-clipboard-outline',
    children: [
      {
        title: 'All Items',
        icon: 'mdi-view-headline',
        link: '/items/list/',
        hide: !hasPermission('item'),
      },
      {
        title: 'Units',
        icon: 'mdi-scale-balance',
        link: '/units/list/',
        hide: !hasPermission('unit'),
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: '/inventory-category/list/',
        hide: !hasPermission('category'),
      },
      {
        title: 'Brands',
        icon: 'mdi-domain',
        link: '/brand/list/',
        hide: !hasPermission('brand'),
      },
      {
        title: 'Inventory Ledger',
        icon: 'inventory',
        link: '/inventory-account/list/',
        hide: !hasPermission('inventoryaccount'),
      },
      {
        title: 'Opening Stock',
        icon: 'edit_note',
        link: '/items/opening/',
        hide: !hasPermission('accountopeningbalance'),
      },
      {
        title: 'Inventory Adjustment',
        icon: 'mdi-swap-horizontal',
        link: '/items/inventory-adjustment/list',
        hide: !hasPermission('inventoryadjustmentvoucher'),
      },
      // {
      //   title: 'Bill of Material',
      //   icon: 'mdi-receipt',
      //   link: '/items/bill-of-material/list',
      //   hide: !hasPermission('BillOfMaterialView')
      // },
      // {
      //   title: 'Inventory Conversion',
      //   icon: 'mdi-shuffle-variant',
      //   link: '/items/inventory-conversion/list',
      //   hide: !hasPermission('InventoryConversionVoucherView')
      // },
    ],
  },
  // {
  //   title: 'Books',
  //   icon: 'mdi-library',
  //   link: '/book/list/',
  // },
  {
    title: 'Sales',
    icon: 'mdi-point-of-sale',
    children: [
      {
        title: 'Sales Invoices',
        icon: 'mdi-point-of-sale',
        link: '/sales-voucher/list/',
        hide: !hasPermission('sales'),
      },
      {
        title: 'Credit Notes',
        icon: 'mdi-clipboard-arrow-down',
        link: '/credit-note/list/',
        hide: !hasPermission('creditnote'),
      },
      {
        title: 'Challans',
        icon: 'mdi-clipboard-arrow-right',
        link: '/challan/list/',
        hide: !hasPermission('challan'),
      },
      {
        title: 'Payment Receipts',
        icon: 'mdi-receipt',
        link: '/payment-receipt/list/',
        hide: !hasPermission('paymentreceipt'),
      },
      {
        title: 'Sales Discounts',
        icon: 'mdi-sale',
        link: '/sales-discount/list/',
        hide: !hasPermission('salesdiscount'),
      },
      {
        title: 'Sales Report',
        icon: 'mdi-format-list-bulleted',
        link: '/sales-row/list/',
        hide: !hasPermission('sales'),
      },
      {
        title: 'Sales Book',
        icon: 'mdi-book',
        link: '/sales-book/list/',
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
        link: '/purchase-voucher/list/',
        hide: !hasPermission('purchasevoucher'),
      },
      {
        title: 'Debit Notes',
        icon: 'mdi-clipboard-arrow-up',
        link: '/debit-note/list/',
        hide: !hasPermission('debitnote'),
      },
      {
        title: 'Purchase Order',
        icon: 'mdi-clipboard-arrow-left',
        link: '/purchase-order/list/',
        hide: !hasPermission('debitnote'),
      },
      {
        title: 'Purchase Discounts',
        icon: 'mdi-sale',
        link: '/purchase-discount/list/',
        hide: !hasPermission('purchasediscount'),
      },
      {
        title: 'Purchase Report',
        icon: 'mdi-format-list-bulleted',
        link: '/purchase-voucher-row/list/',
        hide: !hasPermission('purchasevoucher'),
      },
      {
        title: 'Purchase Book',
        icon: 'book',
        link: '/purchase-book/list/',
        hide: !hasPermission('purchasevoucher'),
      },
    ],
  },
  {
    title: 'Accounts',
    icon: 'mdi-notebook-multiple',
    children: [
      {
        title: 'Ledger',
        icon: 'mdi-notebook-multiple',
        link: '/account/?has_balance=true',
        hide: !hasPermission('account'),
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: '/account-category/list',
        hide: !hasPermission('category'),
      },
      {
        title: 'Journal Vouchers',
        icon: 'mdi-shuffle',
        link: '/journal-voucher/',
        hide: !hasPermission('journalvoucher'),
      },
      {
        title: 'All Accounts',
        icon: 'mdi-notebook-multiple',
        link: '/account/',
        hide: !hasPermission('account'),
      },
      {
        title: 'Opening Balances',
        icon: 'mdi-cash',
        link: '/account-opening-balance/',
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
        link: '/report/category-tree/',
        hide: !hasPermission('category'),
      },
      {
        title: 'Sales By Category',
        icon: 'mdi-shape',
        link: '/report/sales-by-category/',
      },
      {
        title: 'Periodic Tax Summary',
        icon: 'mdi-currency-usd-off',
        link: '/report/tax-summary/',
        hide: !hasPermission('taxpayment'),
      },
      {
        title: 'Collection Report',
        icon: 'mdi-receipt',
        link: '/report/collection-report/',
      },
      {
        title: 'Trial Balance',
        icon: 'mdi-shuffle',
        link: '/report/trial-balance/',
      },
      {
        title: 'Stock Trial Balance',
        icon: 'mdi-shuffle',
        link: '/report/stock-trial-balance/',
      },
      // {
      //   title: 'Income Statement',
      //   icon: 'mdi-chart-gantt',
      //   link: '/report/income-statement/',
      // },
      // {
      //   title: 'Balance Sheet',
      //   icon: 'mdi-clipboard-text',
      //   link: '/report/balance-sheet/',
      // },
      // {
      //   title: 'Ratio Analysis',
      //   icon: 'mdi-chart-arc',
      //   link: '/report/ratio-analysis/',
      // },
      {
        title: 'Transactions',
        icon: 'mdi-reorder-horizontal',
        link: '/report/transactions/',
        hide: !hasPermission('transaction'),
      },
      {
        title: 'Day Book',
        icon: 'mdi-reorder-vertical',
        link: '/report/day-book/',
        hide: !hasPermission('transaction'),
      },
      {
        title: 'Customer Ageing Report',
        icon: 'mdi-chart-gantt',
        link: '/report/ageing-report/',
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
        link: '/bank-accounts/list/',
        hide: !hasPermission('bankaccount'),
      },
      {
        title: 'Cheque Issues',
        icon: 'mdi-checkbook',
        link: '/cheque-issue/list/',
        hide: !hasPermission('chequeissue'),
      },
      {
        title: 'Cheque Deposits',
        icon: 'mdi-ballot',
        link: '/cheque-deposit/list/',
        hide: !hasPermission('chequedeposit'),
      },
      {
        title: 'Cash Deposits',
        icon: 'mdi-cash',
        link: '/cash-deposit/list/',
        hide: !hasPermission('bankcashdeposit'),
      },
      {
        title: 'Funds Transfers',
        icon: 'mdi-bank-transfer',
        link: '/fund-transfer/list/',
        hide: !hasPermission('fundtransfer'),
      },
    ],
  },
  {
    title: 'Taxes',
    caption: 'Bank',
    icon: 'mdi-currency-usd-off',
    children: [
      {
        title: 'Tax Schemes',
        icon: 'mdi-file-percent',
        link: '/taxes/list/',
        hide: !hasPermission('taxscheme'),
      },
      {
        title: 'Tax Payments',
        icon: 'mdi-cash-marker',
        link: '/tax-payment/list/',
        hide: !hasPermission('taxpayment'),
      },
      {
        title: 'Periodic Summary',
        icon: 'mdi-file-chart',
        link: '/report/tax-summary/',
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
        link: '/party/list/',
        hide: !hasPermission('party'),
      },
      {
        title: 'Customers',
        icon: 'mdi-domain',
        link: '/parties/customers/',
        hide: !hasPermission('party'),
      },
      {
        title: 'Suppliers',
        icon: 'mdi-account',
        link: '/parties/suppliers/',
        hide: !hasPermission('party'),
      },
      {
        title: 'Sales Agent',
        icon: 'mdi-face-agent',
        link: '/sales-agent/list/',
        hide: !hasPermission('salesagent'),
      },
    ],
  },
  {
    title: 'Settings',
    icon: 'settings',
    children: [
      {
        title: 'Audit Logs',
        icon: 'mdi-view-list',
        link: '/audit-log/list/',
        hide: !hasPermission('logentry'),
      },
      {
        title: 'Import/Exports',
        icon: 'mdi-database-import',
        link: '/settings/import-export/',
      },
      {
        title: 'Dashboard Widgets',
        icon: 'mdi-widgets',
        link: '/dashboard-widgets/list/',
        hide: !hasPermission('widget'),
      },
      {
        title: 'Payment Modes',
        icon: 'mdi-cash',
        link: '/settings/payment-mode/list/',
        hide: !hasPermission('paymentmode'),
      },
      {
        title: 'Sales Settings',
        icon: 'mdi-point-of-sale',
        link: '/settings/sales/',
        hide: !hasPermission('salessetting'),
      },
      {
        title: 'Purchase Settings',
        icon: 'mdi-shopping',
        link: '/settings/purchase/',
        hide: !hasPermission('purchasesetting'),
      },
      {
        title: 'Inventory Settings',
        icon: 'mdi-calendar-multiple-check',
        link: '/settings/inventory-settings/',
      },
      {
        title: 'Account Closing',
        icon: 'mdi-calendar-multiple-check',
        link: '/settings/account-closing/',
        hide: !hasPermission('AccountClosingCreate'),
      },
      {
        title: 'Item Merge',
        icon: 'mdi-call-merge',
        link: '/settings/item-merge/',
        // hide: !hasPermission('AccountClosingCreate')
      },
    ],
  },
  {
    title: 'POS ',
    icon: 'mdi-cart-arrow-right',
    link: '/pos',
    hide: !hasPermission('SalesCreate') && !hasPermission('sales'),
  },

  // {
  //   title: 'Reset Password',
  //   icon: 'key',
  //   link: '/reset-password/',
  // },
  // {
  //   title: 'Sign Out',
  //   icon: 'power_settings_new',
  //   link: '/login/',
  // },
]

const leftDrawerOpen = ref(false)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

onMounted(() => {
  breadCrumbs.value = route.meta.breadcrumb
})
watch(route, () => {
  breadCrumbs.value = route.meta.breadcrumb
})
</script>

<template>
  <q-layout view="lHh Lpr lFf" class="container-padding-left">
    <!-- <q-header elevated class="bg-grey-1 text-grey-9"> -->
    <q-header bordered class="bg-white text-grey-8 d-print-none print-hide">
      <q-toolbar>
        <q-btn flat dense round icon="mdi-menu" aria-label="Menu" @click="miniState = !miniState" />
        <q-toolbar-title class="flex items-center" style="gap: 16px">
          <RouterLink v-if="store.companyInfo?.logo_url" to="/" style="max-width: 60px; max-height: 40px">
            <img style="max-width: 60px; max-height: 40px; object-fit: contain" :src="store.companyInfo.logo_url" alt="Company Logo" />
          </RouterLink>
          <q-breadcrumbs class="gt-xs" gutter="sm">
            <q-breadcrumbs-el v-for="breadCrum in breadCrumbs" :key="breadCrum" :label="breadCrum" :to="{ name: breadCrum }" />
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
                Fiscal Yaar
              </q-tooltip>
            </q-btn>
            <q-btn v-if="store.companyInfo?.config_template === 'np'" class="dateSwitcher bg-grey-7 text-grey-2" @click="store.isCalendarInAD = !store.isCalendarInAD">
              {{ activeDateFormat }}
              <q-tooltip :delay="1000" :offset="[0, 10]">
                Change Date Format
              </q-tooltip>
            </q-btn>
            <a target="_blank" href="https://docs.awecount.com/" style="color: inherit">
              <q-btn class="gt-sm">
                <q-icon name="mdi-help-circle-outline" />
                <q-tooltip :delay="1000" :offset="[0, 10]">Help</q-tooltip>
              </q-btn>
            </a>
            <q-btn @click="logoutDiologueOpen = true">
              <q-icon name="mdi-logout" />
              <q-tooltip :delay="1000" :offset="[0, 10]">
                Logout
              </q-tooltip>
            </q-btn>
            <q-dialog v-model="logoutDiologueOpen">
              <q-card style="min-width: min(40vw, 450px)">
                <div style="margin: 20px 30px 10px">
                  <div class="text-h6 text-grey-9">
                    <span>Are you sure you want to logout?</span>
                  </div>
                  <div class="q-mb-md" style="margin-top: 40px">
                    <div class="text-right text-blue-6 row justify-end q-gutter-x-lg">
                      <q-btn flat label="Cancel" class="text-grey-8" @click="logoutDiologueOpen = false" />
                      <q-btn flat label="Yes" class="text-red" @click="() => logout()" />
                    </div>
                  </div>
                </div>
              </q-card>
            </q-dialog>
          </div>
        </div>
        <!-- <div>ERP v{{ $q.version }}</div> -->
      </q-toolbar>
    </q-header>
    <q-drawer v-model="leftDrawerOpen" drawer persistent bordered="" show-if-above :mini="miniState">
      <q-list class="icon-grey d-print-none print-hide">
        <!-- <q-item-label header> Menu </q-item-label> -->
        <!-- <q-img src="../assets/background-image.png" style="height: 90px">
            <div class="absolute-bottom bg-transparent text-black">
              <div class="text-weight-bold text-h6 text-grey-10">{{ store.username }}</div>
            </div>
          </q-img> -->

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
            <q-skeleton height="64px" square class="bg-green" />
            <q-card class="q-mx-lg q-pt-md pb-8 px-3">
              <div class="grid lg:grid-cols-2 grid-cols-1 gap-y-12 gap-x-6 py-6">
                <div class="flex gap-4">
                  <div class="flex grow gap-1">
                    <q-skeleton height="45px" type="rect" class="grow" />
                    <q-skeleton height="45px" width="45px" type="QBtn" square />
                  </div>
                  <q-skeleton height="45px" width="65px" type="QBtn" square />
                </div>
                <q-skeleton height="45px" type="QInput" />
                <q-skeleton height="45px" type="QInput" />
                <q-skeleton height="45px" type="QInput" />
                <div class="flex gap-4">
                  <q-skeleton height="45px" type="rect" class="grow" />
                  <q-skeleton height="45px" width="65px" type="QBtn" square />
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
                        <q-skeleton height="45px" type="rect" class="grow" />
                        <q-skeleton height="45px" width="45px" type="QBtn" square />
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
                        <q-skeleton type="text" height="30px" class="w-" />
                        <q-skeleton type="text" height="30px" class="w-" />
                        <q-skeleton type="text" height="30px" class="w-" />
                        <q-skeleton type="text" height="30px" class="w-" />
                        <q-skeleton type="text" height="30px" class="w-" />
                        <q-skeleton type="text" height="30px" class="w-" />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="flex justify-right">
                <q-skeleton type="QBtn" class="bg-green" height="36px" />
              </div>
            </q-card>
          </q-card>
        </div>
      </div>
      <Suspense>
        <RouterView :class="store.isLoading ? 'opacity-0' : ''" class="transition-all" />
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
