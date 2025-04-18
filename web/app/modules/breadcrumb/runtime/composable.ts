import type { NuxtLinkProps } from 'nuxt/app'
import type { MaybeRefOrGetter } from 'vue'
import type { RouteMeta } from 'vue-router'

import { defu } from 'defu'
import { withoutTrailingSlash } from 'ufo'

import { pathBreadcrumbSegments, titleCase, withoutQuery } from './utils'

export interface BreadcrumbProps {
  /**
   * Generate the breadcrumbs based on a different path than the current route.
   */
  path?: MaybeRefOrGetter<string>
  /**
   * The id of the breadcrumb list. It's recommended to provide a unique
   * id when adding multiple breadcrumb lists to the same page.
   */
  id?: string
  /**
   * Append additional breadcrumb items to the end of the list. This is applied
   * after the `overrides` option.
   */
  append?: MaybeRefOrGetter<BreadcrumbItemProps[]>
  /**
   * Prepend additional breadcrumb items to the start of the list. This is applied
   * after the `overrides` option.
   */
  prepend?: MaybeRefOrGetter<BreadcrumbItemProps[]>
  /**
   * Override any of the breadcrumb items based on the index.
   */
  overrides?: MaybeRefOrGetter<(BreadcrumbItemProps | false | undefined)[]>
  /**
   * The Aria Label for the breadcrumbs.
   * You shouldn't need to change this.
   *
   * @default 'Breadcrumbs'
   */
  ariaLabel?: string
  /**
   * Should the current breadcrumb item be shown.
   *
   * @default false
   */
  hideCurrent?: MaybeRefOrGetter<boolean>
  /**
   * Should the root breadcrumb be shown.
   */
  hideRoot?: MaybeRefOrGetter<boolean>
}

export interface BreadcrumbItemProps extends Omit<NuxtLinkProps, 'to' | 'ariaCurrentValue'> {
  label: string
  labelClass?: string
  // icon?: string
  // iconClass?: string
  // as?: string
  // type?: string
  disabled?: boolean
  active?: boolean
  exact?: boolean
  exactQuery?: boolean
  exactMatch?: boolean
  inactiveClass?: string
  /** Whether the breadcrumb item represents the aria-current. */
  current?: boolean
  /**
   * The type of current location the breadcrumb item represents, if `isCurrent` is true.
   * @default 'page'
   */
  ariaCurrent?: NuxtLinkProps['ariaCurrentValue'] | boolean
  to?: NuxtLinkProps['to']
  ariaLabel?: string
  separator?: boolean | string
  class?: (string | string[] | undefined)[] | string

  [key: string]: any
}

export function useBreadcrumbItems(options: BreadcrumbProps = {}) {
  const router = useRouter()

  const items = computed(() => {
    const rootNode = '/'

    const current = withoutQuery(withoutTrailingSlash(toValue(options.path || router.currentRoute.value?.path) || rootNode))!

    // apply overrides
    const overrides = toValue(options.overrides) || []

    const segments = pathBreadcrumbSegments(current, rootNode)
      .map((path, index) => {
        let item = <BreadcrumbItemProps>{
          to: path,
        }
        if (typeof overrides[index] !== 'undefined') {
          if (overrides[index] === false) {
            return false
          }
          item = defu(overrides[index] as any as BreadcrumbItemProps, item)
        }
        return item
      })

    // apply prepends and appends
    if (options.prepend) {
      segments.unshift(...toValue(options.prepend))
    }

    if (options.append) {
      segments.push(...toValue(options.append))
    }

    return (segments.filter(Boolean) as BreadcrumbItemProps[])
      .map((item) => {
        const route = router.resolve(item.to as string)?.matched?.[0]

        let fallbackLabel = titleCase(String((router.resolve(item.to || '').href || '').split('/').pop()))

        if (route) {
          const routeMeta = (route?.meta || {}) as RouteMeta & { title?: string, breadcrumbLabel: string, breadcrumbTitle: string }

          // merge with the route meta
          if (routeMeta.breadcrumb) {
            item = {
              ...item,
              ...routeMeta.breadcrumb,
            }
          }

          const routeName = String(route.name)
          if (routeName === 'index') {
            fallbackLabel = 'Home'
          }
          fallbackLabel = routeMeta.breadcrumbLabel || routeMeta.breadcrumbTitle || routeMeta.title || fallbackLabel
        }

        // allow opt-out of label normalise with `false` value
        item.label = item.label || fallbackLabel
        item.ariaLabel = item.ariaLabel || item.label || ''

        // mark the current based on the options
        item.current = item.current || item.to === current
        if (toValue(options.hideCurrent) && item.current) {
          return false
        }

        return item
      })
      .map((m) => {
        if (m && m.to) {
          // TODO: fix trailing slash
          if (m.to === rootNode && toValue(options.hideRoot)) {
            return false
          }
        }
        return m
      })
      .filter(Boolean) as BreadcrumbItemProps[]
  })

  return items
}
