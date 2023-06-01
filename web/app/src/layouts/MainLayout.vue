<template>
  <q-layout view="lHh Lpr lFf">
    <!-- <q-header elevated class="bg-grey-1 text-grey-9"> -->
    <q-header elevated class="bg-white text-grey-8 q-pa-sm d-print-none print-hide">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>
          <q-breadcrumbs class="gt-xs" gutter="sm">
            <q-breadcrumbs-el v-for="breadCrum in breadCrums" :key="breadCrum" :label="breadCrum"
              :to="{ name: breadCrum }" />
            <!-- :class="breadCrums?.length - 1 === index cursor-pointer" -->
          </q-breadcrumbs>
        </q-toolbar-title>
        <div>
          <!-- <q-btn @click="confirmSignOut" square color="red" icon="power_settings_new" />
             -->
          <div class="row btns-Con">
            <q-btn class="gt-sm">{{ store.companyInfo.current_fiscal_year }}
              <q-tooltip :delay="1000" :offset="[0, 10]">Fiscal Yaar</q-tooltip></q-btn>
            <q-btn class="dateSwitcher bg-grey-7 text-grey-2" @click="store.isCalendarInAD = !store.isCalendarInAD">{{
              activeDateFormat }}
              <q-tooltip :delay="1000" :offset="[0, 10]">Change Date Format</q-tooltip>
            </q-btn>
            <q-btn class="gt-sm"><q-icon name="mdi-help-circle-outline"></q-icon><q-tooltip :delay="1000"
                :offset="[0, 10]">Help</q-tooltip></q-btn>
            <q-btn @click="logoutDiologueOpen = true"><q-icon name="mdi-logout" /><q-tooltip :delay="1000"
                :offset="[0, 10]">Logout</q-tooltip></q-btn>
            <q-dialog v-model="logoutDiologueOpen">
              <q-card style="min-width: min(40vw, 450px)">
                <div style="margin: 20px 30px 10px">
                  <div class="text-h6 text-grey-9">
                    <span>Are you sure you want to logout?</span>
                  </div>
                  <div class="q-mx-md" style="margin-top: 40px">
                    <div class="text-right text-blue-6 row justify-end q-gutter-x-lg">
                      <q-btn flat label="Logout" @click="onLogoutClick()"></q-btn>
                      <q-btn flat label="Cancel" @click="logoutDiologueOpen = false"></q-btn>
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
    <q-drawer v-model="leftDrawerOpen" show-if-above bordered class="d-print-none print-hide">
      <q-list class="icon-grey d-print-none print-hide">
        <!-- <q-item-label header> Menu </q-item-label> -->
        <!-- <q-img src="../assets/background-image.png" style="height: 90px">
            <div class="absolute-bottom bg-transparent text-black">
              <div class="text-weight-bold text-h6 text-grey-10">{{ store.username }}</div>
            </div>
          </q-img> -->

        <div class="q-mb-md"></div>

        <EssentialLink v-for="link in essentialLinks" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { EssentialLinkProps } from 'components/EssentialLink.vue'
import { useLoginStore } from '../stores/login-info.js'
// import useApi from 'src/composables/useApi'
import { Ref } from 'vue'
import { ref } from 'vue'
const router = useRouter()
const route = useRoute()
const breadCrums: Ref<Array<string | null>> = ref([])
const store = useLoginStore()
// const router = useRouter()
// const $q = useQuasar()
const activeDateFormat = computed(() => (store.isCalendarInAD ? 'AD' : 'BS'))
const logoutDiologueOpen = ref(false)
const onLogoutClick = () => {
  store.reset()
  router.push('/login')
}

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
      },
      {
        title: 'Units',
        icon: 'mdi-scale-balance',
        link: '/units/list/',
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: '/inventory-category/list/',
      },
      {
        title: 'Brands',
        icon: 'mdi-domain',
        link: '/brand/list/',
      },
      {
        title: 'Inventory Ledger',
        icon: 'inventory',
        link: '/inventory-account/list/',
      },
      {
        title: 'Opening Stock',
        icon: 'edit_note',
        link: '/items/opening/',
      },
    ],
  },
  {
    title: 'Books',
    icon: 'mdi-library',
    link: '/book/list/',
  },
  {
    title: 'Sales',
    icon: 'mdi-point-of-sale',
    children: [
      {
        title: 'Sales invoices',
        icon: 'mdi-point-of-sale',
        link: '/sales-voucher/list/',
      },
      {
        title: 'Credit Notes',
        icon: 'mdi-clipboard-arrow-down',
        link: '/credit-note/list/',
      },
      {
        title: 'Challans',
        icon: 'mdi-clipboard-arrow-right',
        link: '/challan/list/',
      },
      {
        title: 'Payment Receipts',
        icon: 'mdi-receipt',
        link: '/payment-receipt/list/',
      },
      {
        title: 'Sales Discounts',
        icon: 'mdi-sale',
        link: '/sales-discount/list/',
      },
      {
        title: 'Sales Reoprt',
        icon: 'mdi-format-list-bulleted',
        link: '/sales-row/list/',
      },
      {
        title: 'Sales Book',
        icon: 'mdi-book',
        link: '/sales-book/list/',
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
      },
      {
        title: 'Debit Notes',
        icon: 'mdi-clipboard-arrow-up',
        link: '/debit-note/list/',
      },
      {
        title: 'Purchase Discounts',
        icon: 'mdi-sale',
        link: '/purchase-discount/list/',
      },
      {
        title: 'Purchase Book',
        icon: 'book',
        link: '/purchase-book/list/',
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
        link: '/account/',
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: '/account-category/list',
      },
      {
        title: 'Journal Vouchers',
        icon: 'mdi-shuffle',
        link: '/journal-voucher/',
      },
      {
        title: 'All Accounts',
        icon: 'mdi-notebook-multiple',
        link: '/account/',
      },
      {
        title: 'Opening Balances',
        icon: 'mdi-cash',
        link: '/account-opening-balance/',
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
      },
      {
        title: 'Periodic Tax Summary',
        icon: 'mdi-currency-usd-off',
        link: '/report/tax-summary/',
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
        link: '/income/item/',
      },
      {
        title: 'Income Statement',
        icon: 'mdi-chart-gantt',
        link: '/report/income-statement/',
      },
      {
        title: 'Balance Sheet',
        icon: 'mdi-clipboard-text',
        link: '/report/balance-sheet/',
      },
      {
        title: 'Ratio Analysis',
        icon: 'mdi-chart-arc',
        link: '/report/ratio-analysis/',
      },
    ],
  },
  {
    title: 'Banks & Wallets',
    icon: 'mdi-bank',
    children: [
      {
        title: 'Accounts',
        icon: 'mdi-bank',
        link: '/bank-accounts/list/',
      },
      {
        title: 'Cheque Issues',
        icon: 'mdi-checkbook',
        link: '/cheque-issue/list/',
      },
      {
        title: 'Cheque Deposits',
        icon: 'mdi-ballot',
        link: '/cheque-deposit/list/',
      },
      {
        title: 'Cash Deposits',
        icon: 'mdi-cash',
        link: '/cash-deposit/list/',
      },
      {
        title: 'Funds Transfers',
        icon: 'mdi-bank-transfer',
        link: '/fund-transfer/list/',
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
      },
      {
        title: 'Tax Payments',
        icon: 'mdi-cash-marker',
        link: '/tax-payment/list/',
      },
      {
        title: 'Periodic Summary',
        icon: 'mdi-file-chart',
        link: '/report/tax-summary/',
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
      },
      {
        title: 'Customers',
        icon: 'mdi-domain',
        link: '/parties/customers/',
      },
      {
        title: 'Suppliers',
        icon: 'mdi-account',
        link: '/parties/suppliers/',
      },
      {
        title: 'Sales Agent',
        icon: 'mdi-face-agent',
        link: '/sales-agent/list/',
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
      },
      {
        title: 'Sales Settings',
        icon: 'mdi-point-of-sale',
        link: '/settings/sales/',
      },
      {
        title: 'Purchase Settings',
        icon: 'mdi-shopping',
        link: '/settings/purchase/',
      },
    ],
  },
  {
    title: 'POS ',
    icon: 'mdi-cart-arrow-right',
    link: '/pos',
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
  breadCrums.value = route.meta.breadcrumb
})
watch(route, () => {
  breadCrums.value = route.meta.breadcrumb
})
// function confirmSignOut() {
//   $q.dialog({
//     title: 'Sign out',
//     message: 'Are you sure you want to sign out?',
//     cancel: true,
//     ok: 'Yes',
//     persistent: true,
//   })
//     .onOk(() => {
//       // console.log('>>>> OK')
//       // send request
//       useApi('/api/v1/users/logout/', { method: 'POST', body: {} })
//         .then(() => {
//           store.reset()
//           router.push('/login/')
//         })
//         .catch(() => {
//           // console.log(error)
//         })

//     })
//     .onOk(() => {
//       // console.log('>>>> second OK catcher')
//     })
//     .onCancel(() => {
//       // console.log('>>>> Cancel')
//     })
//     .onDismiss(() => {
//       // console.log('I am triggered on both OK and Cancel')
//     })
// }
</script>

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
</style>
