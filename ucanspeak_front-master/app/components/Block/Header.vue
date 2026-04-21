<script setup lang="ts">
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)


const {$api} = useNuxtApp()
// const links = [
//   {title:'Платформа',to:'/courses'},
//   {title:'О проекте',to:'/about'},
//   {title:'Тарифы',to:'/tariff'},
// ]
const props = defineProps(['is_lesson_header','lesson_title','is_trainer_header'])
const emits = defineEmits(['back_click'])
const links = [
  {title:'Курс для взрослых',to:'/courses/adult_course'},
  {title:'Школьный курс',to:'/courses/school_course'},
  {title:'Тренажер',to:'/courses/trainer'},
]

const headerText = useState('header_text')
const route = useRoute()


</script>

<template>
<header id="top" class="fixed w-full  border-b border-[#EFEFEF] bg-white py-2 lg:py-4 mb-2 lg:mb-6  z-[1000]">

  <div class="container min-h-[40px] lg:h-auto flex items-center justify-between">
    <div class=" flex items-center gap-2">
      <Button v-if="route.path !=='/courses'" @click="$router.back()" outlined severity="secondary" size="small" icon="pi pi-chevron-left"/>

      <div class="flex gap-2 lg:hidden">
        <Button v-if="is_lesson_header" @click="emits('back_click')" outlined severity="secondary" size="small" icon="pi pi-bars"/>
      </div>
     <BlockLogo :clickable="true"/>
    </div>

    <button v-if="headerText" class="hidden lg:block mr-[185px]">
      {{headerText}}
    </button>

    <div v-if="user" class="flex gap-2 items-center">

      <NuxtLink v-if="route.path ==='/courses' && user.last_lesson_url" :to="user.last_lesson_url" class="text-sm font-medium text-[#3333e8] hidden sm:flex items-center gap-3">
        <button class="px-3 py-2 bg-[#F6F6F9] border border-[#E0E0EB] rounded flex items-center gap-2">
          <span>Продолжить</span>
          <svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M1.33333 0.166667C1.20953 0.0738109 1.06231 0.017266 0.908171 0.00336764C0.754037 -0.0105307 0.599077 0.0187669 0.460655 0.0879776C0.322234 0.157188 0.20582 0.263578 0.124458 0.395224C0.0430956 0.526871 0 0.678574 0 0.833334V10.8333C0 10.9881 0.0430956 11.1398 0.124458 11.2714C0.20582 11.4031 0.322234 11.5095 0.460655 11.5787C0.599077 11.6479 0.754037 11.6772 0.908171 11.6633C1.06231 11.6494 1.20953 11.5929 1.33333 11.5L8 6.5C8.1035 6.42238 8.1875 6.32172 8.24535 6.20601C8.30321 6.0903 8.33333 5.9627 8.33333 5.83333C8.33333 5.70396 8.30321 5.57637 8.24535 5.46066C8.1875 5.34494 8.1035 5.24429 8 5.16667L1.33333 0.166667Z" fill="#3333E8"/>
          </svg>
        </button>


      </NuxtLink>
      <NuxtLink  to="/courses/search">
        <button class="p-2 bg-[#F6F6F9] border border-[#E0E0EB] rounded flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7.91667 13.3333C6.40278 13.3333 5.12167 12.8089 4.07333 11.76C3.025 10.7111 2.50056 9.43 2.5 7.91667C2.49944 6.40333 3.02389 5.12222 4.07333 4.07333C5.12278 3.02444 6.40389 2.5 7.91667 2.5C9.42944 2.5 10.7108 3.02444 11.7608 4.07333C12.8108 5.12222 13.335 6.40333 13.3333 7.91667C13.3333 8.52778 13.2361 9.10417 13.0417 9.64583C12.8472 10.1875 12.5833 10.6667 12.25 11.0833L16.9167 15.75C17.0694 15.9028 17.1458 16.0972 17.1458 16.3333C17.1458 16.5694 17.0694 16.7639 16.9167 16.9167C16.7639 17.0694 16.5694 17.1458 16.3333 17.1458C16.0972 17.1458 15.9028 17.0694 15.75 16.9167L11.0833 12.25C10.6667 12.5833 10.1875 12.8472 9.64583 13.0417C9.10417 13.2361 8.52778 13.3333 7.91667 13.3333ZM7.91667 11.6667C8.95833 11.6667 9.84389 11.3022 10.5733 10.5733C11.3028 9.84444 11.6672 8.95889 11.6667 7.91667C11.6661 6.87444 11.3017 5.98917 10.5733 5.26083C9.845 4.5325 8.95944 4.16778 7.91667 4.16667C6.87389 4.16556 5.98861 4.53028 5.26083 5.26083C4.53306 5.99139 4.16833 6.87667 4.16667 7.91667C4.165 8.95667 4.52972 9.84222 5.26083 10.5733C5.99194 11.3044 6.87722 11.6689 7.91667 11.6667Z" fill="#8F8FA3"/>
          </svg>

        </button>

      </NuxtLink>
      <NuxtLink class="hidden lg:inline-block"   to="/profile">
        <button class="p-2 bg-[#F6F6F9] border border-[#E0E0EB] rounded flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16.6667 17.5V15.8333C16.6667 14.9493 16.3155 14.1014 15.6904 13.4763C15.0653 12.8512 14.2174 12.5 13.3334 12.5H6.66671C5.78265 12.5 4.93481 12.8512 4.30968 13.4763C3.68456 14.1014 3.33337 14.9493 3.33337 15.8333V17.5" stroke="#8F8FA3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.99996 9.16667C11.8409 9.16667 13.3333 7.67428 13.3333 5.83333C13.3333 3.99238 11.8409 2.5 9.99996 2.5C8.15901 2.5 6.66663 3.99238 6.66663 5.83333C6.66663 7.67428 8.15901 9.16667 9.99996 9.16667Z" stroke="#8F8FA3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>

        </button>

      </NuxtLink>

    </div>
    <div v-else>
      <NuxtLink class="hidden lg:inline-block" to="/login">
        <Button size="small" label="Вход / Регистрация"/>
      </NuxtLink>
    </div>

  </div>
  <div class="block lg:hidden container mt-2" v-if="is_lesson_header">
    {{lesson_title}}
  </div>
  <div class="block lg:hidden container mt-2" v-if="is_trainer_header">
    {{lesson_title}}
  </div>
</header>
</template>