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
    path: '/sales-voucher',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Sales Invoices',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherList.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Invoices'],
        },
      },
      {
        path: '/sales-voucher/add/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Invoices', 'Create'],
        },
      },
      {
        path: '/sales-voucher/:id/view/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherView.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Invoices', 'View'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Invoices', 'Update'],
        },
      },
      {
        path: '/sales-voucher/:id/mv/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherMV.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Invoices', 'Materialized View'],
        },
      },
    ],
  },
  {
    path: '/payment-receipt',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Payment Receipts',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptList.vue'),
        meta: {
          breadcrumb: ['Home', 'Payment Receipts'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Payment Receipts', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Payment Receipts', 'Update'],
        },
      },
      {
        path: ':id/view/',
        component: () =>
          import('src/pages/payment-receipt/PaymentReceiptView.vue'),
        meta: {
          breadcrumb: ['Home', 'Payment Receipts', 'View'],
        },
      },
    ],
  },
  {
    path: '/credit-note',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Credit Notes',
        component: () =>
          import('src/pages/sales/credit-note/CreditNoteList.vue'),
        meta: {
          breadcrumb: ['Home', 'Credit Notes'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/sales/credit-note/CreditNoteForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Credit Notes', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/sales/credit-note/CreditNoteForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Credit Notes', 'Update'],
        },
      },
      {
        path: ':id/view/',
        component: () =>
          import('src/pages/sales/credit-note/CreditNoteView.vue'),
        meta: {
          breadcrumb: ['Home', 'Credit Notes', 'View'],
        },
      },
    ],
  },
  {
    path: '/challan',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/challan/list/',
        name: 'Challans',
        component: () => import('src/pages/sales/challan/ChallanList.vue'),
        meta: {
          breadcrumb: ['Home', 'Challans'],
        },
      },
      {
        path: '/challan/add/',
        component: () => import('src/pages/sales/challan/ChallanForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Challans', 'Create'],
        },
      },
      {
        path: '/challan/:id/',
        component: () => import('src/pages/sales/challan/ChallanForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Challans', 'Update'],
        },
      },
    ],
  },
  {
    path: '/sales-discount',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Sales Discounts',
        component: () =>
          import('src/pages/sales/discount/SalesDiscountList.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Discounts'],
        },
      },
      {
        path: '/sales-discount/add/',
        component: () =>
          import('src/pages/sales/discount/SalesDiscountForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Discounts', 'Create'],
        },
      },
      {
        path: '/sales-discount/:id/',
        component: () =>
          import('src/pages/sales/discount/SalesDiscountForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Discounts', 'Update'],
        },
      },
    ],
  },
  {
    path: '/sales-row',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/sales/row/SalesRowList.vue'),
        name: 'Sales Rows',
        meta: {
          breadcrumb: ['Home', 'Sales Rows'],
        },
      },
    ],
  },
  {
    path: '/sales-book',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/sales/book/SalesBookList.vue'),
        name: 'Sales Books',
        meta: {
          breadcrumb: ['Home', 'Sales Books'],
        },
      },
    ],
  },
  {
    path: '/purchase-voucher',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherList.vue'),
        name: 'Purchases/Expenses',
        meta: {
          breadcrumb: ['Home', 'Purchases/Expenses'],
        },
      },
      {
        path: '/purchase-voucher/add/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchases/Expenses', 'Create'],
        },
      },
      {
        path: '/purchase-voucher/:id/view/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherView.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchases/Expenses', 'View'],
        },
      },
      {
        path: '/purchase-voucher/:id/',
        component: () =>
          import('src/pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchases/Expenses', 'Update'],
        },
      },
    ],
  },
  {
    path: '/debit-note',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesList.vue'),
        name: 'Debit Notes',
        meta: {
          breadcrumb: ['Home', 'Debit Notes'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Debit Notes', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Debit Notes', 'Update'],
        },
      },
      {
        path: ':id/view/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesView.vue'),
        meta: {
          breadcrumb: ['Home', 'Debit Notes', 'View'],
        },
      },
    ],
  },
  {
    path: '/purchase-discount',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () =>
          import('src/pages/purchase/discounts/PurchaseDiscountList.vue'),
        name: 'Purchase Discounts',
        meta: {
          breadcrumb: ['Home', 'Purchase Discounts'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/purchase/discounts/PurchaseDiscountForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchase Discounts', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/purchase/discounts/PurchaseDiscountForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchase Discounts', 'Update'],
        },
      },
    ],
  },
  {
    path: '/purchase-book',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () =>
          import('src/pages/purchase/purchase-book/PurchaseBookList.vue'),
        name: 'Purchase Books',
        meta: {
          breadcrumb: ['Home', 'Purchase Books'],
        },
      },
    ],
  },
  {
    path: '/purchase-book',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () =>
          import('src/pages/purchase/purchase-book/PurchaseBookList.vue'),
        name: 'Purchase Books',
        meta: {
          breadcrumb: ['Home', 'Purchase Books'],
        },
      },
    ],
  },
  {
    path: '/account',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('src/pages/account/ledger/LedgerList.vue'),
        name: 'Accounts',
        meta: {
          breadcrumb: ['Home', 'Accounts'],
        },
      },
      {
        path: 'add/',
        component: () => import('src/pages/account/ledger/LedgerForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Accounts', 'Create'],
        },
      },
      {
        path: ':id/view/',
        component: () => import('src/pages/account/ledger/LedgerDetail.vue'),
        props: true,
        meta: {
          breadcrumb: ['Home', 'Accounts', 'View'],
        },
      },
      {
        path: ':id/edit/',
        component: () => import('src/pages/account/ledger/LedgerForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Accounts', 'Update'],
        },
      },
    ],
  },
  {
    path: '/account-category',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/account/category/CategoryList.vue'),
        name: 'Account Categories',
        meta: {
          breadcrumb: ['Home', 'Account Categories'],
        },
      },
      {
        path: 'add/',
        component: () => import('src/pages/account/category/CategoryForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Account Categories', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () => import('src/pages/account/category/CategoryForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Account Categories', 'Update'],
        },
      },
    ],
  },
  {
    path: '/journal-voucher',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherList.vue'),
        name: 'Journal Vouchers',
        meta: {
          breadcrumb: ['Home', 'Journal Vouchers'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Journal Vouchers', 'Create'],
        },
      },
      {
        path: ':id/view/',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherDetails.vue'),
        meta: {
          breadcrumb: ['Home', 'Journal Vouchers', 'View'],
        },
        props: true,
      },
      {
        path: ':id/edit/',
        component: () =>
          import('src/pages/account/journal-voucher/JournalVoucherForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Journal Vouchers', 'Update'],
        },
      },
    ],
  },
  {
    path: '/account-opening-balance',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () =>
          import('src/pages/account/opening-balance/OpeningBalanceList.vue'),
        name: 'Account Opening Balances',
        meta: {
          breadcrumb: ['Home', 'Account Opening Balances'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/account/opening-balance/OpeningBalanceForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Account Opening Balances', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/account/opening-balance/OpeningBalanceForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Account Opening Balances', 'Update'],
        },
      },
    ],
  },
  {
    path: '/report',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'trial-balance/',
        component: () => import('src/pages/report/TrialBalance.vue'),
        meta: {
          breadcrumb: ['Home', 'Trial Balance'],
        },
      },
      {
        path: 'category-tree/',
        component: () => import('src/pages/report/CategoryTree.vue'),
        meta: {
          breadcrumb: ['Home', 'Category Tree'],
        },
      },
      {
        path: 'tax-summary/',
        component: () => import('src/pages/report/TaxSummary.vue'),
        meta: {
          breadcrumb: ['Home', 'Periodic Tax Summary'],
        },
      },
      {
        path: 'collection-report/',
        component: () => import('src/pages/report/CollectionReport.vue'),
        meta: {
          breadcrumb: ['Home', 'Collection Report'],
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
        path: 'book/list/',
        component: () => import('src/pages/book/BookList.vue'),
      },
      {
        path: 'book/add/',
        component: () => import('src/pages/book/BookForm.vue'),
      },
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
      // egov Port
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
