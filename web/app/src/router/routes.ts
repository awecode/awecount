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
      {
        path: 'stock-adjustment/list',
        name: 'Stock Adjustment',
        component: () =>
          import(
            'src/pages/inventory/product/stock-adjustment/StockAdjustmentList.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Adjustment'],
        },
      },
      {
        path: 'stock-adjustment/add',
        component: () =>
          import(
            'src/pages/inventory/product/stock-adjustment/StockAdjustmentForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Adjustment', 'Create'],
        },
      },
      {
        path: 'stock-adjustment/:id',
        component: () =>
          import(
            'src/pages/inventory/product/stock-adjustment/StockAdjustmentForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Adjustment', 'Update'],
        },
      },
      {
        path: 'stock-adjustment/:id/view',
        component: () =>
          import(
            'src/pages/inventory/product/stock-adjustment/StockAdjustmentView.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Stock Adjustment', 'Details'],
        },
      },
      {
        path: 'bill-of-material/list',
        name: 'Bill of Material',
        component: () =>
          import(
            'src/pages/inventory/product/bill-of-material/BillOfMaterialList.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Bills of Material'],
        },
      },
      {
        path: 'bill-of-material/add',
        component: () =>
          import(
            'src/pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Bill of Material', 'Create'],
        },
      },
      {
        path: 'bill-of-material/:id',
        component: () =>
          import(
            'src/pages/inventory/product/bill-of-material/BillOfMaterialForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Bill of Material', 'Update'],
        },
      },
      {
        path: 'inventory-conversion/list',
        name: 'Inventory Conversion',
        component: () =>
          import(
            'src/pages/inventory/product/inventory-conversion/InventoryConversionList.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Inventory Conversion'],
        },
      },
      {
        path: 'inventory-conversion/add',
        component: () =>
          import(
            'src/pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Inventory Conversion', 'Create'],
        },
      },
      {
        path: 'inventory-conversion/:id',
        component: () =>
          import(
            'src/pages/inventory/product/inventory-conversion/InventoryConversionForm.vue'
          ),
        meta: {
          breadcrumb: ['Home', 'Items', 'Inventory Conversion', 'Update'],
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
    path: '/purchase-order',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () =>
          import('src/pages/purchase/purchase-order/PurchaseOrderList.vue'),
        name: 'Purchase Orders',
        meta: {
          breadcrumb: ['Home', 'Purchase Orders'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/purchase/purchase-order/PurchaseOrderForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchase Orders', 'Create'],
        },
      },
      {
        path: '/purchase-order/:id',
        component: () =>
          import('src/pages/purchase/purchase-order/PurchaseOrderForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchase Orders', 'Update'],
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
      {
        path: 'income-statement/',
        component: () => import('src/pages/report/IncomeStatement.vue'),
        meta: {
          breadcrumb: ['Home', 'Income Statement'],
        },
      },
      {
        path: 'balance-sheet/',
        component: () => import('src/pages/report/BalanceSheet.vue'),
        meta: {
          breadcrumb: ['Home', 'Balance Sheet'],
        },
      },
      {
        path: 'ratio-analysis/',
        component: () => import('src/pages/report/RatioAnalysis.vue'),
        meta: {
          breadcrumb: ['Home', 'Ratio Analysis'],
        },
      },
      {
        path: 'transactions/',
        component: () => import('src/pages/report/TransactionsList.vue'),
        meta: {
          breadcrumb: ['Home', 'Transactions'],
        },
      },
      {
        path: 'stock-trial-balance/',
        component: () => import('src/pages/report/StockTrialBalance.vue'),
        meta: {
          breadcrumb: ['Home', 'Stock Trial Balance'],
        },
      },
      {
        path: 'ageing-report/',
        component: () => import('src/pages/report/AgeingReport.vue'),
        meta: {
          breadcrumb: ['Home', 'Customer Ageing Report'],
        },
      },
      {
        path: 'sales-by-category/',
        component: () => import('src/pages/report/SalesByCategory.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales By Category'],
        },
      },
    ],
  },
  {
    path: '/bank-accounts',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Bank Accounts',
        component: () => import('src/pages/bank/account/AccountList.vue'),
        meta: {
          breadcrumb: ['Home', 'Bank Accounts'],
        },
      },
      {
        path: 'add/',
        component: () => import('src/pages/bank/account/AccountForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Bank Accounts', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () => import('src/pages/bank/account/AccountForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Bank Accounts', 'Update'],
        },
      },
    ],
  },
  {
    path: '/cheque-issue',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Cheque Issues',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueList.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Issues'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Issues', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Issues', 'Update'],
        },
      },
    ],
  },
  {
    path: '/cheque-issue',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Cheque Issues',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueList.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Issues'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Issues', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/bank/cheque-issue/ChequeIssueForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Issues', 'Update'],
        },
      },
    ],
  },
  {
    path: '/cheque-deposit',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Cheque Deposits',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositList.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Deposits'],
        },
      },

      {
        path: 'add/',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Deposits', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Deposits', 'Update'],
        },
      },
      {
        path: ':id/view/',
        component: () =>
          import('src/pages/bank/cheque-deposit/ChequeDepositDetail.vue'),
        meta: {
          breadcrumb: ['Home', 'Cheque Deposits', 'View'],
        },
        props: true,
      },
    ],
  },
  {
    path: '/cash-deposit',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Cash Deposits',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositList.vue'),
        meta: {
          breadcrumb: ['Home', 'Cash Deposits'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cash Deposits', 'Add'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cash Deposits', 'Create'],
        },
      },
    ],
  },
  {
    path: '/cash-deposit',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Cash Deposits',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositList.vue'),
        meta: {
          breadcrumb: ['Home', 'Cash Deposits'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cash Deposits', 'Add'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/bank/cash-deposit/CashDepositForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Cash Deposits', 'Create'],
        },
      },
    ],
  },
  {
    path: '/fund-transfer',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Fund Transfers',
        component: () =>
          import('src/pages/bank/fund-transfer/FundTransferList.vue'),
        meta: {
          breadcrumb: ['Home', 'Fund Transfers'],
        },
      },
      {
        path: 'add/',
        component: () =>
          import('src/pages/bank/fund-transfer/FundTransferForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Fund Transfers', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () =>
          import('src/pages/bank/fund-transfer/FundTransferForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Fund Transfers', 'Update'],
        },
      },
    ],
  },
  {
    path: '/taxes',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/tax/scheme/TaxAccountList.vue'),
        name: 'Taxes',
        meta: {
          breadcrumb: ['Home', 'Taxes'],
        },
      },
      {
        path: 'add/',

        component: () => import('src/pages/tax/scheme/TaxForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Taxes', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () => import('src/pages/tax/scheme/TaxForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Taxes', 'Update'],
        },
      },
      {
        path: '/taxes/account/:id/',
        component: () => import('src/pages/party/PartyAccount.vue'),
        meta: {
          breadcrumb: ['Home', 'Taxes', 'Account'],
        },
      },
    ],
  },
  {
    path: '/tax-payment',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/tax/payments/TaxPaymentList.vue'),
        name: 'Tax Payments',
        meta: {
          breadcrumb: ['Home', 'Tax Payments'],
        },
      },
      {
        path: 'add/',
        component: () => import('src/pages/tax/payments/TaxPaymentForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Tax Payments', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () => import('src/pages/tax/payments/TaxPaymentForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Tax Payments', 'Update'],
        },
      },
    ],
  },
  {
    path: '/party',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/party/PartyList.vue'),
        name: 'Parties',
        meta: {
          breadcrumb: ['Home', 'Parties'],
        },
      },
      {
        path: 'add/',
        component: () => import('src/pages/party/PartyForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Parties', 'Create'],
        },
      },
      {
        path: ':id/',
        component: () => import('src/pages/party/PartyForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Parties', 'Update'],
        },
      },
      {
        path: '/parties/account/:id',
        component: () => import('src/pages/party/PartyAccount.vue'),
        meta: {
          breadcrumb: ['Home', 'Parties', 'Account'],
        },
      },
      {
        path: '/parties/customers/',
        component: () => import('src/pages/party/CustomerList.vue'),
        meta: {
          breadcrumb: ['Home', 'Parties', 'Customers'],
        },
      },
      {
        path: '/parties/suppliers/',
        component: () => import('src/pages/party/SupplierList.vue'),
        meta: {
          breadcrumb: ['Home', 'Parties', 'Suppliers'],
        },
      },
    ],
  },
  {
    path: '/sales-agent',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/sales/agent/SalesAgentList.vue'),
        name: 'Sales Agents',
        meta: {
          breadcrumb: ['Home', 'Sales Agents'],
        },
      },
      {
        path: '/sales-agent/add/',
        component: () => import('src/pages/sales/agent/SalesAgentForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Agents', 'Create'],
        },
      },
      {
        path: '/sales-agent/:id/',
        component: () => import('src/pages/sales/agent/SalesAgentForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Agents', 'Update'],
        },
      },
    ],
  },
  {
    path: '/audit-log',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        name: 'Audit Logs',
        component: () => import('src/pages/settings/auditlog/AuditLogList.vue'),
        meta: {
          breadcrumb: ['Home', 'Audit Logs'],
        },
      },
      {
        path: '/audit-log/:id/',
        component: () =>
          import('src/pages/settings/auditlog/AuditLogDetails.vue'),
        meta: {
          breadcrumb: ['Home', 'Audit Logs', 'Detail'],
        },
      },
    ],
  },
  {
    path: '/settings',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'import-export/',
        component: () => import('src/pages/settings/ImportExport.vue'),
        meta: {
          breadcrumb: ['Home', 'Import/Export'],
        },
      },
      {
        path: 'sales/',
        component: () => import('src/pages/settings/SalesSetting.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Settings'],
        },
      },
      {
        path: 'purchase/',
        component: () => import('src/pages/settings/PurchaseSetting.vue'),
        meta: {
          breadcrumb: ['Home', 'Purchase Settings'],
        },
      },
      {
        path: 'account-closing/',
        component: () => import('src/pages/settings/AccountsClosing.vue'),
        meta: {
          breadcrumb: ['Home', 'Account Closing'],
        },
      },
      {
        path: 'item-merge/',
        component: () => import('src/pages/settings/ItemMerge.vue'),
        meta: {
          breadcrumb: ['Home', 'Item Merge'],
        },
      },
      {
        path: 'inventory-settings/',
        component: () => import('src/pages/settings/InventorySettings.vue'),
        meta: {
          breadcrumb: ['Home', 'Inventory Settings'],
        },
      },
    ],
  },
  {
    path: '/dashboard-widgets',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'list/',
        component: () => import('src/pages/settings/widgets/WidgetList.vue'),
        meta: {
          breadcrumb: ['Home', 'Dashboard Widgets'],
        },
        name: 'Dashboard Widgets',
      },
      {
        path: '/dashboard-widgets/add/',
        component: () => import('src/pages/settings/widgets/WidgetForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Dashboard Widgets', 'Create'],
        },
      },
      {
        path: '/dashboard-widgets/:id/',
        component: () => import('src/pages/settings/widgets/WidgetForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Dashboard Widgets', 'Update'],
        },
      },
    ],
  },
  {
    path: '/pos',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('src/pages/sales/pos/PosForm.vue'),
        meta: {
          breadcrumb: ['Home', 'Sales Invoices', 'POS'],
        },
      },
    ],
  },
  {
    path: '/journal-entries/:slug/:id/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('src/pages/journal-entry/[slugUrl].vue'),
        props: true,
        meta: {
          breadcrumb: ['Home', 'Journal Entries'],
        },
      },
    ],
  },
  {
    path: '/dashboard',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('src/pages/DashBoard.vue'),
        name: 'Home',
        meta: {
          breadcrumb: ['Dashboard'],
        },
      },
    ],
  },
  {
    path: '/no-permission',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('src/pages/NoPermission.vue'),
        name: 'NoPermission',
        meta: {
          breadcrumb: ['Home'],
        },
      },
    ],
    // children: [{ path: "", component: () => import("pages/IndexPage.vue") }],
  },

  { path: '/', component: () => import('src/pages/LandingPage.vue') },
  // {
  //   path: 'book/list/',
  //   component: () => import('src/pages/book/BookList.vue'),
  // },
  // {
  //   path: 'book/add/',
  //   component: () => import('src/pages/book/BookForm.vue'),
  // },
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
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/ErrorNotFound.vue'),
        name: 'ErrorNotFound',
        meta: {
          breadcrumb: ['Home'],
        },
      },
    ],
  },
]

export default routes
