import ToastService from 'primevue/toastservice';
export default defineNuxtPlugin(async (nuxtApp):Promise<any> => {
  nuxtApp.vueApp.use(ToastService)
  const {$api} = useNuxtApp()
  const authCookie = useCookie('auth_token')
  if (authCookie.value) {
    await $api.auth.me()

  }
})
