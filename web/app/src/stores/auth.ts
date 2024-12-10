import type { RouteLocationRaw } from 'vue-router'
import { acceptHMRUpdate, defineStore } from 'pinia'

import * as config from 'src/config'

interface User {
  access_level: 'owner' | 'admin' | 'member'
  email: string
  display_name: string
  roles: string[]
  permissions: string[]
  [key: string]: any
}

const BASE_PREFIX = '_allauth/app/v1'

export const AuthProcess = {
  LOGIN: 'login',
  CONNECT: 'connect',
} as const

type AuthProcessType = typeof AuthProcess[keyof typeof AuthProcess]

export const URLs = {
  LOGIN: `${BASE_PREFIX}/auth/login`,
  SESSION: `${BASE_PREFIX}/auth/session`,
  SESSION_TOKEN: `${BASE_PREFIX}/auth/session/token`,
  SIGNUP: `${BASE_PREFIX}/auth/signup`,
  REQUEST_PASSWORD_RESET: `${BASE_PREFIX}/auth/password/request`,
  RESET_PASSWORD: `${BASE_PREFIX}/auth/password/reset`,
  VERIFY_EMAIL: `${BASE_PREFIX}/auth/email/verify`,
  PROVIDERS: `${BASE_PREFIX}/account/providers`,
  EMAIL: `${BASE_PREFIX}/account/email`,
  CHANGE_PASSWORD: `${BASE_PREFIX}/account/password/change`,

  // Auth: Social
  PROVIDER_SIGNUP: `${BASE_PREFIX}/auth/provider/signup`,
  PROVIDER_TOKEN: `${BASE_PREFIX}/auth/provider/token`,
  PROVIDER_CALLBACK: `${BASE_PREFIX}/auth/provider/callback`,
  REDIRECT_TO_PROVIDER: `${BASE_PREFIX}/auth/provider/redirect`,
} as const

export const useAuthStore = defineStore('auth', () => {
  const url = new URL(window.location.href)
  const route = useRoute()
  const router = useRouter()

  const $api = useAPI

  const user = ref<User | null>(null)

  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const sessionToken = ref<string | null>(null)
  const authenticatedAt = ref<number | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value && !!sessionToken.value)
  const onboarded = computed(() => user.value?.teams?.length > 0 && user.value?.last_active_team)

  const _roles = computed(() => [
    ...(user.value?.roles || []),
    ...(user.value?.access_level ? [user.value.access_level] : []),
  ])

  const _permissions = computed(() => user.value?.permissions || [])

  const _request = async <T = Record<string, any>>(url: string, options: Record<string, any>) => {
    options.headers = options.headers || {}

    if (sessionToken.value) {
      options.headers['X-Session-Token'] = sessionToken.value
    }

    return await $api<T>(url, {
      ...options,
      trailingSlash: false,
      handleErrors: false,
      onResponse: async ({ response }) => {
        if ([200, 401].includes(response.status) && response._data?.meta?.session_token) {
          sessionToken.value = response._data.meta.session_token
        }
      },
    })
  }

  const _postForm = async (url: string, data: Record<string, any>) => {
    const f = document.createElement('form')
    f.method = 'POST'
    f.action = url
    Object.entries(data).forEach(([key, val]) => {
      const input = document.createElement('input')
      input.type = 'hidden'
      input.name = key
      input.value = val
      f.appendChild(input)
    })

    document.body.appendChild(f)
    f.submit()
  }

  const login = async (credentials: { email: string, password: string }, { redirectTo }: { redirectTo?: RouteLocationRaw | false } = {}) => {
    try {
      const { data, meta } = await _request<any>(URLs.LOGIN, { method: 'POST', body: credentials })

      user.value = data?.user
      sessionToken.value = meta?.session_token
      accessToken.value = meta?.access_token
      refreshToken.value = meta?.refresh_token
      authenticatedAt.value = Date.now()

      if (redirectTo !== false) {
        if (redirectTo === undefined && route.query.next) {
          await router.push(route.query.next.toString())
        }

        if (redirectTo) {
          await router.push(redirectTo)
        }

        if (!onboarded.value && config.auth.onboarding.enabled) {
          await router.push(config.auth.onboarding.route)
        }

        await router.push({ name: 'team-dashboard', params: { team: user.value?.last_active_team?.slug } })
      }

      return data
    } catch (error) {
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      sessionToken.value = null
      authenticatedAt.value = null

      throw error
    }
  }

  const logout = async ({ redirectTo }: { redirectTo?: RouteLocationRaw } = {}) => {
    try {
      await _request(URLs.SESSION, { method: 'DELETE' })
    } catch (error: any) {
      if ([401, 410].includes(error.response?.status)) {
        user.value = null
        accessToken.value = null
        refreshToken.value = null
        sessionToken.value = null
        authenticatedAt.value = null
        if (redirectTo) {
          await router.push(redirectTo)
        }
      } else {
        throw error
      }
    }
  }

  // Allauth helper functions
  const signup = async (data: Record<string, any>) => {
    return await _request(URLs.SIGNUP, { method: 'POST', body: data })
  }

  const refreshUser = async () => {
    const { data } = await _request<any>(URLs.SESSION, { method: 'GET' })

    user.value = data?.user

    return data
  }

  const requestPasswordReset = async (email: string) => {
    return await _request(URLs.REQUEST_PASSWORD_RESET, { method: 'POST', body: { email } })
  }

  const resetPassword = async (data: Record<string, any>) => {
    return await _request(URLs.RESET_PASSWORD, { method: 'POST', body: data })
  }

  const verifyEmail = async (key: string) => {
    const { data, meta } = await _request<any>(URLs.VERIFY_EMAIL, { method: 'POST', body: { key } })

    user.value = data?.user
    sessionToken.value = meta?.session_token
    accessToken.value = meta?.access_token
    refreshToken.value = meta?.refresh_token
    authenticatedAt.value = Date.now()

    return data
  }

  const resendVerificationEmail = async (email: string) => {
    return await _request(URLs.EMAIL, { method: 'PUT', body: { email } })
  }

  const redirectToProvider = async ({ provider, redirect, process = 'login' }: { provider: string, redirect?: string, process?: AuthProcessType }) => {
    _postForm(`${config.api.baseURL}/${URLs.REDIRECT_TO_PROVIDER}`, {
      provider,
      process,
      callback_url: redirect ?? `${url.origin}/auth/${provider}/callback/`,
    })
  }

  const providerCallback = async (provider: string, payload: Record<string, any>) => {
    try {
      const { data, meta } = await _request<any>(`${URLs.PROVIDER_CALLBACK}/${provider}`, { method: 'POST', body: payload })

      user.value = data?.user
      sessionToken.value = meta?.session_token
      accessToken.value = meta?.access_token
      refreshToken.value = meta?.refresh_token
      authenticatedAt.value = Date.now()

      if (!onboarded.value && config.auth.onboarding.enabled) {
        await router.push(config.auth.onboarding.route)
      }

      await router.push({ name: 'team-dashboard', params: { team: user.value?.last_active_team?.slug } })

      return data
    } catch (error) {
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      sessionToken.value = null
      authenticatedAt.value = null

      throw error
    }
  }

  const providerSignup = async ({ email }: { email: string }) => {
    return await _request(URLs.PROVIDER_SIGNUP, { method: 'POST', body: { email } })
  }

  const getProviderAccounts = async () => {
    return await _request(URLs.PROVIDERS, { method: 'GET' })
  }

  const disconnectProviderAccount = async (providerId: string, accountUid: string) => {
    return await _request(URLs.PROVIDERS, { method: 'DELETE', body: { provider: providerId, account: accountUid } })
  }

  const getEmailAddresses = async () => {
    return await _request(URLs.EMAIL, { method: 'GET' })
  }

  const addEmail = async (email: string) => {
    return await _request(URLs.EMAIL, { method: 'POST', body: { email } })
  }

  const deleteEmail = async (email: string) => {
    return await _request(URLs.EMAIL, { method: 'DELETE', body: { email } })
  }

  const markEmailAsPrimary = async (email: string) => {
    return await _request(URLs.EMAIL, { method: 'PATCH', body: { email, primary: true } })
  }

  const changePassword = async (data: Record<string, any>) => {
    return await _request(URLs.CHANGE_PASSWORD, { method: 'POST', body: data })
  }

  const hasPermission = (permission: string) => {
    if (!_permissions.value?.includes(permission)) return false
    return _permissions.value.includes(permission)
  }

  const hasAnyPermission = (permissions: string[]) => {
    if (!_permissions.value?.length) return false
    return permissions.some(permission => _permissions.value!.includes(permission))
  }

  const hasAllPermissions = (permissions: string[]) => {
    if (!_permissions.value?.length) return false
    return permissions.every(permission => _permissions.value!.includes(permission))
  }

  const hasRole = (role: string) => {
    if (!_roles.value?.includes(role)) return false
    return _roles.value.includes(role)
  }

  const hasAnyRole = (roles: string[]) => {
    if (!_roles.value?.length) return false
    return roles.some(role => _roles.value!.includes(role))
  }

  const hasAllRoles = (roles: string[]) => {
    if (!_roles.value.length) return false
    return roles.every(role => _roles.value.includes(role))
  }

  return {
    token: shallowReadonly(accessToken),
    user: shallowReadonly(user),
    isAuthenticated,
    onboarded,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    hasAllRoles,
    login,
    logout,
    signup,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    changePassword,
    providerSignup,
    redirectToProvider,
    refreshUser,
    resendVerificationEmail,
    getProviderAccounts,
    disconnectProviderAccount,
    getEmailAddresses,
    addEmail,
    deleteEmail,
    markEmailAsPrimary,
    providerCallback,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot))
}
