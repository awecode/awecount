import type { RouteLocationRaw } from 'vue-router'

import { defu } from 'defu'
import { addImports, addPlugin, addTemplate, createResolver, defineNuxtModule } from 'nuxt/kit'
import { createRouter as _createRouter, addRoute, findAllRoutes } from 'rou3'

const declaration = `
declare module "nitropack" {
  interface NitroRouteConfig {
    auth?: {
      protected?: boolean
      namespace?: string
      roles?: string[]
      permissions?: string[]
      loginRoute?: string
      redirectIfLoggedIn?: string | false
      redirectIfNotAllowed?: string | false
    }
  }
}

declare module '#app' {
  interface PageMeta {
    auth?: {
      protected?: boolean
      namespace?: string
      roles?: string[]
      permissions?: string[]
      loginRoute?: string
      redirectIfLoggedIn?: string | false
      redirectIfNotAllowed?: string | false
    }
  }
}`

interface ModuleOptions {
  loginRoute?: string
  fullAccessRoles?: string[]
  redirectIfNotAllowed?: string | false
  onboarding?: { enabled?: false } | { enabled: true, route: RouteLocationRaw }
}

const createRouter = <T extends Record<string, any> = Record<string, string>>(routes: string[] | Record<string, T>): RouterContext<T> => {
  const router = _createRouter<T>()
  if (Array.isArray(routes)) {
    for (const route of routes) {
      addRoute(router, 'GET', route, { path: route } as unknown as T)
    }
  } else {
    for (const [route, data] of Object.entries(routes)) {
      addRoute(router, 'GET', route, data)
    }
  }
  return router
}

export default defineNuxtModule<ModuleOptions>({
  meta: {
    name: 'auth',
    configKey: 'auth',
  },
  defaults: {
    fullAccessRoles: [],
    loginRoute: '/auth/login',
    redirectIfNotAllowed: false,
    onboarding: { enabled: false },
  },
  async setup(options, nuxt) {
    const { resolve } = createResolver(import.meta.url)

    const router = createRouter(nuxt.options.routeRules ?? {})

    const getRules = (url: string) => {
      const _rules = defu(
        {},
        ...findAllRoutes(router, 'GET', url)
          .map(route => route.data)
          .reverse(),
      ) as Record<string, any>

      if (_rules.auth) {
        _rules.auth.loginRoute ??= options.loginRoute
        _rules.auth.redirectIfNotAllowed ??= options.redirectIfNotAllowed

        if (options.fullAccessRoles?.length) {
          _rules.auth.roles = (_rules.auth.roles || []).concat(options.fullAccessRoles)
        }
      }

      return _rules
    }

    await addImports([{ name: 'useAuth', from: resolve('./runtime/composable') }])

    await addTemplate({
      filename: 'auth.config.mjs',
      getContents: () => `export default ${JSON.stringify(options, null, 2)}`,
    })

    nuxt.hook('modules:done', () => {
      addPlugin({ src: resolve('./runtime/plugins/authorization') }, { append: true })
    })

    nuxt.hook('prepare:types', ({ declarations }) => {
      declarations.push(declaration)
    })

    nuxt.hook('pages:extend', (pages) => {
      pages.forEach((page) => {
        const rules = getRules(page.path)
        if (rules?.auth) {
          page.meta ||= {}
          page.meta.auth ??= rules.auth
        }
      })
    })
  },
})
