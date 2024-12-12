import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/404',
    name: '404',
    component: () => import('pages/404.vue'),
  },
  {
    path: '/forbidden',
    name: 'no-permission',
    component: () => import('pages/NoPermission.vue'),
  },
  {
    path: '/',
    name: 'landing-page',
    component: () => import('pages/LandingPage.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('pages/Dashboard.vue'),
  },
  {
    path: '/login',
    name: 'login-page',
    component: () => import('pages/LoginPage.vue'),
  },
  {
    path: '/account',
    name: 'account',
    children: [
      {
        path: '/categories',
        name: 'account-categories',
        component: () => import('pages/account/category/CategoryList.vue'),
      },
      {
        path: '/categories/create',
        name: 'account-categories-create',
        component: () => import('pages/account/category/CategoryForm.vue'),
      },
      {
        path: '/categories/:id/edit',
        name: 'account-categories-id',
        component: () => import('pages/account/category/CategoryForm.vue'),
      },
      {
        path: '/journal-vouchers',
        name: 'account-journal-vouchers',
        component: () => import('pages/account/journal-voucher/JournalVoucherList.vue'),
      },
      {
        path: '/journal-vouchers/create',
        name: 'account-journal-vouchers-create',
        component: () => import('pages/account/journal-voucher/JournalVoucherForm.vue'),
      },
      {
        path: '/journal-vouchers/:id',
        name: 'account-journal-vouchers-id',
        component: () => import('pages/account/journal-voucher/JournalVoucherDetail.vue'),
      },
      {
        path: '/journal-vouchers/:id/edit',
        name: 'account-journal-vouchers-id-edit',
        component: () => import('pages/account/journal-voucher/JournalVoucherForm.vue'),
      },
      {
        path: '/ledgers',
        name: 'account-ledgers',
        component: () => import('pages/account/ledger/LedgerList.vue'),
      },
      {
        path: '/ledgers/create',
        name: 'account-ledgers-create',
        component: () => import('pages/account/ledger/LedgerForm.vue'),
      },
      {
        path: '/ledgers/:id',
        name: 'account-ledgers-id',
        component: () => import('pages/account/ledger/LedgerDetail.vue'),
      },
      {
        path: '/ledgers/:id/edit',
        name: 'account-ledgers-id-edit',
        component: () => import('pages/account/ledger/LedgerForm.vue'),
      },
      {
        path: '/opening-balances',
        name: 'account-opening-balances',
        component: () => import('pages/account/opening-balance/OpeningBalanceList.vue'),
      },
      {
        path: '/opening-balances/create',
        name: 'account-opening-balances-create',
        component: () => import('pages/account/opening-balance/OpeningBalanceForm.vue'),
      },
      {
        path: '/opening-balances/:id/edit',
        name: 'account-opening-balances-id-edit',
        component: () => import('pages/account/opening-balance/OpeningBalanceForm.vue'),
      },
    ],
  },
  {
    path: '/banking',
    name: 'banking',
    children: [
      {
        path: '/bank-accounts',
        name: 'banking-bank-accounts',
        component: () => import('pages/bank/account/AccountList.vue'),
      },
      {
        path: '/bank-accounts/create',
        name: 'banking-bank-accounts-create',
        component: () => import('pages/bank/account/AccountForm.vue'),
      },
      {
        path: '/bank-accounts/:id/edit',
        name: 'banking-bank-accounts-id-edit',
        component: () => import('pages/bank/account/AccountForm.vue'),
      },
      {
        path: '/cash-deposits',
        name: 'banking-cash-deposits',
        component: () => import('pages/bank/cash-deposit/CashDepositList.vue'),
      },
      {
        path: '/cash-deposits/create',
        name: 'banking-cash-deposits-create',
        component: () => import('pages/bank/cash-deposit/CashDepositForm.vue'),
      },
      {
        path: '/cash-deposits/:id/edit',
        name: 'banking-cash-deposits-id-edit',
        component: () => import('pages/bank/cash-deposit/CashDepositForm.vue'),
      },
      // {
      //   path: '/cash-withdrawals',
      //   name: 'banking-cash-withdrawals',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalList.vue'),
      // },
      // {
      //   path: '/cash-withdrawals/create',
      //   name: 'banking-cash-withdrawals-create',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalForm.vue'),
      // },
      // {
      //   path: '/cash-withdrawals/:id',
      //   name: 'banking-cash-withdrawals-id',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalDetail.vue'),
      // },
      // {
      //   path: '/cash-withdrawals/:id/edit',
      //   name: 'banking-cash-withdrawals-id-edit',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalForm.vue'),
      // },
      {
        path: '/cheque-deposits',
        name: 'banking-cheque-deposits',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositList.vue'),
      },
      {
        path: '/cheque-deposits/create',
        name: 'banking-cheque-deposits-create',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositForm.vue'),
      },
      {
        path: '/cheque-deposits/:id/edit',
        name: 'banking-cheque-deposits-id-edit',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositForm.vue'),
      },
      {
        path: '/cheque-issues',
        name: 'banking-cheque-issues',
        component: () => import('pages/bank/cheque-issue/ChequeIssueList.vue'),
      },
      {
        path: '/cheque-issues/create',
        name: 'banking-cheque-issues-create',
        component: () => import('pages/bank/cheque-issue/ChequeIssueForm.vue'),
      },
      {
        path: '/cheque-issues/:id/edit',
        name: 'banking-cheque-issues-id-edit',
        component: () => import('pages/bank/cheque-issue/ChequeIssueForm.vue'),
      },
      // {
      //   path: '/cheque-withdrawals',
      //   name: 'banking-cheque-withdrawals',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalList.vue'),
      // },
      // {
      //   path: '/cheque-withdrawals/create',
      //   name: 'banking-cheque-withdrawals-create',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalForm.vue'),
      // },
      // {
      //   path: '/cheque-withdrawals/:id',
      //   name: 'banking-cheque-withdrawals-id',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalDetail.vue'),
      // },
      // {
      //   path: '/cheque-withdrawals/:id/edit',
      //   name: 'banking-cheque-withdrawals-id-edit',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalForm.vue'),
      // },
      {
        path: '/fund-transfers',
        name: 'banking-fund-transfers',
        component: () => import('pages/bank/fund-transfer/FundTransferList.vue'),
      },
      {
        path: '/fund-transfers/create',
        name: 'banking-fund-transfers-create',
        component: () => import('pages/bank/fund-transfer/FundTransferForm.vue'),
      },
      {
        path: '/fund-transfers/:id/edit',
        name: 'banking-fund-transfers-id-edit',
        component: () => import('pages/bank/fund-transfer/FundTransferForm.vue'),
      },
    ],
  },
  {
    path: '/purchase',
    name: 'purchase',
    children: [
      {
        path: '/debit-notes',
        name: 'purchase-debit-notes',
        component: () => import('pages/purchase/debit-notes/DebitNotesList.vue'),
      },
      {
        path: '/debit-notes/create',
        name: 'purchase-debit-notes-create',
        component: () => import('pages/purchase/debit-notes/DebitNotesForm.vue'),
      },
      {
        path: '/debit-notes/:id/edit',
        name: 'purchase-debit-notes-id-edit',
        component: () => import('pages/purchase/debit-notes/DebitNotesForm.vue'),
      },
      {
        path: '/discounts',
        name: 'purchase-discounts',
        component: () => import('pages/purchase/discounts/PurchaseDiscountList.vue'),
      },
      {
        path: '/discounts/create',
        name: 'purchase-discounts-create',
        component: () => import('pages/purchase/discounts/PurchaseDiscountForm.vue'),
      },
      {
        path: '/discounts/:id/edit',
        name: 'purchase-discounts-id-edit',
        component: () => import('pages/purchase/discounts/PurchaseDiscountForm.vue'),
      },
      {
        path: '/purchase-book',
        name: 'purchase-book',
        component: () => import('pages/purchase/purchase-book/PurchaseBookList.vue'),
      },
      {
        path: '/purchase-orders',
        name: 'purchase-orders',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderList.vue'),
      },
      {
        path: '/purchase-orders/create',
        name: 'purchase-orders-create',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderForm.vue'),
      },
      {
        path: '/purchase-orders/:id/edit',
        name: 'purchase-orders-id-edit',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderForm.vue'),
      },
      {
        path: '/purchase-vouchers',
        name: 'purchase-vouchers',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherList.vue'),
      },
      {
        path: '/purchase-vouchers/create',
        name: 'purchase-vouchers-create',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
      },
      {
        path: '/purchase-vouchers/:id',
        name: 'purchase-vouchers-id',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherDetail.vue'),
      },
      {
        path: '/purchase-vouchers/:id/edit',
        name: 'purchase-vouchers-id-edit',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
      },
    ],
  },
  {
    path: '/sales',
    name: 'sales',
    children: [
      {
        path: '/agents',
        name: 'sales-agents',
        component: () => import('pages/sales/agent/SalesAgentList.vue'),
      },
      {
        path: '/agents/create',
        name: 'sales-agents-create',
        component: () => import('pages/sales/agent/SalesAgentForm.vue'),
      },
      {
        path: '/agents/:id/edit',
        name: 'sales-agents-id-edit',
        component: () => import('pages/sales/agent/SalesAgentForm.vue'),
      },
      {
        path: '/sales-book',
        name: 'sales-book',
        component: () => import('pages/sales/book/SalesBookList.vue'),
      },
      {
        path: '/challans',
        name: 'sales-challans',
        component: () => import('pages/sales/challan/ChallanList.vue'),
      },
      {
        path: '/challans/create',
        name: 'sales-challans-create',
        component: () => import('pages/sales/challan/ChallanForm.vue'),
      },
      {
        path: '/challans/:id/edit',
        name: 'sales-challans-id-edit',
        component: () => import('pages/sales/challan/ChallanForm.vue'),
      },
      {
        path: '/credit-notes',
        name: 'sales-credit-notes',
        component: () => import('pages/sales/credit-note/CreditNoteList.vue'),
      },
      {
        path: '/credit-notes/create',
        name: 'sales-credit-notes-create',
        component: () => import('pages/sales/credit-note/CreditNoteForm.vue'),
      },
      {
        path: '/credit-notes/:id',
        name: 'sales-credit-notes-id',
        component: () => import('pages/sales/credit-note/CreditNoteDetail.vue'),
      },
      {
        path: '/credit-notes/:id/edit',
        name: 'sales-credit-notes-id-edit',
        component: () => import('pages/sales/credit-note/CreditNoteForm.vue'),
      },
      {
        path: '/discounts',
        name: 'sales-discounts',
        component: () => import('pages/sales/discount/SalesDiscountList.vue'),
      },
      {
        path: '/discounts/create',
        name: 'sales-discounts-create',
        component: () => import('pages/sales/discount/SalesDiscountForm.vue'),
      },
      {
        path: '/discounts/:id/edit',
        name: 'sales-discounts-id-edit',
        component: () => import('pages/sales/discount/SalesDiscountForm.vue'),
      },
      {
        path: '/pos',
        name: 'sales-pos',
        component: () => import('pages/sales/pos/PosForm.vue'),
      },
      {
        path: '/sales-vouchers',
        name: 'sales-vouchers',
        component: () => import('pages/sales/sales-voucher/SalesVoucherList.vue'),
      },
      {
        path: '/sales-vouchers/create',
        name: 'sales-vouchers-create',
        component: () => import('pages/sales/sales-voucher/SalesVoucherForm.vue'),
      },
      {
        path: '/sales-vouchers/:id',
        name: 'sales-vouchers-id',
        component: () => import('pages/sales/sales-voucher/SalesVoucherDetail.vue'),
      },
      {
        path: '/sales-vouchers/:id/edit',
        name: 'sales-vouchers-id-edit',
        component: () => import('pages/sales/sales-voucher/SalesVoucherForm.vue'),
      },
      {
        path: '/sales-vouchers/:id/material',
        name: 'sales-vouchers-id-edit',
        component: () => import('pages/sales/sales-voucher/SalesVoucherMV.vue'),
      },
    ],
  },
  {
    path: '/settings',
    name: 'settings',
    children: [
      {
        path: '/accounts-closing',
        name: 'settings-accounts-closing',
        component: () => import('pages/settings/AccountsClosing.vue'),
      },
      {
        path: '/import-export',
        name: 'settings-import-export',
        component: () => import('pages/settings/ImportExport.vue'),
      },
      {
        path: '/inventory-settings',
        name: 'settings-inventory',
        component: () => import('pages/settings/InventorySettings.vue'),
      },
      {
        path: '/item-merge',
        name: 'settings-item-merge',
        component: () => import('pages/settings/ItemMerge.vue'),
      },
      {
        path: '/payment-modes',
        name: 'settings-payment-modes',
        component: () => import('pages/settings/PaymentModeList.vue'),
      },
      {
        path: '/payment-modes/create',
        name: 'settings-payment-modes-create',
        component: () => import('pages/settings/PaymentModeForm.vue'),
      },
      {
        path: '/payment-modes/:id/edit',
        name: 'settings-payment-modes-id-edit',
        component: () => import('pages/settings/PaymentModeForm.vue'),
      },
      {
        path: '/purchase-settings',
        name: 'settings-purchase',
        component: () => import('pages/settings/PurchaseSetting.vue'),
      },
      {
        path: '/sales-settings',
        name: 'settings-sales',
        component: () => import('pages/settings/SalesSetting.vue'),
      },
      {
        path: '/audit-logs',
        name: 'settings-audit-logs',
        component: () => import('pages/settings/auditlog/AuditLogList.vue'),
      },
      {
        path: '/audit-logs/:id',
        name: 'settings-audit-logs-id',
        component: () => import('pages/settings/auditlog/AuditLogDetail.vue'),
      },
      {
        path: '/dashboard-widgets',
        name: 'settings-dashboard-widgets',
        component: () => import('pages/settings/widgets/WidgetList.vue'),
      },
      {
        path: '/dashboard-widgets/add',
        name: 'settings-dashboard-widgets-add',
        component: () => import('pages/settings/widgets/WidgetForm.vue'),
      },
      {
        path: '/dashboard-widgets/:id/edit',
        name: 'settings-dashboard-widgets-id-edit',
        component: () => import('pages/settings/widgets/WidgetForm.vue'),
      },
    ],
  },
  {
    path: '/tax',
    name: 'tax',
    children: [
      {
        path: '/payments',
        name: 'tax-payments',
        component: () => import('pages/tax/payments/TaxPaymentList.vue'),
      },
      {
        path: '/payments/create',
        name: 'tax-payments-create',
        component: () => import('pages/tax/payments/TaxPaymentForm.vue'),
      },
      {
        path: '/payments/:id/edit',
        name: 'tax-payments-id-edit',
        component: () => import('pages/tax/payments/TaxPaymentForm.vue'),
      },
      // {
      //   path: '/schemes',
      //   name: 'tax-schemes',
      //   component: () => import('pages/tax/scheme/SchemeList.vue'),
      // },
      // {
      //   path: '/schemes/create',
      //   name: 'tax-schemes-create',
      //   component: () => import('pages/tax/scheme/SchemeForm.vue'),
      // },
      // {
      //   path: '/schemes/:id',
      //   name: 'tax-schemes-id',
      //   component: () => import('pages/tax/scheme/SchemeDetail.vue'),
      // },
      // {
      //   path: '/schemes/:id/edit',
      //   name: 'tax-schemes-id-edit',
      //   component: () => import('pages/tax/scheme/SchemeForm.vue'),
      // },
      // {
      //   path: '/periodic-summary',
      //   name: 'tax-periodic-summary',
      //   component: () => import('pages/tax/periodic-summary/PeriodicSummary.vue'),
      // },
    ],
  },
  {
    path: '/inventory',
    name: 'inventory',
    children: [
      {
        path: '/items',
        name: 'inventory-items',
        component: () => import('pages/inventory/item/ItemList.vue'),
      },
      {
        path: '/items/create',
        name: 'inventory-items-create',
        component: () => import('pages/inventory/item/ItemForm.vue'),
      },
      {
        path: '/items/:id',
        name: 'inventory-items-id',
        component: () => import('pages/inventory/item/ItemDetail.vue'),
      },
      {
        path: '/items/:id/edit',
        name: 'inventory-items-id-edit',
        component: () => import('pages/inventory/item/ItemForm.vue'),
      },
      // {
      //   path: '/products',
      //   name: 'inventory-products',
      //   component: () => import('pages/inventory/product/ProductList.vue'),
      // },
      // {
      //   path: '/products/create',
      //   name: 'inventory-products-create',
      //   component: () => import('pages/inventory/product/ProductForm.vue'),
      // },
      // {
      //   path: '/products/:id',
      //   name: 'inventory-products-id',
      //   component: () => import('pages/inventory/product/ProductDetail.vue'),
      // },
      // {
      //   path: '/products/:id/edit',
      //   name: 'inventory-products-id-edit',
      //   component: () => import('pages/inventory/product/ProductForm.vue'),
      // },
      {
        path: '/units',
        name: 'inventory-units',
        component: () => import('pages/inventory/unit/UnitList.vue'),
      },
      {
        path: '/units/create',
        name: 'inventory-units-create',
        component: () => import('pages/inventory/unit/UnitForm.vue'),
      },
      {
        path: '/units/:id/edit',
        name: 'inventory-units-id-edit',
        component: () => import('pages/inventory/unit/UnitForm.vue'),
      },
      {
        path: '/categories',
        name: 'inventory-categories',
        component: () => import('pages/inventory/product/category/InventoryCategoryList.vue'),
      },
      {
        path: '/categories/create',
        name: 'inventory-categories-create',
        component: () => import('pages/inventory/product/category/InventoryCategoryForm.vue'),
      },
      {
        path: '/categories/:id/edit',
        name: 'inventory-categories-id-edit',
        component: () => import('pages/inventory/product/category/InventoryCategoryForm.vue'),
      },
      {
        path: '/brands',
        name: 'inventory-brands',
        component: () => import('pages/inventory/product/brand/BrandList.vue'),
      },
      {
        path: '/brands/create',
        name: 'inventory-brands-create',
        component: () => import('pages/inventory/product/brand/BrandForm.vue'),
      },
      {
        path: '/brands/:id/edit',
        name: 'inventory-brands-id-edit',
        component: () => import('pages/inventory/product/brand/BrandForm.vue'),
      },
      {
        path: '/opening-stock',
        name: 'inventory-opening-stock',
        component: () => import('pages/inventory/item/opening-stock/ItemOpeningStockList.vue'),
      },
      {
        path: '/opening-stock/create',
        name: 'inventory-opening-stock-create',
        component: () => import('pages/inventory/item/opening-stock/ItemOpeningStockForm.vue'),
      },
      // {
      //   path: '/stock-ledger',
      //   name: 'inventory-stock-ledger',
      //   component: () => import('pages/inventory/stock-ledger/StockLedger.vue'),
      // },
      {
        path: '/adjustments',
        name: 'inventory-adjustments',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentList.vue'),
      },
      {
        path: '/adjustments/create',
        name: 'inventory-adjustments-create',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentForm.vue'),
      },
      {
        path: '/adjustments/:id',
        name: 'inventory-adjustments-id',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentDetail.vue'),
      },
      {
        path: '/adjustments/:id/edit',
        name: 'inventory-adjustments-id-edit',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentForm.vue'),
      },
      {
        path: '/bill-of-materials',
        name: 'inventory-bill-of-materials',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialList.vue'),
      },
      {
        path: '/bill-of-materials/create',
        name: 'inventory-bill-of-materials-create',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'),
      },
      {
        path: '/bill-of-materials/:id/edit',
        name: 'inventory-bill-of-materials-id-edit',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'),
      },
      {
        path: '/conversions',
        name: 'inventory-conversions',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionList.vue'),
      },
      {
        path: '/conversions/create',
        name: 'inventory-conversions-create',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'),
      },
      {
        path: '/conversions/:id',
        name: 'inventory-conversions-id',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionDetail.vue'),
      },
      {
        path: '/conversions/:id/edit',
        name: 'inventory-conversions-id-edit',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'),
      },
    ],
  },
  // {
  //   path: '/journal-entry/:slugUrl',
  //   name: 'journal-entry',
  //   component: () => import('pages/journal-entry/[slugUrl].vue'),
  // },
  {
    path: '/party',
    name: 'party',
    children: [
      {
        path: '/parties',
        name: 'party-list',
        component: () => import('pages/party/PartyList.vue'),
      },
      {
        path: '/parties/create',
        name: 'party-create',
        component: () => import('pages/party/PartyForm.vue'),
      },
      {
        path: '/parties/:id/edit',
        name: 'party-edit',
        component: () => import('pages/party/PartyForm.vue'),
      },
      {
        path: '/parties/:id/account',
        name: 'party-account',
        component: () => import('pages/party/PartyAccount.vue'),
      },
      {
        path: '/parties/:id/alias',
        name: 'party-alias',
        component: () => import('pages/party/PartyAlias.vue'),
      },
      {
        path: '/parties/:id/representative',
        name: 'party-representative',
        component: () => import('pages/party/PartyRepresentative.vue'),
      },
      {
        path: '/customers',
        name: 'customer-list',
        component: () => import('pages/party/CustomerList.vue'),
      },
      {
        path: '/suppliers',
        name: 'supplier-list',
        component: () => import('pages/party/SupplierList.vue'),
      },
    ],
  },
  {
    path: '/payment-receipts',
    name: 'payment-receipts',
    children: [
      {
        path: '',
        name: 'payment-receipts-list',
        component: () => import('pages/payment-receipt/PaymentReceiptList.vue'),
      },
      {
        path: '/create',
        name: 'payment-receipts-create',
        component: () => import('pages/payment-receipt/PaymentReceiptForm.vue'),
      },
      {
        path: '/:id',
        name: 'payment-receipts-id',
        component: () => import('pages/payment-receipt/PaymentReceiptView.vue'),
      },
      {
        path: '/:id/edit',
        name: 'payment-receipts-id-edit',
        component: () => import('pages/payment-receipt/PaymentReceiptForm.vue'),
      },
    ],
  },
  {
    path: '/reports',
    name: 'reports',
    children: [
      {
        path: '/ageing',
        name: 'reports-ageing',
        component: () => import('pages/report/AgeingReport.vue'),
      },
      {
        path: '/balance-sheet',
        name: 'reports-balance-sheet',
        component: () => import('pages/report/BalanceSheet.vue'),
      },
      {
        path: '/category-tree',
        name: 'reports-category-tree',
        component: () => import('pages/report/CategoryTree.vue'),
      },
      {
        path: '/collection',
        name: 'reports-collection',
        component: () => import('pages/report/CollectionReport.vue'),
      },
      {
        path: '/day-book',
        name: 'reports-day-book',
        component: () => import('pages/report/DayBook.vue'),
      },
      {
        path: '/income-statement',
        name: 'reports-income-statement',
        component: () => import('pages/report/IncomeStatement.vue'),
      },
      {
        path: '/ratio-analysis',
        name: 'reports-ratio-analysis',
        component: () => import('pages/report/RatioAnalysis.vue'),
      },
      {
        path: '/sales-by-category',
        name: 'reports-sales-by-category',
        component: () => import('pages/report/SalesByCategory.vue'),
      },
      {
        path: '/stock-trial-balance',
        name: 'reports-stock-trial-balance',
        component: () => import('pages/report/StockTrialBalance.vue'),
      },
      {
        path: '/tax-summary',
        name: 'reports-tax-summary',
        component: () => import('pages/report/TaxSummary.vue'),
      },
      {
        path: '/transactions',
        name: 'reports-transactions',
        component: () => import('pages/report/TransactionsList.vue'),
      },
      {
        path: '/trial-balance',
        name: 'reports-trial-balance',
        component: () => import('pages/report/TrialBalance.vue'),
      },
      // {
      //   path: '/stock-movement',
      //   name: 'reports-stock-movement',
      //   component: () => import('pages/report/StockMovement.vue'),
      // },
    ],
  },
]

export default routes
