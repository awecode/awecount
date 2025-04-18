import type { UseFetchOptions } from '#app'
import type { DefaultAsyncDataValue } from '#app/defaults'
import type { AvailableRouterMethod, NitroFetchOptions, NitroFetchRequest } from 'nitropack'

interface ExtraOptions {
  protected?: boolean
  trailingSlash?: boolean
  authNamespace?: string
  handleErrors?: boolean
}

// source: https://github.com/nuxt/nuxt/blob/6c98cdc645060b0eea311dcc42f8834a10117011/packages/nuxt@/app/composables/asyncData.ts#L17C1-L33C2
export type PickFrom<T, K extends Array<string>> = T extends Array<any>
  ? T
  : T extends Record<string, any>
    ? keyof T extends K[number]
      ? T // Exact same keys as the target, skip Pick
      : K[number] extends never
        ? T
        : Pick<T, K[number]>
    : T

export type KeysOf<T> = Array<
  T extends T // Include all keys of union types, not just common keys
    ? keyof T extends string
      ? keyof T
      : never
    : never
>

export type $APIOptions<R extends NitroFetchRequest> = NitroFetchOptions<R> & ExtraOptions

export type $API = <DefaultT = unknown, DefaultR extends NitroFetchRequest = NitroFetchRequest, T = DefaultT, R extends NitroFetchRequest = DefaultR, O extends $APIOptions<R> = $APIOptions<R>> (request: R, opts?: O) => ReturnType<typeof $fetch<T>>

export type UseAPIOptions<ResT, DataT = ResT, PickKeys extends KeysOf<DataT> = KeysOf<DataT>, DefaultT = DefaultAsyncDataValue, R extends NitroFetchRequest = string & {}, M extends AvailableRouterMethod<R> = AvailableRouterMethod<R>> = UseFetchOptions<ResT, DataT, PickKeys, DefaultT, R, M> & ExtraOptions
