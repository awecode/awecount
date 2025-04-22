const checkPermissions = (permissions: string) => {
  const { hasPermission } = useAuth()
  return hasPermission(permissions)
}

export default checkPermissions
