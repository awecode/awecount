// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  future: {
    compatibilityVersion: 4,
  },

  modules: [
    'nuxt-quasar-ui',
    '@pinia/nuxt',
    'pinia-plugin-persistedstate/nuxt',
  ],

  ssr: false, // TODO: Remove this

  css: ['assets/css/app.scss'],

  quasar: {
    plugins: ['Notify', 'Dialog'],
    config: {
      notify: { position: 'top-right', progress: true },
    },
    extras: {
      font: 'roboto-font',
      fontIcons: ['mdi-v7', 'fontawesome-v6', 'material-icons'],
    },
  },

  api: {
    trailingSlash: true,
    protected: true,
  },

  auth: {
    loginRoute: '/login',
    fullAccessRoles: ['owner', 'admin'],
    redirectIfNotAllowed: false,
    onboarding: {
      enabled: true,
      route: '/onboarding',
    },
  },
})
