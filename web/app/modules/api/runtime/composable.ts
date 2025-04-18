import type { FetchResult } from '#app'
import type { AvailableRouterMethod, NitroFetchRequest } from 'nitropack'
import type { FetchError } from 'ofetch'
import type { Ref } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import type { KeysOf, UseAPIOptions } from './types'

import { useFetch } from '#app'
import { handleTrailingSlash, isURL } from './utils'

export const useAPI = <
  ResT = void,
  ReqT extends NitroFetchRequest = NitroFetchRequest,
  Method extends AvailableRouterMethod<ReqT> = ResT extends void ? 'get' extends AvailableRouterMethod<ReqT> ? 'get' : AvailableRouterMethod<ReqT> : AvailableRouterMethod<ReqT>,
  ErrorT = FetchError,
  _ResT = ResT extends void ? FetchResult<ReqT, Method> : ResT,
  DataT = _ResT,
  PickKeys extends KeysOf<DataT> = KeysOf<DataT>,
  DefaultT = DataT,
> (
  request: Ref<ReqT> | ReqT | (() => ReqT),
  opts?: UseAPIOptions<_ResT, DataT, PickKeys, DefaultT, ReqT, Method>,
) => {
  const nuxt = useNuxtApp()
  const config = useRuntimeConfig()

  if (import.meta.dev && import.meta.client) {
    opts ||= {}
    // @ts-expect-error private property
    opts._functionName ||= 'useAPI'
  }

  const {
    onRequest,
    onResponseError,
    handleErrors = true,
    authNamespace = config.public.api.authNamespace,
    protected: _protected = config.public.api.protected,
    trailingSlash = config.public.api.trailingSlash,
    ...options
  } = opts || {}

  const { token } = useAuth(authNamespace)

  let controller: AbortController | null = null

  onBeforeUnmount(() => {
    controller?.abort()
  })

  console.log('request', request)

  return useFetch<ResT, ErrorT, ReqT, Method, _ResT, DataT, PickKeys, DefaultT>(request, {
    onRequest: async (ctx) => {
      controller?.abort()
      controller = new AbortController()
      ctx.options.signal = controller.signal

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

          if (strategy === 'error') {
            nuxt.payload.error = createError({
              statusCode: ctx.response.status,
              statusMessage: `${ctx.response.statusText} ${ctx.response.url}`,
            })
            return
          }
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
