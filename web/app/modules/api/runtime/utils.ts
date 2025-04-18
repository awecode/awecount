export const isURL = (str: string) => {
  try {
    return Boolean(new URL(str))
  } catch {
    return false
  }
}

export const handleTrailingSlash = (url: string, trailingSlash?: boolean) => {
  if (typeof trailingSlash === 'undefined') {
    return url
  }

  const urlObj = new URL(url, 'http://dummy-base')
  const hasTrailingSlash = urlObj.pathname.endsWith('/')

  urlObj.pathname = hasTrailingSlash === trailingSlash
      ? urlObj.pathname
      : trailingSlash
        ? `${urlObj.pathname}/`
        : urlObj.pathname.slice(0, -1)

  return urlObj.href.replace('http://dummy-base', '')
}
