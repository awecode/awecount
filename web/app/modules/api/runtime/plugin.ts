import type { NitroFetchRequest } from 'nitropack'
import type { RouteLocationRaw } from 'vue-router'

import type { $APIOptions } from './types'
import { handleTrailingSlash, isURL } from './utils'

export default defineNuxtPlugin({
  name: 'api',
  async setup() {
    const nuxt = useNuxtApp()
    const config = useRuntimeConfig()

    const $api = async<
      DefaultT = unknown,
      DefaultR extends NitroFetchRequest = NitroFetchRequest,
      T = DefaultT,
      R extends NitroFetchRequest = DefaultR,
      O extends $APIOptions<R> = $APIOptions<R>,
    > (request: R, opts?: O) => {
      const {
        protected: _protected = config.public.api.protected,
        authNamespace = config.public.api.authNamespace,
        handleErrors = true,
        onRequest,
        onResponseError,
        trailingSlash = config.public.api.trailingSlash,
        ...options
      } = opts || {} as O

      const { token } = useAuth(authNamespace)

      return $fetch<T, R>(request, {
        onRequest: async (ctx) => {
          // await onRequest?.(ctx)

          ctx.options.method ||= 'GET'

          if (typeof ctx.request === 'string') {
            ctx.request = handleTrailingSlash(ctx.request, trailingSlash)
            if (!options.baseURL && !isURL(ctx.request)) {
              ctx.options.baseURL = config.public.api.baseURL
            }
          }

          if (_protected && token.value && !ctx.options.headers.get('Authorization')) {
            ctx.options.headers.set('Authorization', `Token ${token.value}`)
          }
        },

        onResponseError: async (ctx) => {
          // await onResponseError?.(ctx)
          if (!handleErrors) return

          // Handle unauthorized/forbidden responses based on config
          if (_protected && config.public.api.unauthorized) {
            const { statusCodes, strategy, redirect } = config.public.api.unauthorized as { statusCodes: number[], strategy: 'redirect' | 'error', redirect?: RouteLocationRaw }

            if (statusCodes.includes(ctx.response.status)) {
              if (strategy === 'redirect' && redirect) {
                await navigateTo(redirect)
                return
              }

              // if (strategy === 'error') {
              //   nuxt.payload.error = createError({
              //     statusCode: ctx.response.status,
              //     statusMessage: `${ctx.response.statusText} ${ctx.response.url}`,
              //   })
              //   return
              // }
            }
          }

          // Handle 404 errors for GET requests
          if (ctx.response.status === 404 && ctx.options.method === 'GET') {
            nuxt.payload.error = createError({
              statusCode: ctx.response.status,
              statusMessage: `${ctx.response.statusText} ${ctx.response.url}`,
            })
          }
        },
        ...options,
      })
    }

    return {
      provide: {
        api: $api,
      },
    }
  },
})
