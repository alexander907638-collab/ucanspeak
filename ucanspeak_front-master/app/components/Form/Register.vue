<script setup lang="ts">
const emits = defineEmits(['change_form'])
import { useToast } from 'primevue/usetoast';
const toast = useToast()
const {$api} = useNuxtApp()
const loading = ref(false)
const form_data = ref({
  full_name:'',//null,
  email:'',
  is_school:false,
  password:'',
  password1:'',
})

watch(
    () => form_data.value.email,
    (newEmail) => {
      form_data.value.email = newEmail.toLowerCase()
    }
)
const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
const isValidPasswords = (): boolean => {
  return !! form_data.value.password &&
      form_data.value.password ===  form_data.value.password1
}

const send = async () => {
  if (!isValidEmail(form_data.value.email)) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Введите корректный email', life: 3000 });
    return;
  }
  if (!isValidPasswords()) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Пароли не совпадают', life: 3000 });
    return;
  }

  loading.value = true
  try{
    const response = await $api.auth.register(form_data.value)
    toast.add({ severity: 'success',summary:'Успешно', detail: 'Аккаунт создан', life: 3000 });
    emits('change_form','login')


  }catch(error){
    const responseErrors = error.data

    if (responseErrors && typeof responseErrors === 'object') {
      const messages: string[] = []

      for (const key in responseErrors) {
        const fieldErrors = responseErrors[key]
        if (Array.isArray(fieldErrors)) {
          for (const msg of fieldErrors) {
            console.log(fieldErrors)

            messages.push(msg)
          }
        }
      }

      toast.add({
        severity: 'error',
        summary: 'Ошибка',
        detail: messages.join('\n'),
        life: 6000,
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Ошибка',
        detail: 'Ошибка',
        life: 3000,
      })
    }
  }finally {
    loading.value = false
  }
}

</script>

<template>
  <CardBase padding="none" extra-class="w-full px-3 lg:px-[240px]">
    <div class="flex flex-col items-center justify-center py-4 md:py-10 md:p-[60px] w-full">
    <div class="space-y-3 w-full mb-8">
      <TypingText28 text="Регистрация аккаунта"/>
      <UIInput fluid placeholder="Ваше ФИО" label="ФИО" id="full_name" v-model="form_data.full_name"/>
      <UIInput fluid placeholder="Введите адрес почты" label="Email" id="email" v-model="form_data.email"/>
      <UIInput fluid placeholder="Не менее 8 символов" label="Пароль" id="password" type="password" v-model="form_data.password"/>
      <UIInput fluid placeholder="Не менее 8 символов" label="Повторите пароль" type="password" id="password1" v-model="form_data.password1"/>
      <div @click="form_data.is_school = !form_data.is_school" class="p-inputtext py-4 !bg-white flex items-center justify-between cursor-pointer">
        <p class="select-none">Аккаунт для школы</p>
        <ToggleSwitch v-model="form_data.is_school" />
      </div>
    </div>
    <Button fluid @click="send" :loading="loading" label="Зарегистрироваться" class="mb-3"/>
    <p class="text-sm mb-3">Аккаунт для бизнеса имеет свои отличия - большее число одновременных сессий для множества учеников и свою тарификацию, а так же возможность контроля сессий учеников.</p>
    <div class="flex items-center justify-center gap-2">
      Уже есть аккаунт?
      <UILink label="Войти" @click="emits('change_form','login')"/>
    </div>
  </div>
</CardBase>
</template>

<style scoped>

</style>