<script setup lang="ts">

definePageMeta({
  guest: true,
  layout: 'auth'
})

const init_form = useRoute().query.form


const current_form = ref('login')
if (init_form) {
  current_form.value = init_form
}
const changeFormHandler = (form:string) => {
  current_form.value = form
}
</script>

<template>
  <div class=" pt-20 md:pt-0 md:h-[100vh] flex flex-col items-start justify-center">

    <FormLogin v-if="current_form==='login'" @change_form="changeFormHandler"/>
    <FormRegister v-if="current_form==='register'" @change_form="changeFormHandler"/>
  </div>
</template>
