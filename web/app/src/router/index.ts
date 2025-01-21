import { defineRouter } from '#q-app/wrappers'

import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'

import routes from './routes'

export default defineRouter((/* { store, ssrContext } */) => {
  const createHistory = import.meta.env.SSR ? createMemoryHistory : createWebHistory

  const Router = createRouter({
    routes,
    scrollBehavior: () => ({ left: 0, top: 0 }),
    history: createHistory(import.meta.env.VUE_ROUTER_BASE),
  })

  return Router
})
