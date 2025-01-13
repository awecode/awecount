export interface APIConfig {
  baseURL: string
  trailingSlash: boolean
  protected: boolean
  unauthorized?:
    | {
        redirect: string
        statusCodes: number[]
        strategy: 'redirect'
      }
    | {
        statusCodes: number[]
        strategy: 'error'
      }
  authorizationHeader?: string
  authorizationTokenPrefix?: string
}

export interface AuthConfig {
  loginRoute?: string
  fullAccessRoles?: string[]
  redirectIfNotAllowed?: string | false
  onboarding?: { enabled?: false } | { enabled: true; route: string }
}
