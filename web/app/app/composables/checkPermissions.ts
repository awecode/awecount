const checkPermissions = (permissions: string) => {
  console.log('checkPermissions', permissions)
  const { hasPermission } = useAuth()
  return hasPermission(permissions)
}

export default checkPermissions
