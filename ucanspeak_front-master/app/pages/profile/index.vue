<script setup lang="ts">
import { useToast } from 'primevue/usetoast';
import { useClipboard } from '@vueuse/core'
const {$api} = useNuxtApp()
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const selectedFile = ref(null)
const selectedLogoFile = ref(null)
const fileInput = ref(null)
const fileInput1 = ref(null)
const avatarPreview = ref(null)
const schoolLogoPreview = ref(null)
const toast = useToast()
const config = useRuntimeConfig();

const { text, copy, copied} = useClipboard()

const user_data = ref({
  email: user.value.email,
  phone: user.value.phone || null,
  full_name: user.value.full_name || null,
  is_school: user.value.is_school || null,
  time_zone: { "name": "(GMT +03:00) Europe/Moscow", "code": "Europe/Moscow" },
  password: '',
  password1: '',
})

const avatarLabel = computed(() => {
  if (user.value?.full_name) {
    const names = user.value.full_name.split(' ')
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`
    }
    return user.value.full_name[0]
  }
  return 'U'
})

const onFileSelected = (event) => {
  const file = event.target.files[0]
  if (!file) return
  selectedFile.value = file

  // Предпросмотр
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  user_data.value.avatar = selectedFile.value

}
const onSchoolLogoPreviewSelected = (event) => {
  const file = event.target.files[0]
  if (!file) return
  selectedLogoFile.value = file

  // Предпросмотр
  const reader = new FileReader()
  reader.onload = (e) => {
    schoolLogoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  user_data.value.logo = selectedLogoFile.value

}

const { send, pending, errors } = useForm({
  apiFn: $api.auth.update,
  formData: user_data.value,
  asFormData: true,
  onSuccess: async ()=>{
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Профиль обновлен',
      life: 2000
    })
    await $api.auth.me()
  }
})
useSeoMeta({
  title: `Профиль `,
})
</script>

<template>
  <div class="space-y-4 pb-10">
<CardBase padding="md">
  <TypingText28 text="Ваш профиль" class="mb-6"/>
  <TypingText18 text="Фото профиля" class="mb-3"/>
  <div class="flex items-center gap-10 mb-6">
    <Avatar
        :image="avatarPreview || user?.avatar"
        :label="avatarPreview || user?.avatar ? null : avatarLabel"
        size="xlarge"
        shape="circle"
        class="w-20 h-20 text-lg"
    />

      <Button
          label="Выбрать файл"
          icon="pi pi-image"
          size="small"
          @click="fileInput?.click()"
          />

    <input
        type="file"
        ref="fileInput"
        accept="image/*"
        @change="onFileSelected"
        class="hidden"
    />


  </div>
  <div class="space-y-2 mb-3">
    <TypingText18 text="Личные данные" />
    <UIInput fluid
             placeholder="ФИО"
             label="ФИО"
             id="full_name"
             v-model="user_data.full_name"/>

    <UIInput fluid
             placeholder="Телефон"
             label="Телефон"
             id="phone"
             v-model="user_data.phone"/>

  </div>
  <div v-if="errors" class="text-red-500">
    {{errors}}
  </div>



</CardBase>

  <CardBase v-if="!user.is_pupil" padding="md">
    <TypingText28 text="Аккаунт" class="mb-6"/>
    <div class="space-y-3">
      <TypingText18 :text="`Тип аккаунта: ${user.is_school ? 'Школа' : 'Ученик'}`" />
      <template v-if="user.is_school">
        <div class="flex items-center gap-10 mb-6">
          <img class="w-[137px] h-auto object-contain" :src="schoolLogoPreview || user?.school?.image"/>

          <Button
              label="Выбрать логотип школы"
              icon="pi pi-image"
              size="small"
              @click="fileInput1?.click()"
          />

          <input
              type="file"
              ref="fileInput1"
              accept="image/*"
              @change="onSchoolLogoPreviewSelected"
              class="hidden"
          />


        </div>
        <div class="flex flex-wrap items-center justify-between">
          <TypingText18  :text="`Ссылка входа: ${config.public.apiUrl}/login/${user.school.slug}`" />
          <Button size="small" severity="secondary" @click="copy(`${config.public.apiUrl}/login/${user.school.slug}`)" outlined
                  :label="copied ? 'Скопировано' : 'Скопировать'"/>
        </div>
      </template>



      <div class="flex flex-wrap justify-between">
        <div class="space-y-3">
          <TypingText18 :text="`Дата окончания подписки: ${new Date(user.subscription_expire).toLocaleDateString()}`" />
        <TypingText18 :text="`Число одновременных устройств: ${user.max_logins}`" />
      </div>
        <nuxt-link to="/tariff">
          <Button size="small" severity="secondary" outlined label="Продлить"/>
        </nuxt-link>

      </div>


      <TypingText18 text="Email" />
      <UIInput fluid
               placeholder="Адрес почты "
               label="Email"
               id="email"
               v-model="user_data.email"/>
      <TypingText18 text="Пароль" />
      <UIInput fluid
               placeholder="Новый пароль"
               label="Новый пароль"
               id="password"
               v-model="user_data.password"/>
      <UIInput fluid
               placeholder="Повторите пароль"
               label="Повторите пароль"
               id="password1"
               v-model="user_data.password1"/>

      <div class="flex flex-wrap justify-between">
        <div class="">
          <TypingText18 text="Выйти из аккаунта" />
          <p>Выйти</p>
        </div>
        <Button size="small" @click="$api.auth.logout(false)" severity="danger" outlined label="Выйти"/>
      </div>

      <div class="flex flex-wrap justify-between">
        <div class="">
          <TypingText18 text="Выйти со всех устройств" />
          <p>Завершить все сессии</p>
        </div>
        <Button size="small" @click="$api.auth.logout(true)" severity="danger" outlined label="Выйти отовсюду"/>
      </div>
      <div v-if="errors" class="text-red-500">
        {{errors}}
      </div>

      <Button severity="success" @click="send" :loading="pending" label="Обновить"/>
    </div>

  </CardBase>
  </div>
</template>

<style scoped>

</style>