import type { AuthConfig } from './types'

export default <AuthConfig>{
  loginRoute: '/login',
  fullAccessRoles: ['owner', 'admin'],
  redirectIfNotAllowed: false,
  onboarding: {
    enabled: true,
    route: '/onboarding',
  },
}
