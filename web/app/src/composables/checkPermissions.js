import { useLoginStore } from '/src/stores/login-info.js'
const loginStore = useLoginStore()
const permissionsArray = loginStore.userInfo.roles

const checkPermissions = (permissions = []) => {
  return permissionsArray.some((item) => item === permissions)
}

export default checkPermissions
