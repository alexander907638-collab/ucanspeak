export default defineNuxtRouteMiddleware(async (to, from) => {
  if (to.fullPath === '/') return navigateTo({ name: 'courses' })

  const authStore = useAuthStore()
  const { user } = storeToRefs(authStore)

  // юзер с истёкшей подпиской: пускаем только в тариф, профиль, логин
  const allowedForExpired = ['tariff', 'profile', 'profile-index', 'login', 'login-school_slug']
  if (
      user.value &&
      user.value.is_subscription_expired &&
      to.name &&
      !allowedForExpired.includes(to.name as string)
  ) {
    return navigateTo({ name: 'tariff' })
  }

  if (to.meta.auth || to.meta.guest) {
    if (to.meta.auth && !authStore.user) {
      return navigateTo({ name: 'courses' })
    } else if (to.meta.guest && authStore.user) {
      return navigateTo({ name: 'courses' })
    }
  }
})
