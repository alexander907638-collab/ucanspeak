<script setup lang="ts">
const emits = defineEmits(['change_form'])
import { useToast } from 'primevue/usetoast';
const toast = useToast()
const {$api} = useNuxtApp()
const loading = ref(false)
defineProps(['school_auth'])

const form_data = ref({
  login: '',
  password: '',
})

const max_sessions_dialog_visible = ref(false)
const max_sessions_message = ref('')
const force_loading = ref(false)

watch(
    () => form_data.value.login,
    (newEmail) => {
      form_data.value.login = newEmail.toLowerCase()
    }
)

const setAuthCookieAndRedirect = (token: string) => {
  const authCookie = useCookie('auth_token', {
    maxAge: 60 * 60 * 24 * 7,
  })
  authCookie.value = token
  window.location.href = '/courses'
}

const login = async () => {
  loading.value = true
  try {
    const response = await $api.auth.login(form_data.value)
    setAuthCookieAndRedirect(response.auth_token)
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Получение данных пользователя...', life: 3000 })
  } catch (error: any) {
    const data = error?.data
    if (data?.max_sessions_reached === true) {
      max_sessions_message.value = data.detail || 'Превышен лимит одновременных сессий'
      max_sessions_dialog_visible.value = true
    } else if (data?.detail) {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: data.detail, life: 3000 })
    } else {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось войти', life: 3000 })
    }
  } finally {
    loading.value = false
  }
}

const forceLogin = async () => {
  force_loading.value = true
  try {
    const response = await $api.auth.force_login(form_data.value)
    max_sessions_dialog_visible.value = false
    setAuthCookieAndRedirect(response.auth_token)
  } catch (error: any) {
    const data = error?.data
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: data?.detail || 'Не удалось войти',
      life: 3000
    })
  } finally {
    force_loading.value = false
  }
}
</script>

<template>
  <CardBase padding="none" extra-class="w-full px-3 lg:px-[240px]">
  <div class="flex flex-col items-center justify-center py-4 md:py-10 md:p-[60px] w-full">
    <BlockLogo class="mb-4" v-if="school_auth"/>
    <div class="space-y-3 w-full mb-8">
      <TypingText28 v-if="!school_auth" text="Авторизация"/>

      <UIInput fluid
               placeholder="Введите ваш логин"
               label="Логин"
               id="login"
               v-model="form_data.login"/>
      <UIInput fluid
               placeholder="Введите пароль"
               type="password"
               label="Пароль"
               id="password"
               v-model="form_data.password"/>
    </div>
    <Button fluid
            class="mb-4"
            @click="login"
            :loading="loading"
            label="Войти" />
    <div class="text-center mb-6 w-full">
      <NuxtLink to="/forgot-password" class="text-sm text-[#7575F0] hover:underline">
        Восстановить пароль
      </NuxtLink>
    </div>
    <p v-if="!school_auth">
      У вас нет аккаунта?
      <UILink label="Зарегистрируйтесь"
              link="#"
              @click.prevent="emits('change_form','register')"/>
      на нашей платформе и получите 3 дня пробного доступа ко всем урокам и разделам!
    </p>
  </div>
</CardBase>

<Dialog
    v-model:visible="max_sessions_dialog_visible"
    modal
    header="Превышен лимит сессий"
    :style="{ width: '420px' }"
>
  <p class="mb-4">{{ max_sessions_message }}</p>
  <p class="text-sm text-gray-500 mb-2">
    Если нажмёте «Выйти отовсюду и войти» — все ваши активные сессии на других устройствах будут завершены, и вы войдёте на этом устройстве.
  </p>
  <template #footer>
    <Button
        label="Отмена"
        severity="secondary"
        text
        @click="max_sessions_dialog_visible = false"
    />
    <Button
        label="Выйти отовсюду и войти"
        severity="danger"
        :loading="force_loading"
        @click="forceLogin"
    />
  </template>
</Dialog>
</template>