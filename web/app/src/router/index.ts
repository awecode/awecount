import { defineRouter } from '#q-app/wrappers'

import { auth as authConfig } from 'src/config'

import { useAuthStore } from 'stores/auth'

import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'
import { switchCompanyGuard } from './guards/company'
import routes from './routes'

export default defineRouter(({ store }) => {
  const createHistory = import.meta.env.SSR ? createMemoryHistory : createWebHistory

  const { isAuthenticated, onboarded, hasAnyRole, hasAnyPermission, user } = useAuthStore(store)

  const Router = createRouter({
    routes,
    scrollBehavior: () => ({ left: 0, top: 0 }),
    history: createHistory(import.meta.env.VUE_ROUTER_BASE),
  })

  Router.beforeEach(switchCompanyGuard)

  Router.beforeEach((to, from) => {
    if (to.name === undefined) return

    const authRequired = to.meta?.auth?.required ?? false

    const loginRoute = to.meta?.auth?.loginRoute ?? authConfig.loginRoute
    const redirectIfLoggedIn = to.meta?.auth?.redirectIfLoggedIn ?? false
    const redirectIfNotAllowed = to.meta?.auth?.redirectIfNotAllowed ?? authConfig.redirectIfNotAllowed ?? false

    const routeRoles = to.meta?.auth?.roles
    const routePermissions = to.meta?.auth?.permissions

    if (redirectIfLoggedIn && isAuthenticated) {
      // return { path: redirectIfLoggedIn } // TODO: how can we support dynamic redirectIfLoggedIn?
      return { path: `${user.redirect}/dashboard` }
    }

    if (!authRequired) {
      return
    }

    if (!isAuthenticated) {
      return { path: loginRoute, query: { next: to.fullPath } }
    }

    // if (!onboarded && authConfig.onboarding.enabled) {
    //   const route = authConfig.onboarding.route

    //   if ((typeof route === 'string' && route === to.fullPath) || (typeof route === 'object' && (('name' in route && route.name === to.name) || (route.path && route.path === to.fullPath)))) {
    //     return
    //   }

    //   return route
    // }

    if (onboarded && authConfig.onboarding.enabled && to.fullPath === authConfig.onboarding.route) {
      // FIXME: This is a hack to get the user to prevent them from accessing the onboarding route if they are already onboarded
      return { path: `${user.redirect}/dashboard` }
    }

    if (routeRoles && hasAnyRole(routeRoles)) {
      return
    }

    if (routePermissions && hasAnyPermission(routePermissions)) {
      return
    }

    if (!routeRoles && !routePermissions && isAuthenticated) {
      return
    }

    if (from.fullPath !== to.fullPath && from.path !== loginRoute) {
      return from
    }

    if (!redirectIfNotAllowed) {
      return false
    }

    return { path: redirectIfNotAllowed }
  })

  return Router
})
