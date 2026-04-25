<script setup lang="ts">
definePageMeta({
  guest: true,
  layout: 'auth'
})

const email = ref('')
const sent = ref(false)
const loading = ref(false)

const handleSubmit = () => {
  // Заглушка: бэк-эндпоинт восстановления пароля будет реализован
  // отдельной задачей после настройки SMTP. Сейчас кнопка ничего не делает.
  // Намеренно НЕ показываем сообщение пользователю.
}
</script>

<template>
  <div class="pt-20 md:pt-0 md:h-[100vh] flex flex-col items-start justify-center">
    <CardBase padding="none" extra-class="w-full px-3 lg:px-[240px]">
      <div class="flex flex-col items-center justify-center py-4 md:py-10 md:p-[60px] w-full">

        <TypingText28 text="Восстановить пароль" class="mb-2"/>
        <p class="text-sm text-gray-500 text-center mb-6 max-w-md">
          Введите email, на который мы пришлём новый пароль.
        </p>

        <div class="space-y-3 w-full mb-6">
          <UIInput fluid
                   placeholder="your@mail.ru"
                   label="Email"
                   id="email"
                   v-model="email"/>
        </div>

        <Button fluid
                class="mb-4"
                @click="handleSubmit"
                :loading="loading"
                label="Отправить" />

        <p class="text-xs text-gray-500 text-center mb-6 max-w-md">
          Если вы ученик школы и у вас нет email — обратитесь к администратору вашей школы для смены пароля.
        </p>

        <div class="text-center w-full">
          <NuxtLink to="/login" class="text-sm text-[#7575F0] hover:underline">
            Вернуться ко входу
          </NuxtLink>
        </div>

      </div>
    </CardBase>
  </div>
</template>
