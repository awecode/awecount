import { api } from 'boot/ofetch'
import { useLoginStore } from 'src/stores/login-info'

const useGetDataAuth = async (endpoint, body, omitToken) => {
  const loginStore = useLoginStore()
  const router = useRouter()
  const options = {}
  if (omitToken !== true) {
    options.headers = {
      Authorization: `${loginStore.token ? `Token ${loginStore.token}` : ''}`,
      // mode: "no-cors", // no-cors, *cors, same-origin
    }
  }
  if (body?.method && body.method !== 'GET') {
    options.method = body.method
  }
  if (body?.body && body.method !== 'GET') {
    options.body = body.body
  }
  return api(endpoint, options).catch((error) => {
    if (error.status == 401 && omitToken !== true) {
      loginStore.reset()
      router.push('/login')
    }
  })
}

export default useGetDataAuth
