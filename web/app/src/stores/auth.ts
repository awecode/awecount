import type { RouteLocationNormalized, Router } from 'vue-router'
import { acceptHMRUpdate, defineStore } from 'pinia'
import * as config from 'src/config'

interface User {
  access_level: 'owner' | 'admin' | 'member'
  email: string
  display_name: string
  roles: string[]
  permissions: Record<string, Record<string, boolean>>
  [key: string]: any
}

interface Company {
  slug: string
  name: string
  [key: string]: any
}

const BASE_PREFIX = '_allauth/app/v1'

export const AuthProcess = {
  LOGIN: 'login',
  CONNECT: 'connect',
} as const

type AuthProcessType = (typeof AuthProcess)[keyof typeof AuthProcess]

export const URLs = {
  LOGIN: `${BASE_PREFIX}/auth/login`,
  SESSION: `${BASE_PREFIX}/auth/session`,
  SESSION_TOKEN: `${BASE_PREFIX}/auth/session/token`,
  SIGNUP: `${BASE_PREFIX}/auth/signup`,
  REQUEST_PASSWORD_RESET: `${BASE_PREFIX}/auth/password/request`,
  RESET_PASSWORD: `${BASE_PREFIX}/auth/password/reset`,
  VERIFY_EMAIL: `${BASE_PREFIX}/auth/email/verify`,
  REQUEST_VERIFICATION_EMAIL: `${BASE_PREFIX}/auth/email/request-verification`,
  PROVIDERS: `${BASE_PREFIX}/account/providers`,
  EMAIL: `${BASE_PREFIX}/account/email`,
  CHECK_EMAIL: `${BASE_PREFIX}/auth/email/check`,
  CHANGE_PASSWORD: `${BASE_PREFIX}/account/password/change`,

  // Switch company
  SWITCH_COMPANY: `/api/user/me/switch-company/`,

  // Auth: Social
  PROVIDER_SIGNUP: `${BASE_PREFIX}/auth/provider/signup`,
  PROVIDER_TOKEN: `${BASE_PREFIX}/auth/provider/token`,
  PROVIDER_CALLBACK: `${BASE_PREFIX}/auth/provider/callback`,
  REDIRECT_TO_PROVIDER: `${BASE_PREFIX}/auth/provider/redirect`,
} as const

export const useAuthStore = defineStore(
  'auth',
  () => {
    const url = new URL(window.location.href)

    const $api = useAPI

    const user = ref<User | null>(null)
    const company = ref<Company | null>(null)

    const accessToken = ref<string | null>(null)
    const refreshToken = ref<string | null>(null)
    const sessionToken = ref<string | null>(null)
    const authenticatedAt = ref<number | null>(null)

    const isAuthenticated = computed(() => !!accessToken.value && !!refreshToken.value)
    const onboarded = computed(() => user.value?.is_onboarded)

    const _roles = ref<string[]>([])
    const _permissions = ref<Record<string, Record<string, boolean>>>({})

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

    const _handleAuthSuccess = (data: any, meta: any) => {
      user.value = data?.user
      sessionToken.value = meta?.session_token
      accessToken.value = meta?.access_token
      refreshToken.value = meta?.refresh_token
      authenticatedAt.value = Date.now()
    }

    const _resetAuthState = () => {
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      sessionToken.value = null
      authenticatedAt.value = null
      company.value = null
    }

    const _fetchPermissions = async (companySlug: string) => {
      const res = await $api(`/api/company/${companySlug}/permissions/mine/`, {
        method: 'GET',
        protected: true,
      })

      _roles.value = [...(res?.roles || []), ...(res?.role ? [res.role] : [])]
      _permissions.value = Object.fromEntries(
        Object.entries(res?.permissions || {}).map(([key, value]) => [key.replace(/_/g, ''), value]),
      ) as Record<string, Record<string, boolean>>

      return res
    }

    const _fetchCompany = async (companySlug: string) => {
      const res = await $api(`/api/company/${companySlug}/`, {
        method: 'GET',
        protected: true,
      })

      company.value = res

      return res
    }

    const _handleRedirect = async (redirectData: any, explicitRedirectTo?: string | false) => {
      if (explicitRedirectTo === false) {
        return
      }
      if (explicitRedirectTo === undefined && redirectData?.redirect) {
        const next = redirectData.redirect
        switch (next) {
          case 'onboarding':
            if (config.auth.onboarding.enabled) {
              window.location.href = `${url.origin}${config.auth.onboarding.route}`
            } else {
              throw new Error('Onboarding is not enabled')
            }
            break
          case 'invitations':
            window.location.href = `${url.origin}/invitations`
            break
          case 'create-company':
            window.location.href = `${url.origin}/company/create`
            break
          case null:
          case undefined:
          case '':
            break
          default:
            await _fetchPermissions(next) // next is the company slug
            await _fetchCompany(next) // next is the company slug
            window.location.href = `${url.origin}/${next}/dashboard`
            break
        }
      }

      // if (explicitRedirectTo === undefined && route.query.next) {
      //   window.location.href = `${url.origin}${route.query.next}`
      // }

      if (explicitRedirectTo) {
        window.location.href = `${url.origin}${explicitRedirectTo}`
      }
    }

    const login = async (credentials: { email: string, password: string }, { redirectTo }: { redirectTo?: string | false } = {}) => {
      const { data, meta } = await _request<any>(URLs.LOGIN, { method: 'POST', body: credentials })
      _handleAuthSuccess(data, meta)
      await _handleRedirect(data?.user, redirectTo)
      return data
    }

    const logout = async ({ redirectTo }: { redirectTo?: string } = {}) => {
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
            window.location.href = `${url.origin}${redirectTo}`
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

      _handleRedirect(data?.user)

      return data
    }

    const requestPasswordReset = async (email: string) => {
      return await _request(URLs.REQUEST_PASSWORD_RESET, { method: 'POST', body: { email } })
    }

    const resetPassword = async (data: Record<string, any>) => {
      try {
        return await _request(URLs.RESET_PASSWORD, { method: 'POST', body: data })
      } catch (error) {
        if (error.response?.status === 401) {
          return error.response._data
        }
        throw error
      }
    }

    const checkEmail = async (email: string) => {
      return await _request(URLs.CHECK_EMAIL, { method: 'POST', body: { email } })
    }

    const verifyEmail = async (key: string) => {
      const { data, meta } = await _request<any>(URLs.VERIFY_EMAIL, { method: 'POST', body: { key } })
      _handleAuthSuccess(data, meta)
      await _handleRedirect(data?.user)
      return data
    }

    const resendVerificationEmail = async (email: string) => {
      return await _request(URLs.EMAIL, { method: 'PUT', body: { email } })
    }

    const requestEmailVerification = async (email: string) => {
      return await _request(URLs.REQUEST_VERIFICATION_EMAIL, { method: 'POST', body: { email } })
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
        _handleAuthSuccess(data, meta)
        await _handleRedirect(data?.user)
        return data
      } catch (error) {
        _resetAuthState()
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
      try {
        return await _request(URLs.CHANGE_PASSWORD, { method: 'POST', body: data })
      } catch (error) {
        if (error.response?.status === 401) {
          return error.response._data
        }
        throw error
      }
    }

    // TODO: move this to a separate store/composable
    const switchCompany = async (companySlug: string, { router, route }: { router?: Router, route?: RouteLocationNormalized } = {}) => {
      if (companySlug === user.value?.redirect && !(route?.params?.company && route.params.company !== companySlug)) {
        return
      }

      try {
        const res = await $api(URLs.SWITCH_COMPANY, { method: 'PATCH', body: { company_slug: companySlug } })
        user.value.redirect = companySlug
        await _fetchCompany(companySlug)
        await _fetchPermissions(companySlug)
        // if (router && route) {
        //   router.push({ name: route.name, params: { company: companySlug }, query: route.query, hash: route.hash })
        // } else {
        // }
        window.location.href = `${url.origin}/${companySlug}/dashboard`
        return res
      } catch (error) {
        if (error.response?.status === 404 && !['onboarding', 'invitations', 'create-company'].includes(companySlug)) {
          return switchCompany(user.value?.redirect, { router, route })
        }
        throw error
      }
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

    const _hasFullAccess = () => {
      return hasAnyRole(config.auth.fullAccessRoles)
    }

    type Permission = `${string}.${string}` | string

    const hasPermission = (permission: Permission) => {
      // Check for full access roles first
      if (_hasFullAccess()) return true

      if (Object.keys(_permissions.value || {}).length === 0) return false

      if (permission.includes('.')) {
        const [resource, action] = permission.split('.')
        return _permissions.value?.[resource]?.[action] ?? false
      }

      // Resource-only check - return true if any action is allowed for this resource
      return Object.keys(_permissions.value?.[permission] || {}).some(action => _permissions.value?.[permission]?.[action] === true)
    }

    const hasAnyPermission = (permissions: Permission[]) => {
      // Check for full access roles first
      if (_hasFullAccess()) return true

      if (!_permissions.value) return false
      return permissions.some(permission => hasPermission(permission))
    }

    const hasAllPermissions = (permissions: Permission[]) => {
      // Check for full access roles first
      if (_hasFullAccess()) return true

      if (!_permissions.value) return false
      return permissions.every(permission => hasPermission(permission))
    }

    return {
      token: accessToken,
      refreshToken,
      sessionToken,
      user,
      company,
      isAuthenticated,
      onboarded,
      roles: _roles, // FIXME: Save this without exposing
      permissions: _permissions, // FIXME: Save this without exposing
      switchCompany,
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
      checkEmail,
      changePassword,
      providerSignup,
      redirectToProvider,
      refreshUser,
      requestEmailVerification,
      resendVerificationEmail,
      getProviderAccounts,
      disconnectProviderAccount,
      getEmailAddresses,
      addEmail,
      deleteEmail,
      markEmailAsPrimary,
      providerCallback,
    }
  },
  {
    persist: true,
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot))
}
