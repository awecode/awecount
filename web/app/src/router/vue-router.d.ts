import 'vue-router'

export {} // This is To ensure it is treated as a module and prevent type reset

declare module 'vue-router' {
  interface RouteMeta {
    auth?: {
      protected?: boolean
      roles?: Array<'owner' | 'admin' | 'member'>
      permissions?: string[]
      loginRoute?: string
      redirectIfLoggedIn?: string | false
      redirectIfNotAllowed?: string | false
    }
  }
}
