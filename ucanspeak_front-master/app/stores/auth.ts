import type {User} from "~/repository/auth/types";

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const { $api } = useNuxtApp()

  const setUser = (userData: User) => {
    user.value = userData
  }

  const fetchUser = async () => {

    try {
      await $api.auth.me()
    } catch (e) {
      user.value = null
    }
  }

  return {
    user,
    fetchUser,
    setUser,
  }
})