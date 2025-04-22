// @ts-expect-error vfs
import config from '#build/auth.config'

import { addRouteMiddleware, defineNuxtPlugin, defineNuxtRouteMiddleware } from '#imports'

export default defineNuxtPlugin({
  name: 'authorization',
  async setup() {
    addRouteMiddleware(
      'authorization',
      defineNuxtRouteMiddleware((to, from) => {
        if (to.name === undefined) return

        const authRequired = to.meta?.auth?.protected ?? false
        const authNamespace = to.meta?.auth?.namespace

        const loginRoute = to.meta?.auth?.loginRoute
        const redirectIfLoggedIn = to.meta?.auth?.redirectIfLoggedIn ?? false
        const redirectIfNotAllowed = to.meta?.auth?.redirectIfNotAllowed ?? false

        const routeRoles = to.meta?.auth?.roles
        const routePermissions = to.meta?.auth?.permissions

        const { isAuthenticated, onboarded, hasAnyRole, hasAnyPermission } = useAuth(authNamespace)

        if (redirectIfLoggedIn && isAuthenticated.value) {
          return navigateTo({ path: redirectIfLoggedIn }, { redirectCode: 302 })
        }

        if (!authRequired) {
          return
        }

        if (!isAuthenticated.value) {
          return navigateTo(
            {
              path: loginRoute,
              query: { next: to.fullPath },
            },
            {
              redirectCode: 302,
            },
          )
        }

        if (config.onboarding.enabled) {
          const isOnboardingRoute = (typeof config.onboarding.route === 'string' && config.onboarding.route === to.fullPath)
            || (typeof config.onboarding.route === 'object' && config.onboarding.route.name === to.name)

          if (onboarded.value) {
            if (isOnboardingRoute) {
              return navigateTo(config.onboarding.successRoute)
            }
            return
          } else {
            return navigateTo(config.onboarding.route)
          }
        }

        if (routeRoles && hasAnyRole(routeRoles)) {
          return
        }

        if (routePermissions && hasAnyPermission(routePermissions)) {
          return
        }

        if (!routeRoles && !routePermissions && isAuthenticated.value) {
          return
        }

        if (from.fullPath !== to.fullPath && from.path !== loginRoute) {
          return navigateTo(from)
        }

        if (!redirectIfNotAllowed) {
          return abortNavigation({ statusCode: 403 })
        }

        return navigateTo({ path: redirectIfNotAllowed }, { redirectCode: 302 })
      }),
      { global: true },
    )
  },
})
