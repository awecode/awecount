import { defineBoot } from '#q-app/wrappers'

import { auth as authConfig } from 'src/config'
import { useAuthStore } from 'stores/auth'

export default defineBoot(({ router }) => {
  const { isAuthenticated, onboarded, hasAnyRole, hasAnyPermission } = useAuthStore()

  router.beforeEach((to, from) => {
    if (to.name === undefined) return

    const authRequired = to.meta?.auth?.protected ?? false

    const loginRoute = to.meta?.auth?.loginRoute
    const redirectIfLoggedIn = to.meta?.auth?.redirectIfLoggedIn ?? false
    const redirectIfNotAllowed = to.meta?.auth?.redirectIfNotAllowed ?? false

    const routeRoles = to.meta?.auth?.roles
    const routePermissions = to.meta?.auth?.permissions

    if (redirectIfLoggedIn && isAuthenticated) {
      return { path: redirectIfLoggedIn }
    }

    if (!authRequired) {
      return
    }

    if (!isAuthenticated) {
      return { path: loginRoute, query: { next: to.fullPath } }
    }

    if (!onboarded && authConfig.onboarding.enabled) {
      const route = authConfig.onboarding.route

      if ((typeof route === 'string' && route === to.fullPath) || (typeof route === 'object' && (('name' in route && route.name === to.name) || (route.path && route.path === to.fullPath)))) {
        return
      }

      return route
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
})
