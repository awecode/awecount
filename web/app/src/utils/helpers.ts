function parseErrors(errors: Record<string, any>) {
  return Object.fromEntries(
    Object.entries(errors).map(([k, v]) => {
      let val = v
      if (Array.isArray(val)) {
        if (typeof val[0] === 'object') {
        } else {
          val = val.join(' ')
        }
      }
      return [k, val]
    }),
  )
}

export { parseErrors }
