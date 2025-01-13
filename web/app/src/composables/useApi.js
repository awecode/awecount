import { api } from 'boot/ofetch'
import { useLoginStore } from 'src/stores/login-info'
import { useRouter } from 'vue-router'

const useApi = async (endpoint, body, omitToken, permissionRedirect = false) => {
  const loginStore = useLoginStore()
  const router = useRouter()
  const options = {}
  if (omitToken !== true) {
    options.headers = {
      Authorization: `${loginStore.token ? 'Token ' + loginStore.token : ''}`,
      // mode: "no-cors", // no-cors, *cors, same-origin
    }
  }
  if (body?.method && body.method !== 'GET') {
    options.method = body.method
  }
  if (body?.body && body.method !== 'GET') {
    options.body = body.body
  }
  return new Promise((resolve, reject) => {
    api(endpoint, options)
      .then((data) => resolve(data))
      .catch((error) => {
        if (error.status == 401 && omitToken !== true) {
          loginStore.reset()
          router.push('/login')
        }
        if (permissionRedirect && error.status == 403 && error.data.detail === "You don't have the permission to perform this action!") {
          router.push('/no-permission')
        }
        return reject(error)
      })
  })
}
export default useApi
