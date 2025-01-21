import { defineBoot } from '#q-app/wrappers'
import { ofetch } from 'ofetch'

import { api as apiConfig } from 'src/config'

const api = ofetch.create({
  baseURL: apiConfig.baseURL,
})

export default defineBoot(({ app }) => {
  app.config.globalProperties.$ofetch = ofetch
  app.config.globalProperties.$api = api
})

export { api }
