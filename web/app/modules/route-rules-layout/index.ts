import type { RouterContext } from 'rou3'

import { defu } from 'defu'
import { defineNuxtModule } from 'nuxt/kit'
import { createRouter as _createRouter, addRoute, findAllRoutes } from 'rou3'

const declaration = `
import type { ComputedRef, MaybeRef } from 'vue'
import type { LayoutKey } from '#build/types/layouts'
declare module "nitropack" {
  interface NitroRouteConfig {
    layout?: LayoutKey | false
  }
}`

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

export default defineNuxtModule({
  meta: {
    name: 'route-rules-layout',
  },
  async setup(options, nuxt) {
    const router = createRouter(nuxt.options.routeRules ?? {})

    const getRules = (url: string) => {
      return defu(
        {},
        ...findAllRoutes(router, 'GET', url)
          .map(route => route.data)
          .reverse(),
      ) as Record<string, any>
    }

    nuxt.hook('prepare:types', ({ declarations }) => {
      declarations.push(declaration)
    })

    nuxt.hook('pages:resolved', (pages) => {
      pages.forEach((page) => {
        const rules = getRules(page.path)
        if (rules?.layout) {
          page.meta ||= {}
          page.meta.layout ??= rules.layout
        }
      })
    })
  },
})
