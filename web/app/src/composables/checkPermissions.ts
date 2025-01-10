import { useLoginStore } from '/src/stores/login-info.js'
const loginStore = useLoginStore()

const checkPermissions = (permissions: string) => {
  const permissionsArray = loginStore.userInfo?.roles
  return permissionsArray?.some((item: string) => item === permissions)
}

export default checkPermissions
