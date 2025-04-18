import { addImports, createResolver, defineNuxtModule } from 'nuxt/kit'

const declaration = (resolver: ReturnType<typeof createResolver>) => `
import type { BreadcrumbItemProps } from '${resolver.resolve('./runtime/composable')}'
declare module '#app' {
  interface PageMeta {
    breadcrumb?: BreadcrumbItemProps
  }
}
`

export default defineNuxtModule({
  meta: {
    name: 'breadcrumb',
  },
  async setup(options, nuxt) {
    const resolver = createResolver(import.meta.url)

    await addImports([{ name: 'useBreadcrumbItems', from: resolver.resolve('./runtime/composable') }])

    nuxt.hook('prepare:types', ({ declarations }) => {
      declarations.push(declaration(resolver))
    })
  },
})
