const useHandleFormError = (data) => {
  let message = ''
  let errors = {}
  if (data.status == 400) {
    message = 'Please fill out the form correctly.'
    if (data.data?.detail) {
      message = `${data.data.detail}`
    }
    // processErrors(data.response._data)
    const dct = Object.fromEntries(
      Object.entries(data.response._data).map(([k, v]) => {
        let val = v
        if (Array.isArray(val)) {
          if (typeof val[0] === 'object') {
          } else val = val.join(' ')
        }
        return [k, val]
      })
    )
    errors = dct
  }
  if (data.status == 404) {
    if (data.data?.detail && data.data?.detail !== 'Not found.' ) {
      message = `Not found - ${data.data.detail}`
    } else {
      message = 'Not found!'
    }
  } else if (data.status == 500) {
    message = 'Server Error! Please contact us with the problem.'
  }
  return {
    errors,
    message
  }
}

export default useHandleFormError
