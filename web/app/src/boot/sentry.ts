import { defineBoot } from '#q-app/wrappers'
import * as Sentry from '@sentry/vue'

export default defineBoot(({ app }) => {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    enabled: !import.meta.env.DEV,
    integrations: [],
    trackComponents: true,
  })
})
