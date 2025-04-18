import type { CookieOptions } from 'nuxt/app'
import type { Ref, WatchCallback } from 'vue'

import { useCookie, useState } from 'nuxt/app'
import { shallowReadonly, watch } from 'vue'

export type StatefulCookieOptions<T> = CookieOptions<T> & { readonly?: boolean, encrypted?: boolean }

export function useStatefulCookie<T = string | null | undefined>(name: string, options: StatefulCookieOptions<T> & { readonly: true }): Readonly<Ref<T>>
export function useStatefulCookie<T = string | null | undefined>(name: string, options?: StatefulCookieOptions<T>): Ref<T>
export function useStatefulCookie<T = string | null | undefined>(name: string, options: StatefulCookieOptions<T> = {}) {
  const _opts = { ...options, readonly: false } as CookieOptions<T> & { readonly: false }

  const cookie = useCookie<T>(name, _opts)
  const state = useState<T>(`cookies:${name}`, () => cookie.value)

  const callback: WatchCallback<T, T> = () => {
    cookie.value = state.value
  }

  watch(state, callback, { deep: true })

  return options.readonly ? shallowReadonly(state) : state
}
