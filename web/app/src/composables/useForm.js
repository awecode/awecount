// import { api } from 'boot/ofetch'
import { withTrailingSlash, withoutTrailingSlash, joinURL } from 'ufo'
import { getCurrentInstance } from 'vue'
import useApi from './useApi'
import { useLoginStore } from 'src/stores/login-info'
import { useModalFormLoading } from 'src/stores/ModalFormLoading'

// interface UseFormConfig {
//   getDefaults: boolean
//   successRoute: string
// }

// export default (endpoint: string, config: UseFormConfig) => {
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

  const root = getCurrentInstance()
  const context = root?.setupContext

  const isModal = !!root?.attrs['is-modal']
  const store = useLoginStore()
  const modalFormLoading = useModalFormLoading()
  const today = new Date().toISOString().substring(0, 10)
  store.isLoading = true
  const isGetDefaultLoading = ref(false)
  const isGetEditLoading = ref(false)
  const modalId = Math.floor(Math.random() * 999999999)
  // seta a unique key for modal in ModalFormLoading store
  if (isModal) {
    modalFormLoading[modalId] = true
    context.emit('getModalId', modalId)
  }
  onMounted(() => {
    // added is modal check
    isEdit.value = !!route.params.id && !isModal
    if ((!config.getDefaults && !isEdit.value && !isModal)) {
      store.isLoading = false
    }
    else if (isModal && (isEdit.value || config.getDefaults)) {
      store.isLoading = false
    } else setModalLoadingFalse()
    id.value = route.params.id
    if (isEdit.value) {
      isGetEditLoading.value = true
      useApi(withTrailingSlash(joinURL(endpoint, route.params.id))).then(
        (data) => {
          fields.value = data
          isGetDefaultLoading.value = false
          if (!isGetEditLoading.value) {
            store.isLoading = false
          }
          setModalLoadingFalse()
          // if (isModal && store.isModalFormLoading.hasOwnProperty(`${modalId}`)) delete store.isModalFormLoading[modalId]
        }
      )
        .catch((error) => {
          isGetDefaultLoading.value = false
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
      useApi(getDefaultsFetchUrl(), { method: 'GET' }, false, true).then(
        (data) => {
          // TODO: Check with Dipesh sir
          if (data.fields) {
            if (!isEdit) fields.value = Object.assign(fields.value, data.fields)
          }
          formDefaults.value = data
          setTimeout(() => {
            // TODO: Check with Dipesh sir
            isGetDefaultLoading.value = false
            if (!isGetEditLoading.value) {
              store.isLoading = false
              setModalLoadingFalse()
            }
          }, 1000)
        }
      )
    }
  })
  const getDefaultsFetchUrl = () => {
    return joinURL(endpoint, 'create-defaults/')
  }

  const processErrors = (responseData) => {
    // let dct = {}
    const dct = Object.fromEntries(
      Object.entries(responseData).map(([k, v]) => {
        let val = v
        if (Array.isArray(val)) {
          if (typeof val[0] === 'object') {
          } else val = val.join(' ')
        }
        return [k, val]
      })
    )
    errors.value = dct
  }

  const removeLastUrlSegment = (url) => {
    const newParts = withoutTrailingSlash(url).split('/').slice(0, -1)
    return withTrailingSlash(joinURL('/', ...newParts))
  }

  const submitForm = async () => {
    loading.value = true
    errors.value = {}
    let postEndpoint
    if (isEdit.value) {
      postEndpoint = withTrailingSlash(joinURL(endpoint, route.params.id))
    } else {
      postEndpoint = endpoint
    }
    const originalStatus = fields.value.status
    await useApi(postEndpoint, {
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
          context.emit('modalSignal', data)
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
      })
      .catch((data) => {
        let message
        if (data.status == 400) {
          message = 'Please fill out the form correctly.'
          if (data.data?.detail) {
            message = `${data.data.detail}`
          }
          processErrors(data.response._data)
        }
        if (data.status == 404) {
          if (data.data?.detail) {
            message = `Not found - ${data.data.detail}`
          } else {
            message = 'Not found!'
          }
        } else if (data.status == 500) {
          message = 'Server Error! Please contact us with the problem.'
        } else if (data.status === 422) {
          $q.dialog({
            title: `<span class="text-orange">${humanizeWord(data.data?.code)}!</span>`,
            message:
              `<span class="text-grey-8">Reason: ${data.data.detail}` +
              '<div class="text-body1 text-weight-medium text-grey-8 q-mt-md">Are you sure you want to Continue?</div>',
            cancel: true,
            html: true,
          }).onOk(() => {
            useApi(postEndpoint + `?${data.data?.code}=true`, {
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
                  context.emit('modalSignal', data)
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
          })
        }
        else {
          $q.notify({
            color: 'negative',
            message: message,
            icon: 'report_problem',
          })
        }
        loading.value = false
        throw new Error('Api Error')
      })
  }

  const cancel = () => {
    if (isModal) {
      context.emit('closeModal')
    } else if (window.history.length > 2) {
      router.go(-1)
    } else {
      router.push(removeLastUrlSegment(route.path))
    }
  }

  const cancelForm = () => {
    if (isEdit.value) {
      const cancelEndPoint = withTrailingSlash(
        joinURL(endpoint, route.params.id, 'cancel')
      )
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
    if (isModal && modalFormLoading.hasOwnProperty(`${modalId}`)) {
      modalFormLoading[modalId] = false
    }
  }
  onUnmounted(() => {
    store.isLoading = false
    if (isModal && modalFormLoading.hasOwnProperty(`${modalId}`)) delete modalFormLoading[modalId]
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
