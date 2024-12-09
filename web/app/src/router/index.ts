import { defineRouter } from '#q-app/wrappers'
import { useLoginStore } from 'stores/login-info'
import { createMemoryHistory, createRouter, createWebHashHistory, createWebHistory } from 'vue-router'

import routes from './routes'

export default defineRouter((/* { store, ssrContext } */) => {
  const createHistory = import.meta.env.SSR
    ? createMemoryHistory
    : (import.meta.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    routes,
    scrollBehavior: () => ({ left: 0, top: 0 }),
    history: createHistory(import.meta.env.VUE_ROUTER_BASE),
  })

  // Token validation
  Router.beforeEach((to, from, next) => {
    const store = useLoginStore()
    if (to.path === '/') {
      if (store.token) {
        next('/dashboard')
      } else {
        next()
      }
    } else if (to.path !== '/login' && store.token === null) {
      next('/login')
    } else {
      // Should check if back btn is pressed from Nopermission page
      // TODO: Not handled when jumping from one no permission page to another
      if (
        to.fullPath === window.history.state.current
        && from.name === 'NoPermission'
      ) {
        next(window.history.state.back)
      } else {
        next()
      }
    }
  })

  return Router
})
