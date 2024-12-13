import type { RouteRecordRaw } from 'vue-router'

const companyRoutes: RouteRecordRaw[] = [
  {
    path: 'dashboard',
    name: 'company-dashboard',
    component: () => import('pages/Dashboard.vue'),
  },
  {
    path: 'account',
    name: 'company-account',
    children: [
      {
        path: 'categories',
        name: 'company-account-categories',
        component: () => import('pages/account/category/CategoryList.vue'),
      },
      {
        path: 'categories/create',
        name: 'company-account-categories-create',
        component: () => import('pages/account/category/CategoryForm.vue'),
      },
      {
        path: 'categories/:id/edit',
        name: 'company-account-categories-id',
        component: () => import('pages/account/category/CategoryForm.vue'),
      },
      {
        path: 'journal-vouchers',
        name: 'company-account-journal-vouchers',
        component: () => import('pages/account/journal-voucher/JournalVoucherList.vue'),
      },
      {
        path: 'journal-vouchers/create',
        name: 'company-account-journal-vouchers-create',
        component: () => import('pages/account/journal-voucher/JournalVoucherForm.vue'),
      },
      {
        path: 'journal-vouchers/:id',
        name: 'company-account-journal-vouchers-id',
        component: () => import('pages/account/journal-voucher/JournalVoucherDetail.vue'),
      },
      {
        path: 'journal-vouchers/:id/edit',
        name: 'company-account-journal-vouchers-id-edit',
        component: () => import('pages/account/journal-voucher/JournalVoucherForm.vue'),
      },
      {
        path: 'ledgers',
        name: 'company-account-ledgers',
        component: () => import('pages/account/ledger/LedgerList.vue'),
      },
      {
        path: 'ledgers/create',
        name: 'company-account-ledgers-create',
        component: () => import('pages/account/ledger/LedgerForm.vue'),
      },
      {
        path: 'ledgers/:id',
        name: 'company-account-ledgers-id',
        component: () => import('pages/account/ledger/LedgerDetail.vue'),
      },
      {
        path: 'ledgers/:id/edit',
        name: 'company-account-ledgers-id-edit',
        component: () => import('pages/account/ledger/LedgerForm.vue'),
      },
      {
        path: 'opening-balances',
        name: 'company-account-opening-balances',
        component: () => import('pages/account/opening-balance/OpeningBalanceList.vue'),
      },
      {
        path: 'opening-balances/create',
        name: 'company-account-opening-balances-create',
        component: () => import('pages/account/opening-balance/OpeningBalanceForm.vue'),
      },
      {
        path: 'opening-balances/:id/edit',
        name: 'company-account-opening-balances-id-edit',
        component: () => import('pages/account/opening-balance/OpeningBalanceForm.vue'),
      },
    ],
  },
  {
    path: 'banking',
    name: 'company-banking',
    children: [
      {
        path: 'bank-accounts',
        name: 'company-banking-bank-accounts',
        component: () => import('pages/bank/account/AccountList.vue'),
      },
      {
        path: 'bank-accounts/create',
        name: 'company-banking-bank-accounts-create',
        component: () => import('pages/bank/account/AccountForm.vue'),
      },
      {
        path: 'bank-accounts/:id/edit',
        name: 'company-banking-bank-accounts-id-edit',
        component: () => import('pages/bank/account/AccountForm.vue'),
      },
      {
        path: 'cash-deposits',
        name: 'company-banking-cash-deposits',
        component: () => import('pages/bank/cash-deposit/CashDepositList.vue'),
      },
      {
        path: 'cash-deposits/create',
        name: 'company-banking-cash-deposits-create',
        component: () => import('pages/bank/cash-deposit/CashDepositForm.vue'),
      },
      {
        path: 'cash-deposits/:id/edit',
        name: 'company-banking-cash-deposits-id-edit',
        component: () => import('pages/bank/cash-deposit/CashDepositForm.vue'),
      },
      // {
      //   path: 'cash-withdrawals',
      //   name: 'company-banking-cash-withdrawals',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalList.vue'),
      // },
      // {
      //   path: 'cash-withdrawals/create',
      //   name: 'company-banking-cash-withdrawals-create',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalForm.vue'),
      // },
      // {
      //   path: 'cash-withdrawals/:id',
      //   name: 'company-banking-cash-withdrawals-id',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalDetail.vue'),
      // },
      // {
      //   path: 'cash-withdrawals/:id/edit',
      //   name: 'company-banking-cash-withdrawals-id-edit',
      //   component: () => import('pages/bank/cash-withdrawal/CashWithdrawalForm.vue'),
      // },
      {
        path: 'cheque-deposits',
        name: 'company-banking-cheque-deposits',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositList.vue'),
      },
      {
        path: 'cheque-deposits/create',
        name: 'company-banking-cheque-deposits-create',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositForm.vue'),
      },
      {
        path: 'cheque-deposits/:id/edit',
        name: 'company-banking-cheque-deposits-id-edit',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositForm.vue'),
      },
      {
        path: 'cheque-issues',
        name: 'company-banking-cheque-issues',
        component: () => import('pages/bank/cheque-issue/ChequeIssueList.vue'),
      },
      {
        path: 'cheque-issues/create',
        name: 'company-banking-cheque-issues-create',
        component: () => import('pages/bank/cheque-issue/ChequeIssueForm.vue'),
      },
      {
        path: 'cheque-issues/:id/edit',
        name: 'company-banking-cheque-issues-id-edit',
        component: () => import('pages/bank/cheque-issue/ChequeIssueForm.vue'),
      },
      // {
      //   path: 'cheque-withdrawals',
      //   name: 'company-banking-cheque-withdrawals',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalList.vue'),
      // },
      // {
      //   path: 'cheque-withdrawals/create',
      //   name: 'company-banking-cheque-withdrawals-create',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalForm.vue'),
      // },
      // {
      //   path: 'cheque-withdrawals/:id',
      //   name: 'company-banking-cheque-withdrawals-id',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalDetail.vue'),
      // },
      // {
      //   path: 'cheque-withdrawals/:id/edit',
      //   name: 'company-banking-cheque-withdrawals-id-edit',
      //   component: () => import('pages/bank/cheque-withdrawal/ChequeWithdrawalForm.vue'),
      // },
      {
        path: 'fund-transfers',
        name: 'company-banking-fund-transfers',
        component: () => import('pages/bank/fund-transfer/FundTransferList.vue'),
      },
      {
        path: 'fund-transfers/create',
        name: 'company-banking-fund-transfers-create',
        component: () => import('pages/bank/fund-transfer/FundTransferForm.vue'),
      },
      {
        path: 'fund-transfers/:id/edit',
        name: 'company-banking-fund-transfers-id-edit',
        component: () => import('pages/bank/fund-transfer/FundTransferForm.vue'),
      },
    ],
  },
  {
    path: 'purchase',
    name: 'company-purchase',
    children: [
      {
        path: 'debit-notes',
        name: 'company-purchase-debit-notes',
        component: () => import('pages/purchase/debit-notes/DebitNotesList.vue'),
      },
      {
        path: 'debit-notes/create',
        name: 'company-purchase-debit-notes-create',
        component: () => import('pages/purchase/debit-notes/DebitNotesForm.vue'),
      },
      {
        path: 'debit-notes/:id/edit',
        name: 'company-purchase-debit-notes-id-edit',
        component: () => import('pages/purchase/debit-notes/DebitNotesForm.vue'),
      },
      {
        path: 'discounts',
        name: 'company-purchase-discounts',
        component: () => import('pages/purchase/discounts/PurchaseDiscountList.vue'),
      },
      {
        path: 'discounts/create',
        name: 'company-purchase-discounts-create',
        component: () => import('pages/purchase/discounts/PurchaseDiscountForm.vue'),
      },
      {
        path: 'discounts/:id/edit',
        name: 'company-purchase-discounts-id-edit',
        component: () => import('pages/purchase/discounts/PurchaseDiscountForm.vue'),
      },
      {
        path: 'purchase-book',
        name: 'company-purchase-book',
        component: () => import('pages/purchase/purchase-book/PurchaseBookList.vue'),
      },
      {
        path: 'purchase-orders',
        name: 'company-purchase-orders',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderList.vue'),
      },
      {
        path: 'purchase-orders/create',
        name: 'company-purchase-orders-create',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderForm.vue'),
      },
      {
        path: 'purchase-orders/:id/edit',
        name: 'company-purchase-orders-id-edit',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderForm.vue'),
      },
      {
        path: 'purchase-vouchers',
        name: 'company-purchase-vouchers',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherList.vue'),
      },
      {
        path: 'purchase-vouchers/create',
        name: 'company-purchase-vouchers-create',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
      },
      {
        path: 'purchase-vouchers/:id',
        name: 'company-purchase-vouchers-id',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherDetail.vue'),
      },
      {
        path: 'purchase-vouchers/:id/edit',
        name: 'company-purchase-vouchers-id-edit',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
      },
    ],
  },
  {
    path: 'sales',
    name: 'company-sales',
    children: [
      {
        path: 'agents',
        name: 'company-sales-agents',
        component: () => import('pages/sales/agent/SalesAgentList.vue'),
      },
      {
        path: 'agents/create',
        name: 'company-sales-agents-create',
        component: () => import('pages/sales/agent/SalesAgentForm.vue'),
      },
      {
        path: 'agents/:id/edit',
        name: 'company-sales-agents-id-edit',
        component: () => import('pages/sales/agent/SalesAgentForm.vue'),
      },
      {
        path: 'sales-book',
        name: 'company-sales-book',
        component: () => import('pages/sales/book/SalesBookList.vue'),
      },
      {
        path: 'challans',
        name: 'company-sales-challans',
        component: () => import('pages/sales/challan/ChallanList.vue'),
      },
      {
        path: 'challans/create',
        name: 'company-sales-challans-create',
        component: () => import('pages/sales/challan/ChallanForm.vue'),
      },
      {
        path: 'challans/:id/edit',
        name: 'company-sales-challans-id-edit',
        component: () => import('pages/sales/challan/ChallanForm.vue'),
      },
      {
        path: 'credit-notes',
        name: 'company-sales-credit-notes',
        component: () => import('pages/sales/credit-note/CreditNoteList.vue'),
      },
      {
        path: 'credit-notes/create',
        name: 'company-sales-credit-notes-create',
        component: () => import('pages/sales/credit-note/CreditNoteForm.vue'),
      },
      {
        path: 'credit-notes/:id',
        name: 'company-sales-credit-notes-id',
        component: () => import('pages/sales/credit-note/CreditNoteDetail.vue'),
      },
      {
        path: 'credit-notes/:id/edit',
        name: 'company-sales-credit-notes-id-edit',
        component: () => import('pages/sales/credit-note/CreditNoteForm.vue'),
      },
      {
        path: 'discounts',
        name: 'company-sales-discounts',
        component: () => import('pages/sales/discount/SalesDiscountList.vue'),
      },
      {
        path: 'discounts/create',
        name: 'company-sales-discounts-create',
        component: () => import('pages/sales/discount/SalesDiscountForm.vue'),
      },
      {
        path: 'discounts/:id/edit',
        name: 'company-sales-discounts-id-edit',
        component: () => import('pages/sales/discount/SalesDiscountForm.vue'),
      },
      {
        path: 'pos',
        name: 'company-sales-pos',
        component: () => import('pages/sales/pos/PosForm.vue'),
      },
      {
        path: 'sales-vouchers',
        name: 'company-sales-vouchers',
        component: () => import('pages/sales/sales-voucher/SalesVoucherList.vue'),
      },
      {
        path: 'sales-vouchers/create',
        name: 'company-sales-vouchers-create',
        component: () => import('pages/sales/sales-voucher/SalesVoucherForm.vue'),
      },
      {
        path: 'sales-vouchers/:id',
        name: 'company-sales-vouchers-id',
        component: () => import('pages/sales/sales-voucher/SalesVoucherDetail.vue'),
      },
      {
        path: 'sales-vouchers/:id/edit',
        name: 'company-sales-vouchers-id-edit',
        component: () => import('pages/sales/sales-voucher/SalesVoucherForm.vue'),
      },
      {
        path: 'sales-vouchers/:id/material',
        name: 'company-sales-vouchers-id-edit',
        component: () => import('pages/sales/sales-voucher/SalesVoucherMV.vue'),
      },
    ],
  },
  {
    path: 'settings',
    name: 'company-settings',
    children: [
      {
        path: 'accounts-closing',
        name: 'company-settings-accounts-closing',
        component: () => import('pages/settings/AccountsClosing.vue'),
      },
      {
        path: 'import-export',
        name: 'company-settings-import-export',
        component: () => import('pages/settings/ImportExport.vue'),
      },
      {
        path: 'inventory-settings',
        name: 'company-settings-inventory',
        component: () => import('pages/settings/InventorySettings.vue'),
      },
      {
        path: 'item-merge',
        name: 'company-settings-item-merge',
        component: () => import('pages/settings/ItemMerge.vue'),
      },
      {
        path: 'payment-modes',
        name: 'company-settings-payment-modes',
        component: () => import('pages/settings/PaymentModeList.vue'),
      },
      {
        path: 'payment-modes/create',
        name: 'company-settings-payment-modes-create',
        component: () => import('pages/settings/PaymentModeForm.vue'),
      },
      {
        path: 'payment-modes/:id/edit',
        name: 'company-settings-payment-modes-id-edit',
        component: () => import('pages/settings/PaymentModeForm.vue'),
      },
      {
        path: 'purchase-settings',
        name: 'company-settings-purchase',
        component: () => import('pages/settings/PurchaseSetting.vue'),
      },
      {
        path: 'sales-settings',
        name: 'company-settings-sales',
        component: () => import('pages/settings/SalesSetting.vue'),
      },
      {
        path: 'audit-logs',
        name: 'company-settings-audit-logs',
        component: () => import('pages/settings/auditlog/AuditLogList.vue'),
      },
      {
        path: 'audit-logs/:id',
        name: 'company-settings-audit-logs-id',
        component: () => import('pages/settings/auditlog/AuditLogDetail.vue'),
      },
      {
        path: 'dashboard-widgets',
        name: 'company-settings-dashboard-widgets',
        component: () => import('pages/settings/widgets/WidgetList.vue'),
      },
      {
        path: 'dashboard-widgets/add',
        name: 'company-settings-dashboard-widgets-add',
        component: () => import('pages/settings/widgets/WidgetForm.vue'),
      },
      {
        path: 'dashboard-widgets/:id/edit',
        name: 'company-settings-dashboard-widgets-id-edit',
        component: () => import('pages/settings/widgets/WidgetForm.vue'),
      },
    ],
  },
  {
    path: 'tax',
    name: 'company-tax',
    children: [
      {
        path: 'payments',
        name: 'company-tax-payments',
        component: () => import('pages/tax/payments/TaxPaymentList.vue'),
      },
      {
        path: 'payments/create',
        name: 'company-tax-payments-create',
        component: () => import('pages/tax/payments/TaxPaymentForm.vue'),
      },
      {
        path: 'payments/:id/edit',
        name: 'company-tax-payments-id-edit',
        component: () => import('pages/tax/payments/TaxPaymentForm.vue'),
      },
      // {
      //   path: 'schemes',
      //   name: 'company-tax-schemes',
      //   component: () => import('pages/tax/scheme/SchemeList.vue'),
      // },
      // {
      //   path: 'schemes/create',
      //   name: 'company-tax-schemes-create',
      //   component: () => import('pages/tax/scheme/SchemeForm.vue'),
      // },
      // {
      //   path: 'schemes/:id',
      //   name: 'company-tax-schemes-id',
      //   component: () => import('pages/tax/scheme/SchemeDetail.vue'),
      // },
      // {
      //   path: 'schemes/:id/edit',
      //   name: 'company-tax-schemes-id-edit',
      //   component: () => import('pages/tax/scheme/SchemeForm.vue'),
      // },
      // {
      //   path: 'periodic-summary',
      //   name: 'company-tax-periodic-summary',
      //   component: () => import('pages/tax/periodic-summary/PeriodicSummary.vue'),
      // },
    ],
  },
  {
    path: 'inventory',
    name: 'company-inventory',
    children: [
      {
        path: 'items',
        name: 'company-inventory-items',
        component: () => import('pages/inventory/item/ItemList.vue'),
      },
      {
        path: 'items/create',
        name: 'company-inventory-items-create',
        component: () => import('pages/inventory/item/ItemForm.vue'),
      },
      {
        path: 'items/:id',
        name: 'company-inventory-items-id',
        component: () => import('pages/inventory/item/ItemDetail.vue'),
      },
      {
        path: 'items/:id/edit',
        name: 'company-inventory-items-id-edit',
        component: () => import('pages/inventory/item/ItemForm.vue'),
      },
      // {
      //   path: 'products',
      //   name: 'company-inventory-products',
      //   component: () => import('pages/inventory/product/ProductList.vue'),
      // },
      // {
      //   path: 'products/create',
      //   name: 'company-inventory-products-create',
      //   component: () => import('pages/inventory/product/ProductForm.vue'),
      // },
      // {
      //   path: 'products/:id',
      //   name: 'company-inventory-products-id',
      //   component: () => import('pages/inventory/product/ProductDetail.vue'),
      // },
      // {
      //   path: 'products/:id/edit',
      //   name: 'company-inventory-products-id-edit',
      //   component: () => import('pages/inventory/product/ProductForm.vue'),
      // },
      {
        path: 'units',
        name: 'company-inventory-units',
        component: () => import('pages/inventory/unit/UnitList.vue'),
      },
      {
        path: 'units/create',
        name: 'company-inventory-units-create',
        component: () => import('pages/inventory/unit/UnitForm.vue'),
      },
      {
        path: 'units/:id/edit',
        name: 'company-inventory-units-id-edit',
        component: () => import('pages/inventory/unit/UnitForm.vue'),
      },
      {
        path: 'categories',
        name: 'company-inventory-categories',
        component: () => import('pages/inventory/product/category/InventoryCategoryList.vue'),
      },
      {
        path: 'categories/create',
        name: 'company-inventory-categories-create',
        component: () => import('pages/inventory/product/category/InventoryCategoryForm.vue'),
      },
      {
        path: 'categories/:id/edit',
        name: 'company-inventory-categories-id-edit',
        component: () => import('pages/inventory/product/category/InventoryCategoryForm.vue'),
      },
      {
        path: 'brands',
        name: 'company-inventory-brands',
        component: () => import('pages/inventory/product/brand/BrandList.vue'),
      },
      {
        path: 'brands/create',
        name: 'company-inventory-brands-create',
        component: () => import('pages/inventory/product/brand/BrandForm.vue'),
      },
      {
        path: 'brands/:id/edit',
        name: 'company-inventory-brands-id-edit',
        component: () => import('pages/inventory/product/brand/BrandForm.vue'),
      },
      {
        path: 'opening-stock',
        name: 'company-inventory-opening-stock',
        component: () => import('pages/inventory/item/opening-stock/ItemOpeningStockList.vue'),
      },
      {
        path: 'opening-stock/create',
        name: 'company-inventory-opening-stock-create',
        component: () => import('pages/inventory/item/opening-stock/ItemOpeningStockForm.vue'),
      },
      // {
      //   path: 'stock-ledger',
      //   name: 'company-inventory-stock-ledger',
      //   component: () => import('pages/inventory/stock-ledger/StockLedger.vue'),
      // },
      {
        path: 'adjustments',
        name: 'company-inventory-adjustments',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentList.vue'),
      },
      {
        path: 'adjustments/create',
        name: 'company-inventory-adjustments-create',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentForm.vue'),
      },
      {
        path: 'adjustments/:id',
        name: 'company-inventory-adjustments-id',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentDetail.vue'),
      },
      {
        path: 'adjustments/:id/edit',
        name: 'company-inventory-adjustments-id-edit',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentForm.vue'),
      },
      {
        path: 'bill-of-materials',
        name: 'company-inventory-bill-of-materials',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialList.vue'),
      },
      {
        path: 'bill-of-materials/create',
        name: 'company-inventory-bill-of-materials-create',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'),
      },
      {
        path: 'bill-of-materials/:id/edit',
        name: 'company-inventory-bill-of-materials-id-edit',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'),
      },
      {
        path: 'conversions',
        name: 'company-inventory-conversions',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionList.vue'),
      },
      {
        path: 'conversions/create',
        name: 'company-inventory-conversions-create',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'),
      },
      {
        path: 'conversions/:id',
        name: 'company-inventory-conversions-id',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionDetail.vue'),
      },
      {
        path: 'conversions/:id/edit',
        name: 'company-inventory-conversions-id-edit',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'),
      },
    ],
  },
  // {
  //   path: 'journal-entry/:slugUrl',
  //   name: 'company-journal-entry',
  //   component: () => import('pages/journal-entry/[slugUrl].vue'),
  // },
  {
    path: 'party',
    name: 'company-party',
    children: [
      {
        path: 'parties',
        name: 'company-party-list',
        component: () => import('pages/party/PartyList.vue'),
      },
      {
        path: 'parties/create',
        name: 'company-party-create',
        component: () => import('pages/party/PartyForm.vue'),
      },
      {
        path: 'parties/:id/edit',
        name: 'company-party-edit',
        component: () => import('pages/party/PartyForm.vue'),
      },
      {
        path: 'parties/:id/account',
        name: 'company-party-account',
        component: () => import('pages/party/PartyAccount.vue'),
      },
      {
        path: 'parties/:id/alias',
        name: 'company-party-alias',
        component: () => import('pages/party/PartyAlias.vue'),
      },
      {
        path: 'parties/:id/representative',
        name: 'company-party-representative',
        component: () => import('pages/party/PartyRepresentative.vue'),
      },
      {
        path: 'customers',
        name: 'company-customer-list',
        component: () => import('pages/party/CustomerList.vue'),
      },
      {
        path: 'suppliers',
        name: 'company-supplier-list',
        component: () => import('pages/party/SupplierList.vue'),
      },
    ],
  },
  {
    path: 'payment-receipts',
    name: 'company-payment-receipts',
    children: [
      {
        path: '',
        name: 'company-payment-receipts-list',
        component: () => import('pages/payment-receipt/PaymentReceiptList.vue'),
      },
      {
        path: 'create',
        name: 'company-payment-receipts-create',
        component: () => import('pages/payment-receipt/PaymentReceiptForm.vue'),
      },
      {
        path: ':id',
        name: 'company-payment-receipts-id',
        component: () => import('pages/payment-receipt/PaymentReceiptView.vue'),
      },
      {
        path: ':id/edit',
        name: 'company-payment-receipts-id-edit',
        component: () => import('pages/payment-receipt/PaymentReceiptForm.vue'),
      },
    ],
  },
  {
    path: 'reports',
    name: 'company-reports',
    children: [
      {
        path: 'ageing',
        name: 'company-reports-ageing',
        component: () => import('pages/report/AgeingReport.vue'),
      },
      {
        path: 'balance-sheet',
        name: 'company-reports-balance-sheet',
        component: () => import('pages/report/BalanceSheet.vue'),
      },
      {
        path: 'category-tree',
        name: 'company-reports-category-tree',
        component: () => import('pages/report/CategoryTree.vue'),
      },
      {
        path: 'collection',
        name: 'company-reports-collection',
        component: () => import('pages/report/CollectionReport.vue'),
      },
      {
        path: 'day-book',
        name: 'company-reports-day-book',
        component: () => import('pages/report/DayBook.vue'),
      },
      {
        path: 'income-statement',
        name: 'company-reports-income-statement',
        component: () => import('pages/report/IncomeStatement.vue'),
      },
      {
        path: 'ratio-analysis',
        name: 'company-reports-ratio-analysis',
        component: () => import('pages/report/RatioAnalysis.vue'),
      },
      {
        path: 'sales-by-category',
        name: 'company-reports-sales-by-category',
        component: () => import('pages/report/SalesByCategory.vue'),
      },
      {
        path: 'stock-trial-balance',
        name: 'company-reports-stock-trial-balance',
        component: () => import('pages/report/StockTrialBalance.vue'),
      },
      {
        path: 'tax-summary',
        name: 'company-reports-tax-summary',
        component: () => import('pages/report/TaxSummary.vue'),
      },
      {
        path: 'transactions',
        name: 'company-reports-transactions',
        component: () => import('pages/report/TransactionsList.vue'),
      },
      {
        path: 'trial-balance',
        name: 'company-reports-trial-balance',
        component: () => import('pages/report/TrialBalance.vue'),
      },
      // {
      //   path: 'stock-movement',
      //   name: 'company-reports-stock-movement',
      //   component: () => import('pages/report/StockMovement.vue'),
      // },
    ],
  },
]

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
    path: '/login',
    name: 'login-page',
    component: () => import('pages/LoginPage.vue'),
  },
  {
    path: '/:company',
    name: 'company',
    children: companyRoutes,
  },
]

export default routes
