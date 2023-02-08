import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: 'dashboard', component: () => import('pages/IndexPage.vue') },
      {
        path: 'items/list/',
        component: () => import('src/pages/item/ListPage.vue'),
      },
      {
        path: 'items/add/',
        component: () => import('src/pages/item/AddPage.vue'),
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
      {
        path: 'bank/account/:id/view/',
        component: () => import('src/pages/bank/account/AccountDetail.vue'),
        props: true,
      },
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
      {
        path: 'journal-entries/:slug/:id/',
        component: () => import('src/pages/journal-entry/[slugUrl].vue'),
        props: true,
      },
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
];

export default routes;
