import { useLoginStore } from '/src/stores/login-info.js'
const loginStore = useLoginStore()
const permissionsArray = loginStore.userInfo.roles

const checkPermissions = (permissions: string) => {
  return permissionsArray.some((item: string) => item === permissions)
}

export default checkPermissions
