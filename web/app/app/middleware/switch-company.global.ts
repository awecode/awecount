/**
 * List of paths that don't require company context and should bypass company switching logic.
 * These are public routes that are accessible without company context.
 */
const publicPaths = [
  '/login',
  '/signup',
  '/auth',
  '/404',
  '/forbidden',
  '/',
  '/onboarding',
  '/company/create',
  '/profile',
  '/invitations',
]

/**
 * Middleware that handles company switching and 404 route resolution.
 *
 * This middleware provides three main functionalities:
 * 1. Bypasses company switching for public paths
 * 2. Handles 404 routes by attempting to resolve them with company slug (for backward compatibility)
 * 3. Manages company switching when navigating directly to a different company via URL
 *
 * Behavior:
 * - For public paths: Allows navigation without company context
 * - For 404 routes: Attempts to resolve the route by prepending company slug
 * - For company switching: Handles direct navigation to different company via URL
 *
 * Example scenarios:
 * 1. Direct company switch:
 *    - Current URL: /company-123/sales
 *    - User enters: /different-company/sales
 *    - Guard will trigger company switch to 'different-company'
 *
 * 2. 404 resolution:
 *    - User enters: /sales/vouchers (without company slug)
 *    - Route resolves to 404
 *    - Guard attempts: /company-123/sales/vouchers
 *    - If valid route exists, redirects to it
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const router = useRouter()

  const { user, switchCompany } = useAuth()

  // Skip company switching logic for public paths
  if (publicPaths.includes(to.path)) {
    return
  }

  // Handle 404 routes by attempting to resolve with company slug
  // This provides backward compatibility for URLs without company slug
  if (to.matched.length === 0) {
    const resolved = router.resolve(`/${user.value?.redirect}${to.fullPath}`)
    if (resolved.matched.length === 0) {
      return
    }
    return navigateTo({ name: resolved.name as string, params: resolved.params, query: resolved.query, hash: resolved.hash })
  }

  // Handle direct navigation to a different company via URL
  // This allows users to switch companies by entering a different company's URL
  if (from.params.company === undefined && to.params.company && to.params.company !== user.value?.redirect) {
    await switchCompany(to.params.company as string, { router, route: to })
  }
})
