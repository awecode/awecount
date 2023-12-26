<template>
  <q-layout view="lHh Lpr lFf" class="container-padding-left">
    <!-- <q-header elevated class="bg-grey-1 text-grey-9"> -->
    <q-header elevated class="bg-white text-grey-8 q-pa-sm d-print-none print-hide q-pl-md">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title class="flex items-center" style="gap: 16px;">
          <RouterLink v-if="store.companyInfo?.logo_url" to="/" style="max-width: 60px; max-height: 40px;">
            <img style="max-width: 60px; max-height: 40px; object-fit: contain;" :src="store.companyInfo.logo_url" alt="Company Logo">
          </RouterLink>
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
            <q-btn class="gt-sm">{{ store.companyInfo?.current_fiscal_year }}
              <q-tooltip :delay="1000" :offset="[0, 10]">Fiscal Yaar</q-tooltip></q-btn>
            <q-btn v-if="store.companyInfo?.config_template === 'np'" class="dateSwitcher bg-grey-7 text-grey-2" @click="store.isCalendarInAD = !store.isCalendarInAD">{{
              activeDateFormat }}
              <q-tooltip :delay="1000" :offset="[0, 10]">Change Date Format</q-tooltip>
            </q-btn>
            <a target="_blank" href="https://docs.awecount.com/" style="color: inherit;">
              <q-btn class="gt-sm"><q-icon name="mdi-help-circle-outline"></q-icon><q-tooltip :delay="1000"
                  :offset="[0, 10]">Help</q-tooltip></q-btn>
            </a>
            <q-btn @click="logoutDiologueOpen = true"><q-icon name="mdi-logout" /><q-tooltip :delay="1000"
                :offset="[0, 10]">Logout</q-tooltip></q-btn>
            <q-dialog v-model="logoutDiologueOpen">
              <q-card style="min-width: min(40vw, 450px)">
                <div style="margin: 20px 30px 10px">
                  <div class="text-h6 text-grey-9">
                    <span>Are you sure you want to logout?</span>
                  </div>
                  <div class="q-mb-md" style="margin-top: 40px">
                    <div class="text-right text-blue-6 row justify-end q-gutter-x-lg">
                      <q-btn flat label="Cancel" class="text-grey-8" @click="logoutDiologueOpen = false"></q-btn>
                      <q-btn flat label="Yes" class="text-red" @click="onLogoutClick()"></q-btn>
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
    <q-drawer drawer persistent overlay show-if-above :mini="miniState" @mouseover="miniState = false"
      @mouseout="miniState = true" v-model="leftDrawerOpen" class="shadow-6">
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
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { EssentialLinkProps } from 'components/EssentialLink.vue'
import { useLoginStore } from '../stores/login-info.js'
import checkPermissions from 'src/composables/checkPermissions'
// import useApi from 'src/composables/useApi'
import { Ref } from 'vue'
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
const miniState: Ref<boolean> = ref(true)
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
        hide: !checkPermissions('ItemView')
      },
      {
        title: 'Units',
        icon: 'mdi-scale-balance',
        link: '/units/list/',
        hide: !checkPermissions('UnitView')
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: '/inventory-category/list/',
        hide: !checkPermissions('CategoryView')
      },
      {
        title: 'Brands',
        icon: 'mdi-domain',
        link: '/brand/list/',
        hide: !checkPermissions('BrandView')
      },
      {
        title: 'Inventory Ledger',
        icon: 'inventory',
        link: '/inventory-account/list/',
        hide: !checkPermissions('InventoryAccountView')
      },
      {
        title: 'Opening Stock',
        icon: 'edit_note',
        link: '/items/opening/',
        hide: !checkPermissions('AccountOpeningBalanceView')
      },
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
        hide: !checkPermissions('SalesView')

      },
      {
        title: 'Credit Notes',
        icon: 'mdi-clipboard-arrow-down',
        link: '/credit-note/list/',
        hide: !checkPermissions('CreditNoteView')
      },
      {
        title: 'Challans',
        icon: 'mdi-clipboard-arrow-right',
        link: '/challan/list/',
        hide: !checkPermissions('ChallanView')
      },
      {
        title: 'Payment Receipts',
        icon: 'mdi-receipt',
        link: '/payment-receipt/list/',
        hide: !checkPermissions('PaymentReceiptView')
      },
      {
        title: 'Sales Discounts',
        icon: 'mdi-sale',
        link: '/sales-discount/list/',
        hide: !checkPermissions('SalesDiscountView')
      },
      {
        title: 'Sales Report',
        icon: 'mdi-format-list-bulleted',
        link: '/sales-row/list/',
        hide: !checkPermissions('SalesView')
      },
      {
        title: 'Sales Book',
        icon: 'mdi-book',
        link: '/sales-book/list/',
        hide: !checkPermissions('SalesView')
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
        hide: !checkPermissions('PurchaseVoucherView')
      },
      {
        title: 'Debit Notes',
        icon: 'mdi-clipboard-arrow-up',
        link: '/debit-note/list/',
        hide: !checkPermissions('DebitNoteView')
      },
      {
        title: 'Purchase Order',
        icon: 'mdi-clipboard-arrow-left',
        link: '/purchase-order/list/',
        hide: !checkPermissions('DebitNoteView')
      },
      {
        title: 'Purchase Discounts',
        icon: 'mdi-sale',
        link: '/purchase-discount/list/',
        hide: !checkPermissions('PurchaseDiscountView')
      },
      {
        title: 'Purchase Book',
        icon: 'book',
        link: '/purchase-book/list/',
        hide: !checkPermissions('PurchaseVoucherView')
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
        hide: !checkPermissions('AccountView')
      },
      {
        title: 'Categories',
        icon: 'mdi-format-list-bulleted',
        link: '/account-category/list',
        hide: !checkPermissions('CategoryView')
      },
      {
        title: 'Journal Vouchers',
        icon: 'mdi-shuffle',
        link: '/journal-voucher/',
        hide: !checkPermissions('JournalVoucherView')
      },
      {
        title: 'All Accounts',
        icon: 'mdi-notebook-multiple',
        link: '/account/',
        hide: !checkPermissions('AccountView')
      },
      {
        title: 'Opening Balances',
        icon: 'mdi-cash',
        link: '/account-opening-balance/',
        hide: !checkPermissions('AccountOpeningBalanceView')
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
        hide: !checkPermissions('CategoryView')
      },
      {
        title: 'Periodic Tax Summary',
        icon: 'mdi-currency-usd-off',
        link: '/report/tax-summary/',
        hide: !checkPermissions('TaxPaymentView')
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
        hide: !checkPermissions('TransactionView')
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
        title: 'Accounts',
        icon: 'mdi-bank',
        link: '/bank-accounts/list/',
        hide: !checkPermissions('BankAccountView')
      },
      {
        title: 'Cheque Issues',
        icon: 'mdi-checkbook',
        link: '/cheque-issue/list/',
        hide: !checkPermissions('ChequeIssueView')
      },
      {
        title: 'Cheque Deposits',
        icon: 'mdi-ballot',
        link: '/cheque-deposit/list/',
        hide: !checkPermissions('ChequeDepositView')
      },
      {
        title: 'Cash Deposits',
        icon: 'mdi-cash',
        link: '/cash-deposit/list/',
        hide: !checkPermissions('BankCashDepositView')
      },
      {
        title: 'Funds Transfers',
        icon: 'mdi-bank-transfer',
        link: '/fund-transfer/list/',
        hide: !checkPermissions('FundTransferView')
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
        hide: !checkPermissions('TaxSchemeView')
      },
      {
        title: 'Tax Payments',
        icon: 'mdi-cash-marker',
        link: '/tax-payment/list/',
        hide: !checkPermissions('TaxPaymentView')
      },
      {
        title: 'Periodic Summary',
        icon: 'mdi-file-chart',
        link: '/report/tax-summary/',
        hide: !checkPermissions('TaxPaymentView')
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
        hide: !checkPermissions('PartyView')
      },
      {
        title: 'Customers',
        icon: 'mdi-domain',
        link: '/parties/customers/',
        hide: !checkPermissions('PartyView')
      },
      {
        title: 'Suppliers',
        icon: 'mdi-account',
        link: '/parties/suppliers/',
        hide: !checkPermissions('PartyView')
      },
      {
        title: 'Sales Agent',
        icon: 'mdi-face-agent',
        link: '/sales-agent/list/',
        hide: !checkPermissions('SalesAgentView')
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
        hide: !checkPermissions('LogEntryView')
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
        hide: !checkPermissions('WidgetView')
      },
      {
        title: 'Sales Settings',
        icon: 'mdi-point-of-sale',
        link: '/settings/sales/',
        hide: !checkPermissions('SalesSettingView')
      },
      {
        title: 'Purchase Settings',
        icon: 'mdi-shopping',
        link: '/settings/purchase/',
        hide: !checkPermissions('PurchaseSettingView')
      },
      {
        title: 'Account Closing',
        icon: 'mdi-calendar-multiple-check',
        link: '/settings/account-closing/',
        hide: !checkPermissions('AccountClosingCreate')
      },
    ],
  },
  {
    title: 'POS ',
    icon: 'mdi-cart-arrow-right',
    link: '/pos',
    hide: !checkPermissions('SalesCreate') && !checkPermissions('SalesView')
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

@media (min-width: 1000px) {
  .container-padding-left {
    padding-left: 60px;
  }
}
</style>
