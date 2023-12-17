// import { api } from 'boot/ofetch'
import { withTrailingSlash, withoutTrailingSlash, joinURL } from 'ufo'
import { getCurrentInstance } from 'vue'
import useApi from './useApi'

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

  const today = new Date().toISOString().substring(0, 10)

  onMounted(() => {
    // added is modal check
    isEdit.value = !!route.params.id && !isModal
    id.value = route.params.id
    if (isEdit.value) {
      useApi(withTrailingSlash(joinURL(endpoint, route.params.id))).then(
        (data) => {
          fields.value = data
        }
      )
      // .catch((error) => {
      //   if (error.status === 404) {
      //     // router.push('/')
      //     $q.notify({
      //       color: 'negative',
      //       message: 'Not Found!',
      //       icon: 'report_problem',
      //     })
      //   }
      // })
    }
    if (config.getDefaults) {
      useApi(getDefaultsFetchUrl(), { method: 'GET' }, false, true).then(
        (data) => {
          // TODO: Check with Dipesh sir
          if (data.fields) {
            if (!isEdit) fields.value = Object.assign(fields.value, data.fields)
          }
          formDefaults.value = data
          // TODO: Check with Dipesh sir
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
            debugger
            // if (config.successRoute === ) {

            // }
            router.push(config.successRoute)
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
        }
        $q.notify({
          color: 'negative',
          message: message,
          icon: 'report_problem',
        })
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
    loading
  }
}
