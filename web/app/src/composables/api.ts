import type { FetchOptions, FetchRequest, ResponseType } from 'ofetch'
import type { RouteLocationRaw } from 'vue-router'

import { ofetch } from 'ofetch'
import * as config from 'src/config'

import { useAuthStore } from 'stores/auth'

type UseAPIOptions<R extends ResponseType = ResponseType, T = any> = FetchOptions<R, T> & {
  protected?: boolean
  trailingSlash?: boolean
  handleErrors?: boolean
}

const isURL = (str: string) => {
  try {
    return Boolean(new URL(str))
  } catch {
    return false
  }
}

const handleTrailingSlash = (url: string, trailingSlash?: boolean) => {
  if (typeof trailingSlash === 'undefined') {
    return url
  }

  const hasTrailingSlash = url.endsWith('/')
  return hasTrailingSlash === trailingSlash
    ? url
    : trailingSlash
      ? `${url}/`
      : url.slice(0, -1)
}

export const useAPI = <
  T = any,
  R extends ResponseType = 'json',
>(request: FetchRequest,
  opts?: UseAPIOptions<R, T>,
) => {
  const router = useRouter()
  const {
    onRequest,
    onResponseError,
    handleErrors = true,
    protected: _protected = config.api.protected,
    trailingSlash = config.api.trailingSlash,
    ...options
  } = opts || {}

  const { token } = useAuthStore()

  let controller: AbortController | null = null

  onBeforeUnmount(() => {
    controller?.abort()
  })

  return ofetch<T, R>(request, {
    onRequest: async (ctx) => {
      controller?.abort()
      controller = new AbortController()
      ctx.options.signal = controller.signal

      // await onRequest?.(ctx)

      ctx.options.method ||= 'GET'

      if (typeof ctx.request === 'string') {
        ctx.request = handleTrailingSlash(ctx.request, trailingSlash)
        if (!options.baseURL && !isURL(ctx.request)) {
          ctx.options.baseURL = config.api.baseURL
        }
      }

      if (_protected && token && !ctx.options.headers.get('Authorization')) {
        ctx.options.headers.set(config.api.authorizationHeader, `${config.api.authorizationTokenPrefix} ${token}`)
      }
    },

    onResponseError: async (ctx) => {
      // await onResponseError?.(ctx)
      if (!handleErrors) return

      // Handle unauthorized/forbidden responses based on config
      if (_protected && config.api.unauthorized) {
        const { statusCodes, strategy, redirect } = config.api.unauthorized as { statusCodes: number[], strategy: 'redirect' | 'error', redirect?: RouteLocationRaw }

        if (statusCodes.includes(ctx.response.status)) {
          if (strategy === 'redirect' && redirect) {
            await router.push(redirect)
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

        // nuxt.payload.error = createError({
        //   statusCode: ctx.response.status,
        //   statusMessage: `${ctx.response.statusText} ${ctx.response.url}`,
        // })
        // TODO: what's the equivalent of nuxt.payload.error in Quasar?
      }
    },
    ...options,
  })
}
