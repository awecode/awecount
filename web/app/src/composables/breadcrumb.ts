import type { RouteMeta } from 'vue-router'

import { hasTrailingSlash, parseURL, stringifyParsedURL, withoutTrailingSlash, withTrailingSlash } from 'ufo'

const pathBreadcrumbSegments = (path: string, rootNode: string = '/'): string[] => {
  const startNode = parseURL(path)
  const appendsTrailingSlash = hasTrailingSlash(startNode.pathname)

  const stepNode = (node: ReturnType<typeof parseURL>, nodes: string[] = []) => {
    const fullPath = stringifyParsedURL(node)
    // the pathname will always be without the trailing slash
    const currentPathName = node.pathname || '/'
    // when we hit the root the path will be an empty string; we swap it out for a slash
    nodes.push(fullPath || '/')
    if (currentPathName !== rootNode && currentPathName !== '/') {
      // strip the last path segment (/my/cool/path -> /my/cool)
      node.pathname = currentPathName.substring(0, currentPathName.lastIndexOf('/'))
      // if the input was provided with a trailing slash we need to honour that
      if (appendsTrailingSlash) {
        node.pathname = withTrailingSlash(node.pathname.substring(0, node.pathname.lastIndexOf('/')))
      }
      stepNode(node, nodes)
    }
    return nodes
  }
  return stepNode(startNode).reverse()
}

const withoutQuery = (path: string) => {
  return path.split('?')[0]
}

const titleCase = (s: string) => {
  return s.replaceAll('-', ' ').replace(/\w\S*/g, w => w.charAt(0).toUpperCase() + w.substr(1).toLowerCase())
}

interface BreadcrumbItem {
  to: string
  label?: string
  current?: boolean
}

export const useBreadcrumbItems = () => {
  const router = useRouter()

  const items = computed(() => {
    const rootNode = '/'
    const current = withoutQuery(withoutTrailingSlash(toValue(router.currentRoute.value?.path) || rootNode))

    const segments = pathBreadcrumbSegments(current, rootNode).map(path => ({ to: path }) as BreadcrumbItem)

    return segments
      .filter(Boolean)
      .map((item) => {
        const resolved = router.resolve(item.to)
        const matchedLast = resolved?.matched?.[resolved?.matched?.length - 1]
        const route = matchedLast || router.currentRoute.value // fallback to current route
        const routeMeta = (route?.meta || {}) as RouteMeta & { title?: string, breadcrumbLabel: string }
        const routeName = route.name?.toString()
        const fallbackLabel = titleCase(routeName === 'index' ? 'Home' : (item.to || '').split('/').pop() || '') // fallback to last path segment

        // merge with the route meta
        if (routeMeta.breadcrumb) {
          item = {
            ...item,
            ...routeMeta.breadcrumb,
          }
        }

        // allow opt-out of label normalise with `false` value
        // @ts-expect-error untyped
        item.label = item.label || routeMeta.title || routeMeta.breadcrumbTitle || fallbackLabel

        // mark the current based on the options
        item.current = item.current || item.to === current
        return item
      })
      .map((m) => {
        if (m && m.to) {
          if (m.to === rootNode) {
            return false
          }
        }
        return m
      })
      .filter(Boolean) as BreadcrumbItem[]
  })

  return items
}
