import type { APIConfig } from './types'

export default <APIConfig>{
  baseURL: import.meta.env.VITE_API_BASE_URL as string,
  trailingSlash: true,
  protected: true,
  unauthorized: {
    statusCodes: [401],
    strategy: 'redirect',
    redirect: '/login',
  },
  authorizationHeader: 'Authorization',
  authorizationTokenPrefix: 'Token',
}
