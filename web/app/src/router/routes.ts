import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/items',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Items',
        component: () => import('src/pages/inventory/item/ItemList.vue'),
        meta: { breadcrumb: ['Home', 'Items'] },
      },
      {
        path: 'add/',
        name: 'Item Create',
        meta: {
          breadcrumb: ['Home', 'Items', 'Create'],
        },
        component: () => import('src/pages/inventory/item/ItemAdd.vue'),
      },
      {
        path: ':id/',
        component: () => import('src/pages/inventory/item/ItemAdd.vue'),
        meta: {
          breadcrumb: ['Home', 'Items', 'Update'],
        },
      },
      {
        path: 'details/:id/',
        component: () => import('src/pages/inventory/item/ItemDetails.vue'),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Opening'],
        },
      },
      {
        path: 'opening/',
        name: 'Stock Opening',
        component: () =>
          import(
            'src/pages/inventory/item/opening-balance/ItemOpeningBalanceList.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Opening'],
        },
      },
      {
        path: 'opening/add',
        component: () =>
          import(
            'src/pages/inventory/item/opening-balance/ItemOpeningBalanceForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Opening', 'Create'],
        },
      },
      {
        path: 'opening/:id',
        component: () =>
          import(
            'src/pages/inventory/item/opening-balance/ItemOpeningBalanceForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Opening', 'Update'],
        },
      },
    ],
  },
  {
    path: '/units',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list',
        name: 'Units',
        component: () => import('src/pages/inventory/unit/UnitList.vue'),
        meta: { breadcrumb: ['Home', 'Units'] },
      },
      // {
      //   path: 'brand/list/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandList.vue'),
      // },
      // {
      //   path: 'brand/:id/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandForm.vue'),
      // },
      // {
      //   path: 'brand/add/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandForm.vue'),
      // },
      {
        path: 'add/',
        component: () => import('src/pages/inventory/unit/UnitForm.vue'),
        meta: { breadcrumb: ['Home', 'Units', 'Create'] },
      },
      {
        path: ':id/',
        component: () => import('src/pages/inventory/unit/UnitForm.vue'),
        meta: { breadcrumb: ['Home', 'Units', 'Update'] },
      },
    ],
  },
  {
    path: '/units',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list',
        name: 'Units',
        component: () => import('src/pages/inventory/unit/UnitList.vue'),
        meta: { breadcrumb: ['Home', 'Units'] },
      },
      // {
      //   path: 'brand/list/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandList.vue'),
      // },
      // {
      //   path: 'brand/:id/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandForm.vue'),
      // },
      // {
      //   path: 'brand/add/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandForm.vue'),
      // },
      {
        path: 'add/',
        component: () => import('src/pages/inventory/unit/UnitForm.vue'),
        meta: { breadcrumb: ['Home', 'Units', 'Create'] },
      },
      {
        path: ':id/',
        component: () => import('src/pages/inventory/unit/UnitForm.vue'),
        meta: { breadcrumb: ['Home', 'Units', 'Update'] },
      },
    ],
  },
  {
    path: '/brand',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Brands',
        component: () =>
          import('src/pages/inventory/product/brand/BrandList.vue'),
        meta: { breadcrumb: ['Home', 'Brands'] },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/inventory/product/brand/BrandForm.vue'),
        meta: { breadcrumb: ['Home', 'Brands', 'Update'] },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/inventory/product/brand/BrandForm.vue'),
        meta: { breadcrumb: ['Home', 'Brands', 'Create'] },
      },
    ],
  },
  {
    path: '/inventory-category',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Inventory Categories',
        component: () =>
          import(
            'src/pages/inventory/product/category/InventoryCategoryList.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Inventory Categories'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import(
            'src/pages/inventory/product/category/InventoryCategoryForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Inventory Categories', 'Create'],
        },
      },
      {
        path: ':id',
        component: () =>
          import(
            'src/pages/inventory/product/category/InventoryCategoryForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Inventory Categories', 'Update'],
        },
      },
    ],
  },
  {
    path: '/inventory-account',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Inventory Accounts',
        component: () =>
          import(
            'src/pages/inventory/product/inventory-account/InventoryAccountList.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Inventory Accounts'],
        },
      },
      //
      {
        path: 'detail/:id/',
        component: () =>
          import(
            'src/pages/inventory/product/inventory-account/InventoryAccountDetail.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Inventory Accounts', 'Detail'],
        },
      },
    ],
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '/', component: () => import('src/pages/LandingPage.vue') },
      {
        path: 'dashboard',
        component: () => import('src/pages/DashBoard.vue'),
        name: 'Home',
      },
      {
        path: '/sales-voucher/list/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherList.vue'),
      },
      {
        path: '/sales-voucher/add/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherForm.vue'),
      },
      {
        path: '/sales-voucher/:id/view/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherView.vue'),
      },
      {
        path: '/sales-voucher/:id/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherForm.vue'),
      },
      {
        path: '/sales-voucher/:id/mv/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherMV.vue'),
      },
      {
        path: '/payment-receipt/list/',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptList.vue'),
      },
      {
        path: '/payment-receipt/add/',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptForm.vue'),
      },
      {
        path: '/payment-receipt/:id/',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptForm.vue'),
      },
      {
        path: '/payment-receipt/:id/view/',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptView.vue'),
      },
      {
        path: '/sales-discount/list/',
        component: () =>
          import('src/pages/sales/discount/SalesDiscountList.vue'),
      },
      {
        path: '/sales-discount/add/',
        component: () =>
          import('src/pages/sales/discount/SalesDiscountForm.vue'),
      },
      {
        path: '/sales-discount/:id/',
        component: () =>
          import('src/pages/sales/discount/SalesDiscountForm.vue'),
      },
      {
        path: '/sales-row/list/',
        component: () => import('src/pages/sales/row/SalesRowList.vue'),
      },
      {
        path: '/sales-book/list/',
        component: () => import('src/pages/sales/book/SalesBookList.vue'),
      },
      {
        path: '/purchase-voucher/list/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherList.vue'),
      },
      {
        path: '/purchase-voucher/add/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
      },
      {
        path: '/purchase-voucher/:id/view/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherView.vue'),
      },
      {
        path: '/purchase-voucher/:id/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
      },
      // {
      //   path: '/purchase-voucher/journal-entries/:id/',
      //   component: () =>
      //     import(
      //       'src/pages/purchase/purchase-voucher/PurchaseVoucherJournalEntries.vue'
      //     ),
      // },
      {
        path: '/debit-note/list/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesList.vue'),
      },
      {
        path: '/debit-note/add/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesForm.vue'),
      },
      {
        path: '/debit-note/:id/view/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesView.vue'),
      },
      {
        path: '/purchase-discount/list/',
        component: () =>
          import('src/pages/purchase/discounts/PurchaseDiscountList.vue'),
      },
      {
        path: '/purchase-discount/add/',
        component: () =>
          import('src/pages/purchase/discounts/PurchaseDiscountForm.vue'),
      },
      {
        path: '/purchase-discount/:id/',
        component: () =>
          import('src/pages/purchase/discounts/PurchaseDiscountForm.vue'),
      },
      {
        path: '/purchase-book/list/',
        component: () =>
          import('src/pages/purchase/purchase-book/PurchaseBookList.vue'),
      },
      {
        path: '/challan/list/',
        component: () => import('src/pages/sales/challan/ChallanList.vue'),
      },
      {
        path: '/challan/add/',
        component: () => import('src/pages/sales/challan/ChallanForm.vue'),
      },
      {
        path: '/challan/:id/',
        component: () => import('src/pages/sales/challan/ChallanForm.vue'),
      },
      {
        path: 'book/list/',
        component: () => import('src/pages/book/BookList.vue'),
      },
      {
        path: 'book/add/',
        component: () => import('src/pages/book/BookForm.vue'),
      },

      // {
      //   path: 'inventory-category/list/',
      //   component: () =>
      //     import(
      //       'src/pages/inventory/product/category/InventoryCategoryList.vue'
      //     ),
      // },
      // {
      //   path: 'inventory-category/add/',
      //   component: () =>
      //     import(
      //       'src/pages/inventory/product/category/InventoryCategoryForm.vue'
      //     ),
      // },

      {
        path: '/credit-note/list/',
        component: () =>
          import('src/pages/sales/credit-note/CreditNoteList.vue'),
      },
      {
        path: '/credit-note/add/',
        component: () =>
          import('src/pages/sales/credit-note/CreditNoteForm.vue'),
      },
      {
        path: '/credit-note/:id/view/',
        component: () =>
          import('src/pages/sales/credit-note/CreditNoteView.vue'),
      },
      // {
      //   path: 'brand/list/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandList.vue'),
      // },
      // {
      //   path: 'brand/:id/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandForm.vue'),
      // },
      // {
      //   path: 'brand/add/',
      //   component: () =>
      //     import('src/pages/inventory/product/brand/BrandForm.vue'),
      // },
      // {
      //   path: 'units/list/',
      //   component: () => import('src/pages/inventory/unit/UnitList.vue'),
      // },
      // {
      //   path: 'units/add/',
      //   component: () => import('src/pages/inventory/unit/UnitForm.vue'),
      // },
      // {
      //   path: 'units/:id/',
      //   component: () => import('src/pages/inventory/unit/UnitForm.vue'),
      // },
      // egov Port
      {
        path: 'bank/account/add/',
        component: () => import('src/pages/bank/account/AccountForm.vue'),
      },
      {
        path: 'bank/account/:id/edit/',
        component: () => import('src/pages/bank/account/AccountForm.vue'),
      },
      // {
      //   path: 'bank/account/:id/view/',
      //   component: () => import('src/pages/bank/account/AccountDetail.vue'),
      //   props: true,
      // },
      {
        path: 'bank',
        component: () => import('src/pages/bank/account/AccountList.vue'),
      },
      {
        path: 'bank/cheque-issue/',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueList.vue'),
      },
      {
        path: 'bank/cheque/cheque-issue/add/',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueForm.vue'),
      },
      {
        path: 'bank/cheque/cheque-issue/:id/edit/',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueForm.vue'),
      },
      {
        path: 'bank/cheque-deposit/',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositList.vue'),
      },
      {
        path: 'bank/cheque/cheque-deposit/:id/view/',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositDetail.vue'),
        props: true,
      },
      // journal
      {
        path: 'journal-entries/:slug/:id/',
        component: () => import('src/pages/journal-entry/[slugUrl].vue'),
        props: true,
      },
      // journal
      {
        path: 'bank/cheque/cheque-deposit/add/',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositForm.vue'),
      },
      {
        path: 'bank/cheque/cheque-deposit/:id/edit/',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositForm.vue'),
      },
      {
        path: 'bank/cash-deposit/',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositList.vue'),
      },
      {
        path: 'bank/cash/cash-deposit/add/',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositForm.vue'),
      },
      {
        path: 'bank/cash/cash-deposit/:id/edit/',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositForm.vue'),
      },
      {
        path: 'bank/fund-transfer/',
        component: () =>
          import('src/pages/bank/fund-transfer/FundTransferList.vue'),
      },
      {
        path: 'bank/fund/fund-transfer/add/',
        component: () =>
          import('src/pages/bank/fund-transfer/FundTransferForm.vue'),
      },
      {
        path: 'bank/fund/fund-transfer/:id/edit/',
        component: () =>
          import('src/pages/bank/fund-transfer/FundTransferForm.vue'),
      },
      {
        path: 'account/',
        component: () => import('src/pages/account/ledger/LedgerList.vue'),
      },
      {
        path: 'account/add/',
        component: () => import('src/pages/account/ledger/LedgerForm.vue'),
      },
      {
        path: 'account/:id/view/',
        component: () => import('src/pages/account/ledger/LedgerDetail.vue'),
        props: true,
      },
      {
        path: 'account/:id/edit/',
        component: () => import('src/pages/account/ledger/LedgerForm.vue'),
      },
      {
        path: 'journal-voucher/',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherList.vue'),
      },
      {
        path: 'journal-voucher/add/',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherForm.vue'),
      },
      {
        path: 'journal-voucher/:id/view/',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherDetails.vue'),
        props: true,
      },
      {
        path: 'journal-voucher/:id/edit/',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherForm.vue'),
      },
      {
        path: 'account/category/',
        component: () => import('src/pages/account/category/CategoryList.vue'),
      },
      {
        path: 'account/category/add/',
        component: () => import('src/pages/account/category/CategoryForm.vue'),
      },
      {
        path: 'account/category/:id/edit/',
        component: () => import('src/pages/account/category/CategoryForm.vue'),
      },
      {
        path: 'account/opening-balance/',
        component: () =>
          import('src/pages/account/opening-balance/OpeningBalanceList.vue'),
      },
      {
        path: 'account/opening-balance/add/',
        component: () =>
          import('src/pages/account/opening-balance/OpeningBalanceForm.vue'),
      },
      {
        path: 'account/opening-balance/:id/edit/',
        component: () =>
          import('src/pages/account/opening-balance/OpeningBalanceForm.vue'),
      },
      // egov Port
      {
        path: '/report/trial-balance/',
        component: () => import('src/pages/report/TrialBalance.vue'),
      },
      {
        path: '/report/category-tree/',
        component: () => import('src/pages/report/CategoryTree.vue'),
      },
      {
        path: '/report/tax-summary/',
        component: () => import('src/pages/report/TaxSummary.vue'),
      },
      {
        path: '/report/collection-report/',
        component: () => import('src/pages/report/CollectionReport.vue'),
      },
      {
        path: '/taxes/list/',
        component: () => import('src/pages/tax/scheme/TaxAccountList.vue'),
      },
      {
        path: '/taxes/add/',
        component: () => import('src/pages/tax/scheme/TaxForm.vue'),
      },
      {
        path: '/taxes/:id/',
        component: () => import('src/pages/tax/scheme/TaxForm.vue'),
      },
      {
        path: '/taxes/account/:id/',
        component: () => import('src/pages/tax/scheme/TaxForm.vue'),
      },
      {
        path: '/tax-payment/list/',
        component: () => import('src/pages/tax/payments/TaxPaymentList.vue'),
      },
      {
        path: '/tax-payment/add/',
        component: () => import('src/pages/tax/payments/TaxPaymentForm.vue'),
      },
      {
        path: '/tax-payment/:id/',
        component: () => import('src/pages/tax/payments/TaxPaymentForm.vue'),
      },
      {
        path: '/party/list/',
        component: () => import('src/pages/party/PartyList.vue'),
      },
      {
        path: '/party/add/',
        component: () => import('src/pages/party/PartyForm.vue'),
      },
      {
        path: '/party/:id/',
        component: () => import('src/pages/party/PartyForm.vue'),
      },
      {
        path: '/parties/account/:id',
        component: () => import('src/pages/party/PartyAccount.vue'),
      },
      {
        path: '/parties/customers/',
        component: () => import('src/pages/party/CustomerList.vue'),
      },
      {
        path: '/parties/suppliers/',
        component: () => import('src/pages/party/SupplierList.vue'),
      },
      {
        path: '/sales-agent/list/',
        component: () => import('src/pages/sales/agent/SalesAgentList.vue'),
      },
      {
        path: '/sales-agent/add/',
        component: () => import('src/pages/sales/agent/SalesAgentForm.vue'),
      },
      {
        path: '/sales-agent/:id/',
        component: () => import('src/pages/sales/agent/SalesAgentForm.vue'),
      },
      {
        path: '/audit-log/list/',
        component: () => import('src/pages/settings/auditlog/AuditLogList.vue'),
      },
      {
        path: '/audit-log/:id/',
        component: () =>
          import('src/pages/settings/auditlog/AuditLogDetails.vue'),
      },
      {
        path: '/settings/import-export/',
        component: () => import('src/pages/settings/ImportExport.vue'),
      },
      {
        path: '/dashboard-widgets/list/',
        component: () => import('src/pages/settings/widgets/WidgetList.vue'),
      },
      {
        path: '/dashboard-widgets/add/',
        component: () => import('src/pages/settings/widgets/WidgetForm.vue'),
      },
      {
        path: '/dashboard-widgets/:id/',
        component: () => import('src/pages/settings/widgets/WidgetForm.vue'),
      },
      {
        path: '/settings/sales/',
        component: () => import('src/pages/settings/SalesSetting.vue'),
      },
      {
        path: '/settings/purchase/',
        component: () => import('src/pages/settings/PurchaseSetting.vue'),
      },
      {
        path: '/pos/',
        component: () => import('src/pages/sales/pos/PosForm.vue'),
      },
      {
        path: '/test/',
        component: () => import('src/pages/TestPage.vue'),
      },
      // {
      //   path: '/dashboard/',
      //   component: () => import('src/pages/Dashboard.vue'),
      // },
      // {
      //   path: 'income/add/',
      //   component: () => import('src/pages/income/IncomeForm.vue'),
      // },
      // {
      //   path: 'income/:id/edit',
      //   component: () => import('src/pages/income/IncomeForm.vue'),
      // },
      // {
      //   path: 'income/item/',
      //   component: () => import('src/pages/income/IncomeItemList.vue'),
      // },
    ],
  },
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue'),
    // children: [{ path: "", component: () => import("pages/IndexPage.vue") }],
  },
  // {
  //   path: '/',
  //   component: () => import('pages/LandingPage.vue'),
  //   // children: [{ path: "", component: () => import("pages/IndexPage.vue") }],
  // },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
