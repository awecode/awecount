import { boot } from 'quasar/wrappers'
import { ofetch } from 'ofetch'

// console.log(store.token)

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)

const api = ofetch.create({
  baseURL: process.env.BASE_URL,
})

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$ofetch and this.$api

  app.config.globalProperties.$ofetch = ofetch
  // ^ ^ ^ this will allow you to use this.$ofetch (for Vue Options API form)
  //       so you won't necessarily have to import ofetch in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})

export { api }
