import { useLoginStore } from 'src/stores/login-info'
import { useModalFormLoading } from 'src/stores/ModalFormLoading'
import { parseErrors } from 'src/utils/helpers'
import { joinURL, withoutTrailingSlash, withTrailingSlash } from 'ufo'
import { getCurrentInstance, useId } from 'vue'
import useApi from './useApi'

export default (endpoint, config) => {
  const $q = useQuasar()
  const fields = ref({})
  const errors = ref({})
  const loading = ref(false)
  const formDefaults = ref({})

  const isEdit = ref(false)
  const id = ref(null)

  const route = useRoute()
  const router = useRouter()

  const { emit, ...root } = getCurrentInstance()

  const isModal = !!root?.attrs['is-modal']
  let editId = root?.attrs['edit-id']?.toString()
  const defaultFieldsData = root?.attrs['default-fields'] || {}
  const store = useLoginStore()
  const modalFormLoading = useModalFormLoading()
  const today = new Date().toISOString().substring(0, 10)
  const isGetDefaultLoading = ref(false)
  const isGetEditLoading = ref(false)

  const modalId = useId()

  // seta a unique key for modal in ModalFormLoading store
  if (isModal) {
    modalFormLoading[modalId] = true
    emit('getModalId', modalId)
  } else {
    store.isLoading = true
  }

  const getDefaultsFetchUrl = () => {
    return config.createDefaultsEndpoint || joinURL(endpoint, 'create-defaults/')
  }

  const processErrors = (responseData) => {
    errors.value = parseErrors(responseData)
  }

  const removeLastUrlSegment = (url) => {
    const newParts = withoutTrailingSlash(url).split('/').slice(0, -1)
    return withTrailingSlash(joinURL('/', ...newParts))
  }

  function createErrorMessage(errorData) {
    const messages = []

    // Handle top-level 'detail' message directly from DRF
    if (typeof errorData === 'object' && errorData !== null && errorData.detail) {
      messages.push(errorData.detail)
      return messages // If a detail message exists, it often overrides other structured errors
    }

    if (typeof errorData === 'object' && errorData !== null) {
      for (const field in errorData) {
        if (Object.prototype.hasOwnProperty.call(errorData, field)) {
          const errors = errorData[field]

          if (field === 'landed_cost_rows' && Array.isArray(errors)) {
            errors.forEach((rowErrors, index) => {
              if (typeof rowErrors === 'object' && rowErrors !== null && Object.keys(rowErrors).length > 0) {
                for (const subField in rowErrors) {
                  if (Object.prototype.hasOwnProperty.call(rowErrors, subField)) {
                    const subFieldMessages = rowErrors[subField]
                    if (Array.isArray(subFieldMessages)) {
                      subFieldMessages.forEach((msg) => {
                        messages.unshift(`Landed Cost Row #${index + 1}: ${msg}`)
                      })
                    } else if (typeof subFieldMessages === 'string') {
                      const formattedSubField = subField.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                      messages.unshift(`Landed Cost Row #${index + 1}: ${formattedSubField}: ${subFieldMessages}`)
                    }
                  }
                }
              } else if (Array.isArray(rowErrors) && rowErrors.length > 0) {
                rowErrors.forEach((msg) => {
                  messages.unshift(`Landed Cost Row #${index + 1}: ${msg}`)
                })
              }
            })
          } else if (Array.isArray(errors)) {
            errors.forEach((msg) => {
              const formattedField = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
              messages.unshift(`${formattedField}: ${msg}`)
            })
          } else if (typeof errors === 'string') {
            const formattedField = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            messages.unshift(`${formattedField}: ${errors}`)
          }
        }
      }
    } else if (Array.isArray(errorData)) {
      errorData.forEach((itemError, index) => {
        if (typeof itemError === 'object' && itemError !== null && Object.keys(itemError).length > 0) {
          for (const field in itemError) {
            if (Object.prototype.hasOwnProperty.call(itemError, field)) {
              const fieldMessages = itemError[field]
              if (Array.isArray(fieldMessages)) {
                fieldMessages.forEach((msg) => {
                  const formattedField = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                  messages.unshift(`Item #${index + 1} - ${formattedField}: ${msg}`)
                })
              } else if (typeof fieldMessages === 'string') {
                const formattedField = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                messages.unshift(`Item #${index + 1} - ${formattedField}: ${fieldMessages}`)
              }
            }
          }
        } else if (typeof itemError === 'string') {
          messages.unshift(`Item #${index + 1}: ${itemError}`)
        }
      })
    }

    // Fallback if no specific messages were parsed
    if (messages.length === 0) {
      return ['Please fill out the form correctly or check your input.']
    }

    return messages
  }

  const submitForm = async () => {
    loading.value = true
    errors.value = {}
    let postEndpoint
    if (isEdit.value) {
      postEndpoint = withTrailingSlash(joinURL(endpoint, id.value))
    } else {
      postEndpoint = endpoint
    }
    const originalStatus = fields.value.status
    return await useApi(postEndpoint, {
      method: isEdit.value ? 'PATCH' : 'POST',
      body: fields.value,
    })
      .then((data) => {
        $q.notify({
          color: 'positive',
          message: 'Saved',
          icon: 'check_circle',
        })
        loading.value = false
        if (isModal) {
          emit('modalSignal', data)
        } else {
          if (config.successRoute) {
            const lastRoute = router.getRoutes()[0]
            if (lastRoute && lastRoute.path === config.successRoute) {
              router.go(-1)
            } else {
              router.push(config.successRoute)
            }
          } else {
            router.push(removeLastUrlSegment(route.path))
          }
        }
        return data
      })
      .catch((data) => {
        let messages = []
        if (data.status === 400) {
          const responseData = data.response._data || data.data
          messages = createErrorMessage(responseData)
          loading.value = false
          processErrors(responseData)
        }
        if (data.status === 404) {
          if (data.data?.detail) {
            messages = [`Not found - ${data.data.detail}`]
          } else {
            messages = ['Not found!']
          }
          loading.value = false
        } else if (data.status === 500) {
          messages = ['Server Error! Please contact us with the problem.']
          loading.value = false
        } else if (data.status === 422) {
          $q.dialog({
            title: `<span class="text-orange">${humanizeWord(data.data?.code)}!</span>`,
            message: `<span class="text-grey-8">Reason: ${data.data.detail}` + '<div class="text-body1 text-weight-medium text-grey-8 q-mt-md">Are you sure you want to Continue?</div>',
            cancel: true,
            html: true,
          })
            .onOk(() => {
              useApi(`${postEndpoint}?${data.data?.code}=true`, {
                method: isEdit.value ? 'PATCH' : 'POST',
                body: { ...fields.value, status: originalStatus },
              })
                .then((data) => {
                  $q.notify({
                    color: 'positive',
                    message: 'Saved',
                    icon: 'check_circle',
                  })
                  if (isModal) {
                    emit('modalSignal', data)
                  } else {
                    if (config.successRoute) {
                      router.push(config.successRoute)
                    } else {
                      router.push(removeLastUrlSegment(route.path))
                    }
                  }
                })
                .catch(() => {
                  $q.notify({
                    color: 'negative',
                    message: 'Something went Wrong!',
                    icon: 'report_problem',
                  })
                })
                .finally(() => {
                  loading.value = false
                })
            })
            .onCancel(() => {
              loading.value = false
            })
        } else {
          messages.forEach((msg) => {
            $q.notify({
              color: 'negative',
              message: msg,
              icon: 'report_problem',
            })
          })
          loading.value = false
        }
        return {
          error: 'Api Error',
        }
        // throw new Error('Api Error')
      })
  }

  const cancel = () => {
    if (isModal) {
      emit('closeModal')
    } else if (window.history.length > 2) {
      router.go(-1)
    } else {
      router.push(removeLastUrlSegment(route.path))
    }
  }

  const cancelForm = () => {
    if (isEdit.value) {
      const cancelEndPoint = withTrailingSlash(joinURL(endpoint, id.value, 'cancel'))
      useApi(cancelEndPoint, {
        method: 'POST',
      })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Success',
            icon: 'check_circle',
          })
          if (config.successRoute) {
            router.push(config.successRoute)
          }
        })
        .catch(() => {
          $q.notify({
            color: 'negative',
            message: 'error',
            icon: 'report_problem',
          })
        })
    }
  }

  const setModalLoadingFalse = () => {
    if (isModal && Object.hasOwn(modalFormLoading, `${modalId}`)) {
      modalFormLoading[modalId] = false
    }
  }

  onMounted(() => {
    if (!editId && !isModal) {
      editId = route.params.id
    }

    isEdit.value = !!editId

    if (!config.getDefaults && !isEdit.value) {
      store.isLoading = false
    } else {
      setModalLoadingFalse()
    }

    id.value = editId

    if (isEdit.value) {
      isGetEditLoading.value = true
      let fetchUrl = withTrailingSlash(joinURL(endpoint, id.value))
      if (config.queryParams) {
        const queryParams = new URLSearchParams(config.queryParams).toString()
        fetchUrl += `?${queryParams}`
      }
      useApi(fetchUrl)
        .then((data) => {
          fields.value = data
          isGetEditLoading.value = false
          if (!isGetDefaultLoading.value) {
            store.isLoading = false
          }
          setModalLoadingFalse()
        })
        .catch((error) => {
          isGetEditLoading.value = false
          if (!isGetEditLoading.value) {
            store.isLoading = false
            setModalLoadingFalse()
          }
          if (error.status === 404) {
            // router.push('/')
            $q.notify({
              color: 'negative',
              message: 'Not Found!',
              icon: 'report_problem',
            })
          }
        })
    }

    if (config.getDefaults) {
      isGetDefaultLoading.value = true
      useApi(getDefaultsFetchUrl(), { method: 'GET' }, false, true).then((data) => {
        if (data.fields) {
          if (!isEdit) fields.value = Object.assign(fields.value, data.fields)
        }

        if (defaultFieldsData) {
          for (const key in defaultFieldsData) {
            fields.value[key] = defaultFieldsData[key]
          }
        }

        // From drop down branch
        // TODO: resolve and remove this
        // delete data.collections
        // Object.assign(formDefaults.value, data)
        // Object.assign(fields.value, data.fields)
        // From drop down branch

        // From main
        formDefaults.value = data
        isGetDefaultLoading.value = false
        if (!isGetEditLoading.value) {
          store.isLoading = false
          setModalLoadingFalse()
        }
        // From main
      })
    }
  })

  onUnmounted(() => {
    if (isModal) {
      if (Object.hasOwn(modalFormLoading, `${modalId}`)) delete modalFormLoading[modalId]
    } else {
      store.isLoading = false
    }
  })

  return {
    fields,
    errors,
    isEdit,
    id,
    formDefaults,
    isModal,
    today,
    submitForm,
    cancel,
    cancelForm,
    loading,
  }
}
