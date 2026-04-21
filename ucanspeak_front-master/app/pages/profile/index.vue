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

const show_password_form = ref(false)

// TODO: нужны бек-эндпоинты active_sessions/terminate_session (S1.9)
const sessions_data = ref({
  total_active: 1,
  max_logins: user.value?.max_logins || 0,
  sessions: [] as any[]
})

const sessions_expanded = ref(false)

const visible_sessions = computed(() => {
  const list = sessions_data.value?.sessions || []
  return sessions_expanded.value ? list : list.slice(0, 4)
})

const hidden_sessions_count = computed(() => {
  const total = sessions_data.value?.sessions?.length || 0
  return Math.max(0, total - 4)
})

async function terminate_session(session_id: number) {
  // TODO: implement when backend ready
  toast.add({ severity: 'info', summary: 'Скоро', detail: 'Функция будет доступна в ближайшем обновлении', life: 2000 })
}

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

function getInitials(name: string): string {
  if (!name) return '?'
  return name.split(/\s+/).map(p => p.charAt(0).toUpperCase()).slice(0, 2).join('')
}

function formatDate(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
}

function formatSessionTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 2) return 'сейчас'
  if (diffMin < 60) return `${diffMin} мин назад`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr} ${pluralize(diffHr, 'ча��', 'часа', 'часов')} назад`
  const diffDay = Math.floor(diffHr / 24)
  if (diffDay < 7) return `${diffDay} ${pluralize(diffDay, 'день', 'дня', 'дней')} назад`
  return formatDate(iso)
}

function pluralize(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10, mod100 = n % 100
  if (mod100 >= 11 && mod100 <= 14) return many
  if (mod10 === 1) return one
  if (mod10 >= 2 && mod10 <= 4) return few
  return many
}

const onFileSelected = (event) => {
  const file = event.target.files[0]
  if (!file) return
  selectedFile.value = file

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
  <div>
    <BlockBaseBreadcrumbs :items="[{ label: 'Главная', to: '/' }, { label: 'Профиль' }]" />
    <TypingText48 text="Профиль" class="mb-6" />

    <div class="space-y-3">

      <!-- 1. CTA подписка -->
      <CardBase v-if="user && !user.is_pupil" padding="sm" class="relative overflow-hidden">
        <div class="absolute inset-0 -z-10"
             style="background: linear-gradient(135deg, #7575F0 0%, #9F7AEA 100%);"></div>
        <div class="flex items-center justify-between gap-4 flex-wrap text-white">
          <div>
            <p class="text-xs opacity-80 uppercase tracking-wider mb-1">Ваша подписка</p>
            <p class="text-lg font-semibold mb-1">
              {{ user?.is_school ? 'Школа' : 'Ученик' }}
              <span v-if="user?.subscription_expire" class="font-normal opacity-90">
                · до {{ formatDate(user.subscription_expire) }}
              </span>
            </p>
            <p class="text-sm opacity-80" v-if="user?.max_logins">
              Активна · до {{ user.max_logins }} {{ pluralize(user.max_logins, 'устройство', 'устройства', 'устройств') }} одновременно
            </p>
          </div>
          <NuxtLink to="/tariff">
            <Button label="Продлить" class="!bg-white !text-[#7575F0] !border-white" />
          </NuxtLink>
        </div>
      </CardBase>

      <!-- 2. Личные данные -->
      <CardBase padding="sm">
        <h2 class="text-base font-semibold mb-4">Личные данные</h2>

        <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div class="md:col-span-3 flex flex-col items-center gap-2">
            <Avatar
                :image="avatarPreview || user?.avatar"
                :label="avatarPreview || user?.avatar ? null : avatarLabel"
                size="xlarge"
                shape="circle"
                class="w-20 h-20 text-lg"
            />
            <label class="text-xs text-[#7575F0] hover:underline cursor-pointer">
              Загрузить фото
              <input type="file" class="hidden" accept="image/*" @change="onFileSelected">
            </label>
          </div>

          <div class="md:col-span-9 space-y-3">
            <UIInput fluid
                     placeholder="ФИО"
                     label="ФИО"
                     id="full_name"
                     v-model="user_data.full_name"/>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <UIInput fluid
                       placeholder="Email"
                       label="Email"
                       id="email"
                       v-model="user_data.email"/>
              <UIInput fluid
                       placeholder="Телефон"
                       label="Телефон"
                       id="phone"
                       v-model="user_data.phone"/>
            </div>
          </div>
        </div>

        <!-- Школа: логотип и ссылка -->
        <template v-if="user?.is_school">
          <div class="flex items-center gap-10 mt-4 mb-4">
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
            <p class="text-sm text-gray-600">Ссылка входа: {{ config.public.apiUrl }}/login/{{ user.school.slug }}</p>
            <Button size="small" severity="secondary" @click="copy(`${config.public.apiUrl}/login/${user.school.slug}`)" outlined
                    :label="copied ? 'Скопировано' : 'Скопировать'"/>
          </div>
        </template>

        <div v-if="errors" class="text-red-500 mt-3">{{ errors }}</div>

        <div class="mt-4 flex justify-end">
          <Button label="Сохранить изменения" severity="success" @click="send" :loading="pending" />
        </div>
      </CardBase>

      <!-- 3. Пароль -->
      <CardBase padding="sm">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 class="text-base font-semibold">Пароль</h2>
            <p class="text-sm text-gray-500 mt-0.5">Для безопасности меняйте пароль раз в несколько месяцев</p>
          </div>
          <Button
              :label="show_password_form ? 'Свернуть' : 'Изменить пароль'"
              severity="secondary"
              outlined
              @click="show_password_form = !show_password_form"
          />
        </div>

        <div v-if="show_password_form" class="mt-4 pt-4 border-t border-gray-100 space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <UIInput fluid
                     placeholder="Новый пароль"
                     label="Новый пароль"
                     id="password"
                     type="password"
                     v-model="user_data.password"/>
            <UIInput fluid
                     placeholder="Повторите пароль"
                     label="Повторите пароль"
                     id="password1"
                     type="password"
                     v-model="user_data.password1"/>
          </div>
          <div class="flex justify-end">
            <Button label="Обновить пароль" severity="success" @click="send" :loading="pending" />
          </div>
        </div>
      </CardBase>

      <!-- 4. Сессии -->
      <CardBase padding="sm" v-if="sessions_data && sessions_data.sessions.length > 0">
        <div class="flex items-center justify-between mb-0.5 flex-wrap gap-2">
          <h2 class="text-base font-semibold">Активные сессии</h2>
          <span class="text-sm text-gray-500">
            {{ sessions_data.total_active || 0 }} из {{ sessions_data.max_logins || 0 }} активны
          </span>
        </div>
        <p class="text-sm text-gray-500 mb-3">Устройства где вы сейчас вошли</p>

        <div>
          <div
              v-for="session in visible_sessions"
              :key="session.id"
              class="flex justify-between items-center py-3 border-b border-gray-100 last:border-b-0 flex-wrap gap-2"
          >
            <div>
              <p class="font-medium text-sm">{{ session.user_agent_short || session.user_agent || 'Неизвестное устройство' }}</p>
              <p class="text-xs text-gray-500">
                Последняя активность: {{ formatSessionTime(session.last_used_at) }}
                <span v-if="session.ip_address"> · IP {{ session.ip_address }}</span>
              </p>
            </div>
            <span v-if="session.is_current"
                  class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
              Эта сессия
            </span>
            <button v-else
                    class="text-xs text-red-600 hover:underline cursor-pointer"
                    @click="terminate_session(session.id)">
              Завершить
            </button>
          </div>

          <div v-if="hidden_sessions_count > 0" class="pt-3 text-center">
            <button
                class="text-sm text-[#7575F0] hover:underline cursor-pointer font-medium"
                @click="sessions_expanded = !sessions_expanded"
            >
              {{ sessions_expanded ? 'Свернуть' : `Показать все (${hidden_sessions_count} скрыто)` }}
            </button>
          </div>
        </div>
      </CardBase>

      <!-- 5. Кнопки выхода -->
      <div v-if="user && !user.is_pupil" class="rounded-xl p-4 border space-y-3" style="background: #FFFBFB; border-color: #FECACA;">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <p class="font-medium text-sm">Выйти из аккаунта</p>
            <p class="text-xs text-gray-500">На этом устройстве</p>
          </div>
          <Button label="Выйти" severity="danger" outlined @click="$api.auth.logout(false)" />
        </div>
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <p class="font-medium text-sm">Выйти со всех устройств</p>
            <p class="text-xs text-gray-500">Завершить все активные сессии</p>
          </div>
          <Button label="Выйти везде" severity="danger" outlined @click="$api.auth.logout(true)" />
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>

</style>
