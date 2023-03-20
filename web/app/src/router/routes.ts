import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: 'dashboard', component: () => import('pages/IndexPage.vue') },
      {
        path: 'items/list/',
        component: () => import('src/pages/inventory/item/ItemList.vue'),
      },
      {
        path: 'items/add/',
        component: () => import('src/pages/inventory/item/ItemAdd.vue'),
      },
      {
        path: 'items/:id/',
        component: () => import('src/pages/inventory/item/ItemAdd.vue'),
      },
      {
        path: 'items/details/:id/',
        component: () => import('src/pages/inventory/item/ItemDetails.vue'),
      },
      {
        path: 'items/opening/',
        component: () =>
          import(
            'src/pages/inventory/item/opening-balance/ItemOpeningBalanceList.vue'
          ),
      },
      {
        path: 'items/opening/add',
        component: () =>
          import(
            'src/pages/inventory/item/opening-balance/ItemOpeningBalanceForm.vue'
          ),
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
      // journal entries
      {
        path: '/journal-entries/sales-voucher/:id/',
        component: () =>
          import('src/pages/voucher/SalesVoucherJournalEntries.vue'),
      },
      // journal entries
      {
        path: '/sales-voucher/:id/',
        component: () =>
          import('src/pages/sales/sales-voucher/SalesVoucherForm.vue'),
      },
      {
        path: '/journal-entries/credit-note/:id/',
        component: () =>
          import('src/pages/voucher/CreditNoteJournalEntries.vue'),
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
      {
        path: '/purchase-voucher/journal-entries/:id/',
        component: () =>
          import(
            'src/pages/purchase/purchase-voucher/PurchaseVoucherJournalEntries.vue'
          ),
      },
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
      // {
      //   path: '/debit-note/:id/',
      //   component: () =>
      //     import('src/pages/purchase/debit-notes/DebitNotesView.vue'),
      // },
      {
        path: '/journal-entries/debit-note/:id/',
        component: () =>
          import('src/pages/purchase/debit-notes/DebitNotesJournalEntries.vue'),
      },
      {
        path: '/journal-entries/payment-receipt/:id/',
        component: () =>
          import('src/pages/payment-receipt/PaymentRecieptJournalEntries.vue'),
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
        path: '/items/opening/:id',
        component: () =>
          import(
            'src/pages/inventory/item/opening-balance/ItemOpeningBalanceForm.vue'
          ),
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
        path: 'inventory-category/list/',
        component: () =>
          import(
            'src/pages/inventory/product/category/InventoryCategoryList.vue'
          ),
      },
      {
        path: 'inventory-category/add/',
        component: () =>
          import(
            'src/pages/inventory/product/category/InventoryCategoryForm.vue'
          ),
      },
      {
        path: 'inventory-account/list/',
        component: () =>
          import(
            'src/pages/inventory/product/inventory-account/InventoryAccountList.vue'
          ),
      },
      {
        path: '/inventory-account/add/',
        component: () =>
          import(
            'src/pages/inventory/product/category/InventoryCategoryForm.vue'
          ),
      },
      //
      {
        path: 'inventory-account/detail/:id/',
        component: () =>
          import(
            'src/pages/inventory/product/inventory-account/InventoryAccountDetail.vue'
          ),
      },
      {
        path: '/inventory-account/add/',
        component: () =>
          import(
            'src/pages/inventory/product/category/InventoryCategoryForm.vue'
          ),
      },
      //
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
      {
        path: 'brand/list/',
        component: () =>
          import('src/pages/inventory/product/brand/BrandList.vue'),
      },
      {
        path: 'brand/add/',
        component: () =>
          import('src/pages/inventory/product/brand/BrandForm.vue'),
      },
      {
        path: 'units/list/',
        component: () => import('src/pages/inventory/unit/UnitList.vue'),
      },
      {
        path: 'units/add/',
        component: () => import('src/pages/inventory/unit/UnitForm.vue'),
      },
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
      // {
      //   path: 'journal-entries/:slug/:id/',
      //   component: () => import('src/pages/journal-entry/[slugUrl].vue'),
      //   props: true,
      // },
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

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
