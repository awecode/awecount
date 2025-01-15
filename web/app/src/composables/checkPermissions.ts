import { useAuthStore } from 'src/stores/auth'

const checkPermissions = (permissions: string) => {
  const { hasPermission } = useAuthStore()
  return hasPermission(permissions)
}

export default checkPermissions
