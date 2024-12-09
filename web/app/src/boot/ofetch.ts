import { defineBoot } from '#q-app/wrappers'
import { ofetch } from 'ofetch'

const api = ofetch.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

export default defineBoot(({ app }) => {
  app.config.globalProperties.$ofetch = ofetch
  app.config.globalProperties.$api = api
})

export { api }
