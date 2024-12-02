import { route } from 'quasar/wrappers'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'

import routes from './routes'
import { useLoginStore } from 'src/stores/login-info'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
    ? createWebHistory
    : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })
  // Token validation

  const hashPathRegexes = [
    '^/sales-voucher/\\d+/view$',
  ]

  function isHashPath(path: string) {
    return hashPathRegexes.some((regex) => new RegExp(regex).test(path))
  }

  Router.beforeEach((to, from, next) => {
    const store = useLoginStore()
    if (to.path === '/') {
      if (!!store.token) {
        next('/dashboard')
      } else next()
    } else if (to.path !== '/login' && store.token === null) {
      if (to.query.hash && isHashPath(to.path)) {
        next()
      } else next('/login')
    } else {
      // Should check if back btn is pressed from Nopermission page
      // TODO: Not handled when jumping from one no permission page to another
      if (
        to.fullPath === window.history.state.current &&
        from.name === 'NoPermission'
      ) {
        next(window.history.state.back)
      } else next()
    }
  })
  return Router
})
