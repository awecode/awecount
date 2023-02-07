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
