import { addImports, createResolver, defineNuxtModule } from 'nuxt/kit'

export default defineNuxtModule({
  meta: {
    name: 'stateful-cookie',
  },
  async setup(options, nuxt) {
    const { resolve } = createResolver(import.meta.url)

    await addImports([{ name: 'useStatefulCookie', from: resolve('./runtime/composable') }])

    nuxt.hook('prepare:types', ({ declarations }) => {
      declarations.push('')
      declarations.push(`export type { StatefulCookieOptions } from '${resolve('./runtime/composable')}'`)
    })
  },
})
