import type { RouteRecordRaw } from 'vue-router'

const companyRoutes: RouteRecordRaw[] = [
  {
    path: 'dashboard',
    name: 'company-dashboard',
    component: () => import('pages/Dashboard.vue'),
    meta: {
      breadcrumbs: ['Dashboard'],
    },
  },
  {
    path: 'account',
    name: 'company-account',
    meta: {
      breadcrumbs: ['Account'],
    },
    children: [
      {
        path: 'categories',
        name: 'company-account-categories',
        component: () => import('pages/account/category/CategoryList.vue'),
        meta: {
          breadcrumbs: ['Account', 'Categories'],
        },
      },
      {
        path: 'categories/create',
        name: 'company-account-categories-create',
        component: () => import('pages/account/category/CategoryForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Categories', 'Create'],
        },
      },
      {
        path: 'categories/:id',
        name: 'company-account-categories-id',
        component: () => import('pages/account/category/CategoryForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Categories', 'Edit'],
        },
      },
      {
        path: 'categories/:id/edit',
        name: 'company-account-categories-id-edit',
        component: () => import('pages/account/category/CategoryForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Categories', 'Edit'],
        },
      },
      {
        path: 'journal-vouchers',
        name: 'company-account-journal-vouchers',
        component: () => import('pages/account/journal-voucher/JournalVoucherList.vue'),
        meta: {
          breadcrumbs: ['Account', 'Journal Vouchers'],
        },
      },
      {
        path: 'journal-vouchers/create',
        name: 'company-account-journal-vouchers-create',
        component: () => import('pages/account/journal-voucher/JournalVoucherForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Journal Vouchers', 'Create'],
        },
      },
      {
        path: 'journal-vouchers/:id',
        name: 'company-account-journal-vouchers-id',
        component: () => import('pages/account/journal-voucher/JournalVoucherDetail.vue'),
        meta: {
          breadcrumbs: ['Account', 'Journal Vouchers', 'Detail'],
        },
      },
      {
        path: 'journal-vouchers/:id/edit',
        name: 'company-account-journal-vouchers-id-edit',
        component: () => import('pages/account/journal-voucher/JournalVoucherForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Journal Vouchers', 'Edit'],
        },
      },
      {
        path: 'ledgers',
        name: 'company-account-ledgers',
        component: () => import('pages/account/ledger/LedgerList.vue'),
        meta: {
          breadcrumbs: ['Account', 'Ledgers'],
        },
      },
      {
        path: 'ledgers/create',
        name: 'company-account-ledgers-create',
        component: () => import('pages/account/ledger/LedgerForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Ledgers', 'Create'],
        },
      },
      {
        path: 'ledgers/:id',
        name: 'company-account-ledgers-id',
        component: () => import('pages/account/ledger/LedgerDetail.vue'),
        meta: {
          breadcrumbs: ['Account', 'Ledgers', 'Detail'],
        },
      },
      {
        path: 'ledgers/:id/edit',
        name: 'company-account-ledgers-id-edit',
        component: () => import('pages/account/ledger/LedgerForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Ledgers', 'Edit'],
        },
      },
      {
        path: 'opening-balances',
        name: 'company-account-opening-balances',
        component: () => import('pages/account/opening-balance/OpeningBalanceList.vue'),
        meta: {
          breadcrumbs: ['Account', 'Opening Balances'],
        },
      },
      {
        path: 'opening-balances/create',
        name: 'company-account-opening-balances-create',
        component: () => import('pages/account/opening-balance/OpeningBalanceForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Opening Balances', 'Create'],
        },
      },
      {
        path: 'opening-balances/:id/edit',
        name: 'company-account-opening-balances-id-edit',
        component: () => import('pages/account/opening-balance/OpeningBalanceForm.vue'),
        meta: {
          breadcrumbs: ['Account', 'Opening Balances', 'Edit'],
        },
      },
    ],
  },
  {
    path: 'banking',
    name: 'company-banking',
    meta: {
      breadcrumbs: ['Banking'],
    },
    children: [
      {
        path: 'bank-accounts',
        name: 'company-banking-bank-accounts',
        component: () => import('pages/bank/account/AccountList.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Bank Accounts'],
        },
      },
      {
        path: 'bank-accounts/create',
        name: 'company-banking-bank-accounts-create',
        component: () => import('pages/bank/account/AccountForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Bank Accounts', 'Create'],
        },
      },
      {
        path: 'bank-accounts/:id',
        name: 'company-banking-bank-accounts-id',
        component: () => import('pages/bank/account/AccountForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Bank Accounts', 'Edit'],
        },
      },
      {
        path: 'bank-accounts/:id/edit',
        name: 'company-banking-bank-accounts-id-edit',
        component: () => import('pages/bank/account/AccountForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Bank Accounts', 'Edit'],
        },
      },
      {
        path: 'cash-deposits',
        name: 'company-banking-cash-deposits',
        component: () => import('pages/bank/cash-deposit/CashDepositList.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cash Deposits'],
        },
      },
      {
        path: 'cash-deposits/create',
        name: 'company-banking-cash-deposits-create',
        component: () => import('pages/bank/cash-deposit/CashDepositForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cash Deposits', 'Create'],
        },
      },
      {
        path: 'cash-deposits/:id/edit',
        name: 'company-banking-cash-deposits-id-edit',
        component: () => import('pages/bank/cash-deposit/CashDepositForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cash Deposits', 'Edit'],
        },
      },
      {
        path: 'cheque-deposits',
        name: 'company-banking-cheque-deposits',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositList.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cheque Deposits'],
        },
      },
      {
        path: 'cheque-deposits/create',
        name: 'company-banking-cheque-deposits-create',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cheque Deposits', 'Create'],
        },
      },
      {
        path: 'cheque-deposits/:id/edit',
        name: 'company-banking-cheque-deposits-id-edit',
        component: () => import('pages/bank/cheque-deposit/ChequeDepositForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cheque Deposits', 'Edit'],
        },
      },
      {
        path: 'cheque-issues',
        name: 'company-banking-cheque-issues',
        component: () => import('pages/bank/cheque-issue/ChequeIssueList.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cheque Issues'],
        },
      },
      {
        path: 'cheque-issues/create',
        name: 'company-banking-cheque-issues-create',
        component: () => import('pages/bank/cheque-issue/ChequeIssueForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cheque Issues', 'Create'],
        },
      },
      {
        path: 'cheque-issues/:id/edit',
        name: 'company-banking-cheque-issues-id-edit',
        component: () => import('pages/bank/cheque-issue/ChequeIssueForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Cheque Issues', 'Edit'],
        },
      },
      {
        path: 'fund-transfers',
        name: 'company-banking-fund-transfers',
        component: () => import('pages/bank/fund-transfer/FundTransferList.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Fund Transfers'],
        },
      },
      {
        path: 'fund-transfers/create',
        name: 'company-banking-fund-transfers-create',
        component: () => import('pages/bank/fund-transfer/FundTransferForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Fund Transfers', 'Create'],
        },
      },
      {
        path: 'fund-transfers/:id/edit',
        name: 'company-banking-fund-transfers-id-edit',
        component: () => import('pages/bank/fund-transfer/FundTransferForm.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Fund Transfers', 'Edit'],
        },
      },
      {
        path: 'reconciliation',
        name: 'company-banking-reconciliation',
        component: () => import('pages/bank/reconciliation/IndexPage.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Reconciliation'],
        },
      },
      {
        path: 'reconciliation/reconcile',
        name: 'company-banking-reconciliation-reconcile',
        component: () => import('pages/bank/reconciliation/ReconcileTransactions.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Reconciliation', 'Reconcile'],
        },
      },
      {
        path: 'reconciliation/:id',
        name: 'company-banking-reconciliation-id',
        component: () => import('pages/bank/reconciliation/StatementDetail.vue'),
        meta: {
          breadcrumbs: ['Banking', 'Reconciliation', 'Detail'],
        },
      },
    ],
  },
  {
    path: 'purchase',
    name: 'company-purchase',
    meta: {
      breadcrumbs: ['Purchase'],
    },
    children: [
      {
        path: 'debit-notes',
        name: 'company-purchase-debit-notes',
        component: () => import('pages/purchase/debit-notes/DebitNotesList.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Debit Notes'],
        },
      },
      {
        path: 'debit-notes/create',
        name: 'company-purchase-debit-notes-create',
        component: () => import('pages/purchase/debit-notes/DebitNotesForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Debit Notes', 'Create'],
        },
      },
      {
        path: 'debit-notes/:id/edit',
        name: 'company-purchase-debit-notes-id-edit',
        component: () => import('pages/purchase/debit-notes/DebitNotesForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Debit Notes', 'Edit'],
        },
      },
      {
        path: 'discounts',
        name: 'company-purchase-discounts',
        component: () => import('pages/purchase/discounts/PurchaseDiscountList.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Discounts'],
        },
      },
      {
        path: 'discounts/create',
        name: 'company-purchase-discounts-create',
        component: () => import('pages/purchase/discounts/PurchaseDiscountForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Discounts', 'Create'],
        },
      },
      {
        path: 'discounts/:id/edit',
        name: 'company-purchase-discounts-id-edit',
        component: () => import('pages/purchase/discounts/PurchaseDiscountForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Discounts', 'Edit'],
        },
      },
      {
        path: 'purchase-book',
        name: 'company-purchase-book',
        component: () => import('pages/purchase/purchase-book/PurchaseBookList.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Book'],
        },
      },
      {
        path: 'purchase-orders',
        name: 'company-purchase-orders',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderList.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Orders'],
        },
      },
      {
        path: 'purchase-orders/create',
        name: 'company-purchase-orders-create',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Orders', 'Create'],
        },
      },
      {
        path: 'purchase-orders/:id/edit',
        name: 'company-purchase-orders-id-edit',
        component: () => import('pages/purchase/purchase-order/PurchaseOrderForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Orders', 'Edit'],
        },
      },
      {
        path: 'vouchers',
        name: 'company-purchase-vouchers',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherList.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Vouchers'],
        },
      },
      {
        path: 'vouchers/create',
        name: 'company-purchase-vouchers-create',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Vouchers', 'Create'],
        },
      },
      {
        path: 'vouchers/:id',
        name: 'company-purchase-vouchers-id',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherDetail.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Vouchers', 'Detail'],
        },
      },
      {
        path: 'vouchers/:id/edit',
        name: 'company-purchase-vouchers-id-edit',
        component: () => import('pages/purchase/purchase-voucher/PurchaseVoucherForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Vouchers', 'Edit'],
        },
      },
      {
        path: 'vouchers/recurring-templates',
        name: 'company-purchase-vouchers-recurring-templates',
        component: () => import('pages/purchase/purchase-voucher/RecurringTemplateList.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Vouchers', 'Recurring Templates'],
        },
      },
      {
        path: 'vouchers/recurring-templates/create',
        name: 'company-purchase-vouchers-recurring-templates-create',
        component: () => import('pages/purchase/purchase-voucher/RecurringTemplateForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Vouchers', 'Recurring Templates', 'Create'],
        },
      },
      {
        path: 'vouchers/recurring-templates/:id/edit',
        name: 'company-purchase-vouchers-recurring-templates-id-edit',
        component: () => import('pages/purchase/purchase-voucher/RecurringTemplateForm.vue'),
        meta: {
          breadcrumbs: ['Purchase', 'Purchase Vouchers', 'Recurring Templates', 'Edit'],
        },
      },
    ],
  },
  {
    path: 'sales',
    name: 'company-sales',
    meta: {
      breadcrumbs: ['Sales'],
    },
    children: [
      {
        path: 'agents',
        name: 'company-sales-agents',
        component: () => import('pages/sales/agent/SalesAgentList.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Agents'],
        },
      },
      {
        path: 'agents/create',
        name: 'company-sales-agents-create',
        component: () => import('pages/sales/agent/SalesAgentForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Agents', 'Create'],
        },
      },
      {
        path: 'agents/:id/edit',
        name: 'company-sales-agents-id-edit',
        component: () => import('pages/sales/agent/SalesAgentForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Agents', 'Edit'],
        },
      },
      {
        path: 'sales-book',
        name: 'company-sales-book',
        component: () => import('pages/sales/book/SalesBookList.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Book'],
        },
      },
      {
        path: 'challans',
        name: 'company-sales-challans',
        component: () => import('pages/sales/challan/ChallanList.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Challans'],
        },
      },
      {
        path: 'challans/create',
        name: 'company-sales-challans-create',
        component: () => import('pages/sales/challan/ChallanForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Challans', 'Create'],
        },
      },
      {
        path: 'challans/:id/edit',
        name: 'company-sales-challans-id-edit',
        component: () => import('pages/sales/challan/ChallanForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Challans', 'Edit'],
        },
      },
      {
        path: 'credit-notes',
        name: 'company-sales-credit-notes',
        component: () => import('pages/sales/credit-note/CreditNoteList.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Credit Notes'],
        },
      },
      {
        path: 'credit-notes/create',
        name: 'company-sales-credit-notes-create',
        component: () => import('pages/sales/credit-note/CreditNoteForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Credit Notes', 'Create'],
        },
      },
      {
        path: 'credit-notes/:id',
        name: 'company-sales-credit-notes-id',
        component: () => import('pages/sales/credit-note/CreditNoteDetail.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Credit Notes', 'Detail'],
        },
      },
      {
        path: 'credit-notes/:id/edit',
        name: 'company-sales-credit-notes-id-edit',
        component: () => import('pages/sales/credit-note/CreditNoteForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Credit Notes', 'Edit'],
        },
      },
      {
        path: 'discounts',
        name: 'company-sales-discounts',
        component: () => import('pages/sales/discount/SalesDiscountList.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Discounts'],
        },
      },
      {
        path: 'discounts/create',
        name: 'company-sales-discounts-create',
        component: () => import('pages/sales/discount/SalesDiscountForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Discounts', 'Create'],
        },
      },
      {
        path: 'discounts/:id/edit',
        name: 'company-sales-discounts-id-edit',
        component: () => import('pages/sales/discount/SalesDiscountForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Discounts', 'Edit'],
        },
      },
      {
        path: 'pos',
        name: 'company-sales-pos',
        component: () => import('pages/sales/pos/PosForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'POS'],
        },
      },
      {
        path: 'vouchers',
        name: 'company-sales-vouchers',
        component: () => import('pages/sales/sales-voucher/SalesVoucherList.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers'],
        },
      },
      {
        path: 'vouchers/create',
        name: 'company-sales-vouchers-create',
        component: () => import('pages/sales/sales-voucher/SalesVoucherForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers', 'Create'],
        },
      },
      {
        path: 'vouchers/:id',
        name: 'company-sales-vouchers-id',
        component: () => import('pages/sales/sales-voucher/SalesVoucherDetail.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers', 'Detail'],
        },
      },
      {
        path: 'vouchers/:id/edit',
        name: 'company-sales-vouchers-id-edit',
        component: () => import('pages/sales/sales-voucher/SalesVoucherForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers', 'Edit'],
        },
      },
      {
        path: 'vouchers/:id/materialized-view',
        name: 'company-sales-vouchers-id-materialized-view',
        component: () => import('pages/sales/sales-voucher/SalesVoucherMV.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers', 'Materialized View'],
        },
      },
      {
        path: 'vouchers/recurring-templates',
        name: 'company-sales-vouchers-recurring-templates',
        component: () => import('pages/sales/sales-voucher/RecurringTemplateList.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers', 'Recurring Templates'],
        },
      },
      {
        path: 'vouchers/recurring-templates/create',
        name: 'company-sales-vouchers-recurring-templates-create',
        component: () => import('pages/sales/sales-voucher/RecurringTemplateForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers', 'Recurring Templates', 'Create'],
        },
      },
      {
        path: 'vouchers/recurring-templates/:id/edit',
        name: 'company-sales-vouchers-recurring-templates-id-edit',
        component: () => import('pages/sales/sales-voucher/RecurringTemplateForm.vue'),
        meta: {
          breadcrumbs: ['Sales', 'Sales Vouchers', 'Recurring Templates', 'Edit'],
        },
      },
    ],
  },
  {
    path: 'settings',
    component: () => import('layouts/SettingsLayout.vue'),
    children: [
      {
        path: '',
        name: 'company-settings',
        component: () => import('pages/company/settings/index.vue'),
        meta: {
          breadcrumbs: ['Settings', 'General'],
        },
      },
      {
        path: 'members',
        name: 'company-settings-members',
        component: () => import('pages/company/settings/members.vue'),
        meta: {
          breadcrumbs: ['Settings', 'Members'],
        },
      },
      {
        path: 'permissions',
        name: 'company-settings-permissions',
        component: () => import('pages/company/settings/permissions.vue'),
        meta: {
          breadcrumbs: ['Settings', 'Permissions'],
        },
      },
      {
        path: 'api-tokens',
        name: 'company-settings-api-tokens',
        component: () => import('pages/company/settings/api-tokens.vue'),
        meta: {
          breadcrumbs: ['Settings', 'API Tokens'],
        },
      },
      {
        path: 'purchase',
        name: 'company-settings-purchase-settings',
        component: () => import('pages/settings/PurchaseSetting.vue'),
        meta: {
          breadcrumbs: ['Settings', 'Purchase Settings'],
        },
      },
      {
        path: 'sales',
        name: 'company-settings-sales-settings',
        component: () => import('pages/settings/SalesSetting.vue'),
      },
      {
        path: 'inventory',
        name: 'company-settings-inventory-settings',
        component: () => import('pages/settings/InventorySettings.vue'),
        meta: {
          breadcrumbs: ['Settings', 'Inventory Settings'],
        },
      },
    ],
  },
  {
    path: 'tax',
    name: 'company-tax',
    meta: {
      breadcrumbs: ['Tax'],
    },
    children: [
      {
        path: 'payments',
        name: 'company-tax-payments',
        component: () => import('pages/tax/payments/TaxPaymentList.vue'),
        meta: {
          breadcrumbs: ['Tax', 'Payments'],
        },
      },
      {
        path: 'payments/create',
        name: 'company-tax-payments-create',
        component: () => import('pages/tax/payments/TaxPaymentForm.vue'),
        meta: {
          breadcrumbs: ['Tax', 'Payments', 'Create'],
        },
      },
      {
        path: 'payments/:id/edit',
        name: 'company-tax-payments-id-edit',
        component: () => import('pages/tax/payments/TaxPaymentForm.vue'),
        meta: {
          breadcrumbs: ['Tax', 'Payments', 'Edit'],
        },
      },
      {
        path: 'schemes',
        name: 'company-tax-schemes',
        component: () => import('pages/tax/scheme/TaxAccountList.vue'),
      },
      {
        path: 'schemes/create',
        name: 'company-tax-schemes-create',
        component: () => import('pages/tax/scheme/TaxForm.vue'),
      },
      {
        path: 'schemes/:id',
        name: 'company-tax-schemes-id',
        component: () => import('pages/tax/scheme/TaxForm.vue'),
      },
      {
        path: 'schemes/:id/edit',
        name: 'company-tax-schemes-id-edit',
        component: () => import('pages/tax/scheme/TaxForm.vue'),
      },
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
    meta: {
      breadcrumbs: ['Inventory'],
    },
    children: [
      {
        path: 'items',
        name: 'company-inventory-items',
        component: () => import('pages/inventory/item/ItemList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Items'],
        },
      },
      {
        path: 'items/create',
        name: 'company-inventory-items-create',
        component: () => import('pages/inventory/item/ItemForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Items', 'Create'],
        },
      },
      {
        path: 'items/:id',
        name: 'company-inventory-items-id',
        component: () => import('pages/inventory/item/ItemDetail.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Items', 'Detail'],
        },
      },
      {
        path: 'items/:id/edit',
        name: 'company-inventory-items-id-edit',
        component: () => import('pages/inventory/item/ItemForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Items', 'Edit'],
        },
      },
      {
        path: 'units',
        name: 'company-inventory-units',
        component: () => import('pages/inventory/unit/UnitList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Units'],
        },
      },
      {
        path: 'units/create',
        name: 'company-inventory-units-create',
        component: () => import('pages/inventory/unit/UnitForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Units', 'Create'],
        },
      },
      {
        path: 'units/:id',
        name: 'company-inventory-units-id',
        component: () => import('pages/inventory/unit/UnitForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Units', 'Edit'],
        },
      },
      {
        path: 'units/:id/edit',
        name: 'company-inventory-units-id-edit',
        component: () => import('pages/inventory/unit/UnitForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Units', 'Edit'],
        },
      },
      {
        path: 'categories',
        name: 'company-inventory-categories',
        component: () => import('pages/inventory/product/category/InventoryCategoryList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Categories'],
        },
      },
      {
        path: 'categories/create',
        name: 'company-inventory-categories-create',
        component: () => import('pages/inventory/product/category/InventoryCategoryForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Categories', 'Create'],
        },
      },
      {
        path: 'categories/:id',
        name: 'company-inventory-categories-id',
        component: () => import('pages/inventory/product/category/InventoryCategoryForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Categories', 'Edit'],
        },
      },
      {
        path: 'categories/:id/edit',
        name: 'company-inventory-categories-id-edit',
        component: () => import('pages/inventory/product/category/InventoryCategoryForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Categories', 'Edit'],
        },
      },
      {
        path: 'brands',
        name: 'company-inventory-brands',
        component: () => import('pages/inventory/product/brand/BrandList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Brands'],
        },
      },
      {
        path: 'brands/create',
        name: 'company-inventory-brands-create',
        component: () => import('pages/inventory/product/brand/BrandForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Brands', 'Create'],
        },
      },
      {
        path: 'brands/:id/edit',
        name: 'company-inventory-brands-id-edit',
        component: () => import('pages/inventory/product/brand/BrandForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Brands', 'Edit'],
        },
      },
      {
        path: 'opening-stock',
        name: 'company-inventory-opening-stock',
        component: () => import('pages/inventory/item/opening-stock/ItemOpeningStockList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Opening Stock'],
        },
      },
      {
        path: 'opening-stock/create',
        name: 'company-inventory-opening-stock-create',
        component: () => import('pages/inventory/item/opening-stock/ItemOpeningStockForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Opening Stock', 'Create'],
        },
      },
      {
        path: 'opening-stock/:id',
        name: 'company-inventory-opening-stock-id',
        component: () => import('pages/inventory/item/opening-stock/ItemOpeningStockForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Opening Stock', 'Edit'],
        },
      },
      {
        path: 'adjustments',
        name: 'company-inventory-adjustments',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Adjustments'],
        },
      },
      {
        path: 'adjustments/create',
        name: 'company-inventory-adjustments-create',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Adjustments', 'Create'],
        },
      },
      {
        path: 'adjustments/:id',
        name: 'company-inventory-adjustments-id',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentDetail.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Adjustments', 'Detail'],
        },
      },
      {
        path: 'adjustments/:id/edit',
        name: 'company-inventory-adjustments-id-edit',
        component: () => import('pages/inventory/product/inventory-adjustment/InventoryAdjustmentForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Adjustments', 'Edit'],
        },
      },
      {
        path: 'bill-of-materials',
        name: 'company-inventory-bill-of-materials',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Bill of Materials'],
        },
      },
      {
        path: 'bill-of-materials/create',
        name: 'company-inventory-bill-of-materials-create',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Bill of Materials', 'Create'],
        },
      },
      {
        path: 'bill-of-materials/:id',
        name: 'company-inventory-bill-of-materials-id',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Bill of Materials', 'Detail'],
        },
      },
      {
        path: 'bill-of-materials/:id/edit',
        name: 'company-inventory-bill-of-materials-id-edit',
        component: () => import('pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Bill of Materials', 'Edit'],
        },
      },
      {
        path: 'conversions',
        name: 'company-inventory-conversions',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Conversions'],
        },
      },
      {
        path: 'conversions/create',
        name: 'company-inventory-conversions-create',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Conversions', 'Create'],
        },
      },
      {
        path: 'conversions/:id',
        name: 'company-inventory-conversions-id',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionDetail.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Conversions', 'Detail'],
        },
      },
      {
        path: 'conversions/:id/edit',
        name: 'company-inventory-conversions-id-edit',
        component: () => import('pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Conversions', 'Edit'],
        },
      },
      {
        path: 'ledgers',
        name: 'company-inventory-ledgers',
        component: () => import('pages/inventory/product/inventory-account/InventoryAccountList.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Ledgers'],
        },
      },
      {
        path: 'ledgers/:id',
        name: 'company-inventory-ledgers-id',
        component: () => import('pages/inventory/product/inventory-account/InventoryAccountDetail.vue'),
        meta: {
          breadcrumbs: ['Inventory', 'Ledgers', 'Detail'],
        },
      },
    ],
  },
  {
    path: 'journal-entries/:slug/:id',
    name: 'company-journal-entries',
    component: () => import('pages/journal-entry/[slugUrl].vue'),
  },
  {
    path: 'crm',
    name: 'company-crm',
    meta: {
      breadcrumbs: ['CRM'],
    },
    children: [
      {
        path: 'parties',
        name: 'company-party-list',
        component: () => import('pages/party/PartyList.vue'),
        meta: {
          breadcrumbs: ['Party', 'All Parties'],
        },
      },
      {
        path: 'parties/create',
        name: 'company-party-create',
        component: () => import('pages/party/PartyForm.vue'),
        meta: {
          breadcrumbs: ['Party', 'Create'],
        },
      },
      {
        path: 'parties/:id',
        name: 'company-party-id',
        component: () => import('pages/party/PartyForm.vue'),
        meta: {
          breadcrumbs: ['Party', 'Detail'],
        },
      },
      {
        path: 'parties/:id/edit',
        name: 'company-party-edit',
        component: () => import('pages/party/PartyForm.vue'),
        meta: {
          breadcrumbs: ['Party', 'Edit'],
        },
      },
      {
        path: 'parties/:id/account',
        name: 'company-party-account',
        component: () => import('pages/party/PartyAccount.vue'),
        meta: {
          breadcrumbs: ['Party', 'Account'],
        },
      },
      {
        path: 'parties/:id/alias',
        name: 'company-party-alias',
        component: () => import('pages/party/PartyAlias.vue'),
        meta: {
          breadcrumbs: ['Party', 'Alias'],
        },
      },
      {
        path: 'parties/:id/representative',
        name: 'company-party-representative',
        component: () => import('pages/party/PartyRepresentative.vue'),
        meta: {
          breadcrumbs: ['Party', 'Representative'],
        },
      },
      {
        path: 'customers',
        name: 'company-customer-list',
        component: () => import('pages/party/CustomerList.vue'),
        meta: {
          breadcrumbs: ['Party', 'Customers'],
        },
      },
      {
        path: 'suppliers',
        name: 'company-supplier-list',
        component: () => import('pages/party/SupplierList.vue'),
        meta: {
          breadcrumbs: ['Party', 'Suppliers'],
        },
      },
    ],
  },
  {
    path: 'payment-receipts',
    name: 'company-payment-receipts',
    meta: {
      breadcrumbs: ['Payment Receipts'],
    },
    children: [
      {
        path: '',
        name: 'company-payment-receipts-list',
        component: () => import('pages/payment-receipt/PaymentReceiptList.vue'),
        meta: {
          breadcrumbs: ['Payment Receipts', 'List'],
        },
      },
      {
        path: 'create',
        name: 'company-payment-receipts-create',
        component: () => import('pages/payment-receipt/PaymentReceiptForm.vue'),
        meta: {
          breadcrumbs: ['Payment Receipts', 'Create'],
        },
      },
      {
        path: ':id',
        name: 'company-payment-receipts-id',
        component: () => import('pages/payment-receipt/PaymentReceiptView.vue'),
        meta: {
          breadcrumbs: ['Payment Receipts', 'Detail'],
        },
      },
      {
        path: ':id/edit',
        name: 'company-payment-receipts-id-edit',
        component: () => import('pages/payment-receipt/PaymentReceiptForm.vue'),
        meta: {
          breadcrumbs: ['Payment Receipts', 'Edit'],
        },
      },
    ],
  },
  {
    path: 'reports',
    name: 'company-reports',
    meta: {
      breadcrumbs: ['Reports'],
    },
    children: [
      {
        path: 'account-ledger',
        name: 'company-reports-account-ledger',
        component: () => import('pages/report/AgeingReport.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Account Ledger'],
        },
      },
      {
        path: 'balance-sheet',
        name: 'company-reports-balance-sheet',
        component: () => import('pages/report/BalanceSheet.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Balance Sheet'],
        },
      },
      {
        path: 'category-tree',
        name: 'company-reports-category-tree',
        component: () => import('pages/report/CategoryTree.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Category Tree'],
        },
      },
      {
        path: 'chart-of-accounts',
        name: 'company-reports-chart-of-accounts',
        component: () => import('pages/report/ChartOfAccounts.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Chart of Accounts'],
        },
      },
      {
        path: 'collection',
        name: 'company-reports-collection',
        component: () => import('pages/report/CollectionReport.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Collection'],
        },
      },
      {
        path: 'day-book',
        name: 'company-reports-day-book',
        component: () => import('pages/report/DayBook.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Day Book'],
        },
      },
      {
        path: 'income-statement',
        name: 'company-reports-income-statement',
        component: () => import('pages/report/IncomeStatement.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Income Statement'],
        },
      },

      {
        path: 'ratio-analysis',
        name: 'company-reports-ratio-analysis',
        component: () => import('pages/report/RatioAnalysis.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Ratio Analysis'],
        },
      },
      {
        path: 'sales-by-category',
        name: 'company-reports-sales-by-category',
        component: () => import('pages/report/SalesByCategory.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Sales By Category'],
        },
      },
      {
        path: 'stock-trial-balance',
        name: 'company-reports-stock-trial-balance',
        component: () => import('pages/report/StockTrialBalance.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Stock Trial Balance'],
        },
      },
      {
        path: 'tax-summary',
        name: 'company-reports-tax-summary',
        component: () => import('pages/report/TaxSummary.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Tax Summary'],
        },
      },
      {
        path: 'transactions',
        name: 'company-reports-transactions',
        component: () => import('pages/report/TransactionsList.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Transactions'],
        },
      },
      {
        path: 'trial-balance',
        name: 'company-reports-trial-balance',
        component: () => import('pages/report/TrialBalance.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Trial Balance'],
        },
      },
      {
        path: 'stock-movement',
        name: 'company-reports-stock-movement',
        component: () => import('pages/report/StockMovement.vue'),
        meta: {
          breadcrumbs: ['Reports', 'Stock Movement'],
        },
      },
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
    meta: {
      auth: {
        redirectIfLoggedIn: '/',
      },
    },
  },
  {
    path: '/signup',
    name: 'signup-page',
    component: () => import('pages/SignupPage.vue'),
    meta: {
      auth: {
        redirectIfLoggedIn: '/',
      },
    },
  },
  {
    path: '/auth',
    meta: {
      auth: {
        redirectIfLoggedIn: '/',
      },
    },
    children: [
      {
        path: 'verify-email/:token',
        name: 'verify-email',
        component: () => import('pages/auth/verify-email/[token].vue'),
      },
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: () => import('pages/auth/forgot-password.vue'),
      },
      {
        path: 'password/reset/:token',
        name: 'password-reset',
        component: () => import('pages/auth/password/reset/[token].vue'),
      },
    ],
  },
  {
    path: '/onboarding',
    name: 'onboarding',
    component: () => import('pages/onboarding.vue'),
    meta: {
      auth: {
        required: true,
      },
    },
  },
  {
    path: '/company/create',
    name: 'company-create',
    component: () => import('pages/company/create.vue'),
    meta: {
      breadcrumbs: ['Create Company'],
      auth: {
        required: true,
      },
    },

  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('pages/profile/index.vue'),
    meta: {
      breadcrumbs: ['Profile'],
      auth: {
        required: true,
      },
    },
  },
  {
    path: '/invitations',
    name: 'invitations',
    component: () => import('pages/profile/invitations.vue'),
    meta: {
      breadcrumbs: ['Invitations'],
      auth: {
        required: true,
      },
    },
  },
  {
    path: '/invitations/:token',
    name: 'invitations-token',
    component: () => import('pages/profile/invitations.vue'),
    meta: {
      breadcrumbs: ['Invitations'],
      auth: {
        required: false,
      },
    },
  },
  {
    path: '/:company',
    name: 'company',
    component: () => import('layouts/MainLayout.vue'),
    children: companyRoutes,
    meta: {
      auth: {
        required: true,
      },
    },
  },
]

export default routes
