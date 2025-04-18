import type { RouteLocationRaw } from 'vue-router'

import { defu } from 'defu'
import { addImports, addPlugin, createResolver, defineNuxtModule } from 'nuxt/kit'

export interface ModuleOptions {
  baseURL: string
  trailingSlash: boolean
  protected: boolean
  unauthorized?:
    | {
      redirect: RouteLocationRaw
      statusCodes: number[]
      strategy: 'redirect'
    }
    | {
      statusCodes: number[]
      strategy: 'error'
    }
  authNamespace: string | 'default'
  tokenPrefix?: string
  authorizationHeader?: string
}

// declare module 'nuxt/schema' {
//   interface PublicRuntimeConfig {
//     api: ModuleOptions
//   }
// }

const defaults: ModuleOptions = {
  baseURL: '/',
  trailingSlash: false,
  protected: false,
  authNamespace: 'default',
  authorizationHeader: 'Authorization',
  tokenPrefix: 'Token',
  unauthorized: {
    statusCodes: [401, 403],
    strategy: 'error',
  },
}

const declareAPI = () => {
  const { resolve } = createResolver(import.meta.url)

  return [
    `import type { $API } from '${resolve('./runtime/types')}'`,
    `import type { ModuleOptions as APIModuleOptions } from '${resolve('./index')}'`,
    `export type { PickFrom, KeysOf, UseAPIOptions, $APIOptions } from '${resolve('./runtime/types')}'`,
    '',
    `declare module '#app' {`,
    `  interface NuxtApp {`,
    `    $api: $API`,
    `  }`,
    `}`,
    '',
    `declare module 'nuxt/schema' {`,
    `  interface PublicRuntimeConfig {`,
    `    api: APIModuleOptions`,
    `  }`,
    `}`,
    '',
  ].join('\n')
}

export default defineNuxtModule<ModuleOptions>({
  meta: {
    name: 'api',
    configKey: 'api',
  },
  defaults,
  async setup(options, nuxt) {
    nuxt.options.runtimeConfig.public.api = defu(nuxt.options.runtimeConfig.public.api, options)

    const { resolve } = createResolver(import.meta.url)

    await addPlugin({ src: resolve('./runtime/plugin') })
    await addImports([{ name: 'useAPI', from: resolve('./runtime/composable') }])

    nuxt.hook('prepare:types', ({ declarations }) => {
      declarations.push('')
      declarations.push(declareAPI())
    })
  },
})
