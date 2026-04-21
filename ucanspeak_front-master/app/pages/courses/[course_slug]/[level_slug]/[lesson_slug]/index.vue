<!--lesson_slug-->
<script setup lang="ts">

import { useBreakpoints } from '@vueuse/core'

const breakpoints = useBreakpoints({
  mobile: 0, // optional
  tablet: 640,
  laptop: 1024,
  desktop: 1280,
})


const activeBreakpoint = breakpoints.active()

const is_mobile = computed(()=>{

  return  activeBreakpoint.value === 'mobile' || activeBreakpoint.value === 'tablet'
})
definePageMeta({
  // guest: false,
  // auth:true,
  layout: 'lesson'
})
type ViewMode = "module" | "videos" | "audio" | "trainer" | "table"
const router = useRouter()
const {$api} = useNuxtApp()
const {lesson_slug, level_slug, course_slug}  = useRoute().params
const route = useRoute()
const {m_id} = route.query
const current_module = ref(null)
const {data:lesson,refresh,pending} = useHttpRequest(await useAsyncData(()=>$api.lessons.lesson(lesson_slug)))
const video_tutorial_modal_visible = ref(false)
const loading = ref(false)
const fav_loading = ref(false)
const module = ref(null)
const tutorial_video = ref(null)
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const openedId = ref<number | null>(null)
const opened_dictionary_id = ref<number | null>(null)
const viewMode = ref<ViewMode>("module")
const dictionary_modal_visible = ref(false)
const table_modal_visible = ref(false)
const table = ref(null)
const showMenu = ref(true)
const is_play = ref(false)

const videos = ref([])
const config = useRuntimeConfig();

const dictionary_direction = ref('ruEN')
const isPlaying = ref(false)
const audio = new Audio()

const headerText = useState('header_text')
headerText.value = lesson.value?.title

audio.src = lesson.value.file
const play = () => {
  if (isPlaying.value) {
    audio.pause()
    isPlaying.value = false
  } else {

    audio.play()
    isPlaying.value = true
  }
}

audio.addEventListener('ended', () => {
  isPlaying.value = false
})

const handleToggleOpen = (id: number) => {
  openedId.value = openedId.value === id ? null : id
}
const handleToggleDictionaryOpen = (id: number) => {
  opened_dictionary_id.value = opened_dictionary_id.value === id ? null : id
}

const fetch_module = async (id) => {
  is_play.value = false
  current_module.value= id
  if (is_mobile.value) showMenu.value = false
  viewMode.value = "module"
  loading.value = true
  await router.replace({
    query: {
      ...route.query, // сохраняем остальные query параметры
      m_id: id
    }
  })

  await nextTick()
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
  try{
    module.value = await $api.lessons.module(id)
  }catch(error){}
  finally{
    loading.value = false

  }
}

onMounted(async () => {
  const id = m_id ? Number(m_id) : lesson.value.modules[0].id
  await fetch_module(id)
  showMenu.value = true
})

const videoSelected = (video_src) =>{
  tutorial_video.value = video_src
  video_tutorial_modal_visible.value = true

}

const toggleBlockDone = async (id,index) => {

  loading.value = false
  module.value.blocks.splice(index, 1, {
    ...module.value.blocks[index],
    is_done: !module.value.blocks[index].is_done
  })
  await $api.lessons.toggle_block({id})
  await refresh()
  loading.value = false
}

const handleToggleFav = async (id) => {
  fav_loading.value = true
  await $api.lessons.toggle_dictionary_favorite({
    id: id
  })
  await refresh()
  fav_loading.value = false
}
const handlePharaseToggleFav = async (id) => {
  fav_loading.value = true
  await $api.lessons.toggle_phrase_favorite({
    id: id
  })
  fav_loading.value = false
}

const fetchTable = async () => {
  is_play.value = false
  if (lesson.value.table_file) {
    table.value = lesson.value.table_file
    table_modal_visible.value = true
    return
  }
  if (!table.value) {
    const resp =  await $api.lessons.lesson_table(lesson_slug)
    table.value = resp.table
  }
  table_modal_visible.value = true
  //viewMode.value = "table"
}

const fetchVideos = async () => {
  is_play.value = false
  if (videos.value.length === 0) {
    videos.value = await $api.lessons.lesson_videos(lesson_slug)
  }
  if (is_mobile.value) showMenu.value = false
  viewMode.value = "videos"
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

useSeoMeta({
  title: `${lesson.value.title} `,
})
const toggleMenu = async ()=>{
  is_play.value = false
  showMenu.value = !showMenu.value
  await nextTick()
  if (showMenu.value) {
    const el = document.getElementById('top')
    el?.scrollIntoView({ behavior: 'auto' })
  }

}

const toggleView = async (mode:ViewMode)=>{
  console.log(mode)
  if (is_mobile.value) showMenu.value = false


  viewMode.value = mode
  await nextTick()
  mode === 'audio'? is_play.value = true : is_play.value = false
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })

}

const handleBackClick = () => {
    showMenu.value = true
}

const showContent =  computed(()=>{
  console.log(is_mobile.value)
  if (!is_mobile.value) return true
  return !showMenu.value
})

watch(is_mobile, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    // Перешли с мобилки на десктоп — показываем меню
    showMenu.value = true
  }
  if (!oldVal && newVal) {
    // Перешли с десктопа на мобилку — показываем меню (начальное состояние)
    showMenu.value = true
  }
})

</script>


<template>
  <BlockHeader :is_lesson_header="true" :lesson_title="lesson.title" @back_click="handleBackClick"/>

  <div class="container pb-[60px] lg:pb-10 pt-20 lg:pt-20">
  <BlockBaseBreadcrumbs
      :items="[
    { label: 'Главная', to: '/' },
    { label: 'Курсы', to: '/courses' },
    { label: lesson.course_title, to: `/courses/${course_slug}` },
    { label: lesson.level_title, to: `/courses/${course_slug}/${level_slug}` },
    { label: lesson.title },
  ]"
  />




  <div class="grid grid-cols-12 gap-0 lg:gap-4">
    <div class="col-span-12 lg:col-span-3 ">
      <div class="sticky top-20 ">

        <CardBase  v-if="showMenu" padding="sm" class="mb-4 mt-4 lg:mt-0 h-auto lg:h-[75vh] overflow-x-hidden overflow-y-auto space-y-1 overscroll-contain">
          <p
              v-for="(module, i) in lesson.modules"
              :key="i"
              @click="fetch_module(module.id)"
              class="w-full border cursor-pointer flex items-center justify-between gap-2 p-3 rounded-lg hover:bg-[#F6F6FB] transition-[0.2s] duration-[ease-in-out] ease-[all]"
              :class="{
              'bg-[#F6F6FB]': viewMode === 'module' && current_module === module.id
            }"
          >
            <span> {{ i + 1 }}. {{ module.title }}</span>
            <i v-if="module.is_done" class="text-green-500 pi pi-check-circle"></i>
          </p>
          <div  class="flex items-center gap-3 border rounded-lg px-2 py-1 cursor-pointer  hover:bg-[#F6F6FB]"
                @click="fetchVideos"
                :class="viewMode === 'videos' ? 'bg-[#efeff5]' : 'bg-white'"
          >
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
              <path d="M10 13C10 12.7348 10.1054 12.4804 10.2929 12.2929C10.4804 12.1054 10.7348 12 11 12H29C29.2652 12 29.5196 12.1054 29.7071 12.2929C29.8946 12.4804 30 12.7348 30 13V27C30 27.2652 29.8946 27.5196 29.7071 27.7071C29.5196 27.8946 29.2652 28 29 28H11C10.7348 28 10.4804 27.8946 10.2929 27.7071C10.1054 27.5196 10 27.2652 10 27V13Z" stroke="#3333E8" stroke-width="2" stroke-linejoin="round"/>
              <path d="M26 12V28M14 12V28M27 17H30M27 23H30M10 17H13M10 16V18M12.5 12H15.5M12.5 28H15.5M24.5 12H27.5M24.5 28H27.5M10 23H13M10 22V24M30 22V24M30 16V18" stroke="#3333E8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18.5 17.5L22.5 20L18.5 22.5V17.5Z" stroke="#3333E8" stroke-width="2" stroke-linejoin="round"/>
            </svg>
            <p>Видео</p>
          </div>
          <div v-if="lesson.have_table" class="flex items-center gap-3 border rounded-lg px-2 py-1 cursor-pointer  hover:bg-[#F6F6FB]"
               @click="fetchTable"
               :class="viewMode === 'table' ? 'bg-[#efeff5]' : 'bg-white'"
          >
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
              <path d="M13 12H27C27.5304 12 28.0391 12.2107 28.4142 12.5858C28.7893 12.9609 29 13.4696 29 14V26C29 26.5304 28.7893 27.0391 28.4142 27.4142C28.0391 27.7893 27.5304 28 27 28H13C12.4696 28 11.9609 27.7893 11.5858 27.4142C11.2107 27.0391 11 26.5304 11 26V14C11 13.4696 11.2107 12.9609 11.5858 12.5858C11.9609 12.2107 12.4696 12 13 12ZM13 16V20H19V16H13ZM21 16V20H27V16H21ZM13 22V26H19V22H13ZM21 22V26H27V22H21Z" fill="#3333E8"/>
            </svg>

            <p>Таблица</p>
          </div>
          <div class="flex items-center gap-3 border rounded-lg px-2 py-1 cursor-pointer  hover:bg-[#F6F6FB]" @click="toggleView('trainer')"
               :class="viewMode === 'trainer' ? 'bg-[#efeff5]' : 'bg-white'"
          >
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
              <path d="M20.573 28.6957H25.2174C25.6786 28.6957 26.121 28.5124 26.4471 28.1863C26.7733 27.8601 26.9565 27.4178 26.9565 26.9565V16.5217C26.9572 16.2462 26.9033 15.9732 26.7979 15.7186C26.6926 15.464 26.5378 15.2328 26.3426 15.0383L23.2226 11.9183C23.0281 11.7231 22.7969 11.5683 22.5423 11.4629C22.2877 11.3576 22.0147 11.3037 21.7391 11.3044H14.7826C14.3214 11.3044 13.879 11.4876 13.5529 11.8137C13.2267 12.1399 13.0435 12.5822 13.0435 13.0435V21.1652" stroke="#3333E8" stroke-width="1.73913" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21.74 11.3043V15.6522C21.74 15.8828 21.8316 16.104 21.9947 16.267C22.1578 16.4301 22.3789 16.5217 22.6096 16.5217H26.9574M18.5904 20.5409C18.9367 20.1949 19.4062 20.0007 19.8957 20.001C20.3852 20.0012 20.8545 20.1959 21.2004 20.5422C21.5464 20.8885 21.7406 21.358 21.7403 21.8474C21.7401 22.3369 21.5454 22.8062 21.1991 23.1522L16.8357 27.5104C16.629 27.7172 16.3736 27.8685 16.093 27.9504L13.6 28.6783C13.5252 28.7001 13.4459 28.7014 13.3704 28.682C13.2949 28.6627 13.2259 28.6234 13.1708 28.5683C13.1157 28.5132 13.0764 28.4443 13.0571 28.3688C13.0377 28.2933 13.039 28.214 13.0609 28.1391L13.7878 25.6443C13.8699 25.3641 14.0212 25.109 14.2278 24.9026L18.5904 20.5409Z" stroke="#3333E8" stroke-width="1.73913" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p>Орфография</p>
          </div>
          <div class="flex items-center gap-3 border rounded-lg px-2 py-1 cursor-pointer  hover:bg-[#F6F6FB]"
               @click="toggleView('audio')"
               :class="viewMode === 'audio' ? 'bg-[#efeff5]' : 'bg-white'"
          >
            <svg v-if="!isPlaying" width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
              <path fill-rule="evenodd" clip-rule="evenodd" d="M17.8656 13.2C17.7171 13.0886 17.5404 13.0207 17.3554 13.004C17.1705 12.9874 16.9845 13.0225 16.8184 13.1056C16.6523 13.1886 16.5126 13.3163 16.415 13.4743C16.3173 13.6322 16.2656 13.8143 16.2656 14V26C16.2656 26.1857 16.3173 26.3678 16.415 26.5257C16.5126 26.6837 16.6523 26.8114 16.8184 26.8944C16.9845 26.9775 17.1705 27.0126 17.3554 26.996C17.5404 26.9793 17.7171 26.9114 17.8656 26.8L25.8656 20.8C25.9898 20.7069 26.0906 20.5861 26.1601 20.4472C26.2295 20.3084 26.2656 20.1552 26.2656 20C26.2656 19.8448 26.2295 19.6916 26.1601 19.5528C26.0906 19.4139 25.9898 19.2931 25.8656 19.2L17.8656 13.2Z" fill="#3333E8"/>
            </svg>
            <svg v-else width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
              <path d="M14 26.4V13.6C14 13.4409 14.0632 13.2883 14.1757 13.1757C14.2883 13.0632 14.4409 13 14.6 13H17.4C17.5591 13 17.7117 13.0632 17.8243 13.1757C17.9368 13.2883 18 13.4409 18 13.6V26.4C18 26.5591 17.9368 26.7117 17.8243 26.8243C17.7117 26.9368 17.5591 27 17.4 27H14.6C14.4409 27 14.2883 26.9368 14.1757 26.8243C14.0632 26.7117 14 26.5591 14 26.4ZM22 26.4V13.6C22 13.4409 22.0632 13.2883 22.1757 13.1757C22.2883 13.0632 22.4409 13 22.6 13H25.4C25.5591 13 25.7117 13.0632 25.8243 13.1757C25.9368 13.2883 26 13.4409 26 13.6V26.4C26 26.5591 25.9368 26.7117 25.8243 26.8243C25.7117 26.9368 25.5591 27 25.4 27H22.6C22.4409 27 22.2883 26.9368 22.1757 26.8243C22.0632 26.7117 22 26.5591 22 26.4Z" fill="#3333E8" stroke="#3333E8" stroke-width="1.5"/>
            </svg>
            <p>Аудиоурок</p>
          </div>
          <UIEditAdminBtn
            app="lesson"
            model="lesson"
            :id="lesson.id"
            label="Редактировать урок"
            :fluid="true"
            class="block mt-3"
          />
        </CardBase>
      </div>

    </div>

    <div v-if="showContent" class="col-span-12 lg:col-span-6 pt-4 lg:pt-0">
      <template v-if="loading">
        <div class="space-y-3">
          <SkeletonLessonCard />
        </div>
      </template>
      <template v-else>
        <template v-if="viewMode === 'audio'">
          <CardBase padding="sm" class=" bg-[url('/a_bg.png')] relative bg-top bg-no-repeat bg-cover flex flex-col items-center justify-evenly h-[400px]">
            <div class="space-y-4 text-center">
              <TypingText28 text="Аудиоурок"/>
              <p class="text-gray-500">{{lesson.title}}</p>
            </div>
            <div class="block lg:hidden absolute top-4 right-4">
              <Button  @click.stop="handleBackClick" size="small" outlined rounded icon="pi pi-times"/>
            </div>

<!--            <audio class="w-[80%]" controlsList="nodownload" @contextmenu.prevent controls :src="lesson.file"></audio>-->
            <div class="px-0 lg:px-10 w-full">
              <BlockAudioPlayer :play="is_play" :src="lesson.file" />
            </div>

          </CardBase>
        </template>
        <template  v-else-if="viewMode === 'trainer'">
          <CardBase padding="sm" >

            <p class="font-medium mb-2">{{lesson.orthography_description}}</p>
            <div class="space-y-1">
              <CardSpellingTrainer v-for="item in lesson.orthography_items" :item="item" lang="ru"/>
            </div>
          </CardBase>
        </template>
        <template v-else-if="viewMode === 'videos'">
          <CardBase padding="sm">
            <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
              <div class="" v-for="video in videos" :key="video.id">
                {{video.video_number}}
                <BlockVideoWithPreview :use_modal="true" :showPreview = "true" :data="video"/>
                <UIEditAdminBtn
                  app="lesson"
                  model="video"
                  :id="video.id"
                  class="mt-1"
                />
              </div>
            </div>
          </CardBase>
        </template>
        <template v-else>
          <div class="space-y-3 mb-6">
            <CardBase padding="sm" v-for="(block,index) in module?.blocks" :key="block.id">
              <!--              <p class="text-[16px] lg:text-lg font-medium mb-2">{{module.index}}.{{index+1}}</p>-->

              <div class="text-[16px] lg:text-lg font-medium mb-3 !leading-[110%] text-[#202021]"
                   v-html="block.caption === '  None' ? '' : block.caption"></div>

              <div v-if="block.videos.length > 0 && block.videos[0].phrases.length === 0" class="mt-3 ">
                <img @click="videoSelected(block.videos[0].file)" class="cursor-pointer w-[120px] h-[90px] object-contain" src="~assets/images/tutorial_video.png">

              </div>
              <div v-if="block.videos.length > 0 && block.videos[0].phrases.length > 0" class="mt-3">
                <BlockVideoWithPreview :showPreview = "false" :data="block.videos[0]"/>
              </div>
              <UIEditAdminBtn
                v-if="block.videos.length > 0"
                app="lesson"
                model="video"
                :id="block.videos[0].id"
                class="mt-2"
              />
              <div v-if="block.type3_content" v-html="block.type3_content" class="block-w-table mt-3 text-[14px] !leading-[110%] lg:text-[16px] text-[#202021]"></div>
              <div v-if="block.items.length>0" class="space-y-1">
                <CardVoiceFile
                    v-for="item in block.items"
                    :key="item.id"
                    :item="item"
                    :reverse="false"
                    :opened="openedId === item.id"
                    :loading="fav_loading"
                    :show_add_to_fav="true"
                    @toggle_open="handleToggleOpen"
                    @toggle_fav="handlePharaseToggleFav"
                />
              </div>
              <div class="flex gap-4 mt-3">
                <Button v-if="user && !user.is_pupil && block.can_be_done" @click="toggleBlockDone(block.id,index)"
                        fluid
                        severity="success"
                        :icon="block.is_done ? 'pi pi-check-circle' :'' "
                        :outlined="!block.is_done"
                        label="Выполнено"/>
                <UIEditAdminBtn
                  app="lesson"
                  model="moduleblock"
                  :id="block.id"
                />
              </div>

            </CardBase>
          </div>
          <!--          <div class="grid grid-cols-2 gap-3">-->
          <!--            <Button outlined icon="pi pi-arrow-left" label="Предыдущий урок"/>-->
          <!--            <Button  icon-pos="right" icon="pi pi-arrow-right" label="Следующий урок"/>-->
          <!--          </div>-->
        </template>
      </template>
    </div>
    <div class="hidden lg:block col-span-3   ">
      <CardBase padding="sm" class="h-[75vh] sticky top-20 overflow-x-hidden overflow-y-auto overscroll-contain">
        <TypingText20 text="Словарь" class="mb-4"/>
        <div class="border border-[#D1D1E0] rounded-lg px-6 py-3 flex items-center justify-between mb-4 cursor-pointer"
             @click="dictionary_direction === 'ruEN' ? dictionary_direction = 'enRU' : dictionary_direction = 'ruEN'">
          <p >{{dictionary_direction==='ruEN' ? 'Русский' : 'Английский'}} </p>
          <svg width="63" height="28" viewBox="0 0 63 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="63" height="28" rx="14" fill="#EFEFF5"/>
            <path d="M24 11.918H39L34 6.91797M39.3329 16.0846H24.3329L29.3329 21.0846" stroke="black" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p >{{dictionary_direction==='ruEN' ? 'Английский' : 'Русский'}} </p>
          <p></p>
        </div>
        <div class="space-y-1 mb-3"
             v-for="group in  module?.module_dictionary_groups.length>0 ? module?.module_dictionary_groups : lesson.dictionary_groups ">

		<UIEditAdminBtn
		 app="lesson"
		 model="dictionarygroup"
		 :id="group.id"
		 :label="group.title"
		/>
		<TypingText18 v-if="!user || !user.is_superuser" :text="group.title"/>

          <CardDictionaryItem :dictionary_direction="dictionary_direction"
                              :item="item"
                              v-for="item in group.items"
                              :opened="opened_dictionary_id === item.id"
                              :show_checkbox="true"
                              @toggle_open="handleToggleDictionaryOpen"
                              @toggle_fav="handleToggleFav"
                              :loading="fav_loading"/>
        </div>
      </CardBase>
    </div>
  </div>
  </div>
  <Dialog v-model:visible="table_modal_visible"
          modal
          :show-header="false"
          class="relative p-0 w-[90%] lg:w-[50%]"
          >
    <i class="pi pi-times absolute top-3 right-3 cursor-pointer z-40" @click="table_modal_visible=false"></i>
    <img class="w-full h-auto object-contain" :src="table"/>

  </Dialog>
  <Dialog v-model:visible="video_tutorial_modal_visible"

          :show-header="false"

          class="w-[90%] lg:w-[65%] relative video-modal overflow-hidden"
          >

    <div class="px-4 py-2 flex justify-end">
        <svg @click="video_tutorial_modal_visible=false" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="0.5" y="0.5" width="23" height="23" rx="3.5" stroke="#E0E0EB"/>
          <path d="M8 16L16 8" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
          <path d="M8 8L16 16" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
    </div>
    <video width="100%" height="auto" preload="none" playsinline="true" id="video_player"
           controls="controls" autoplay="autoplay">
      <source :src="tutorial_video" type="video/mp4">
    </video>
  </Dialog>
  <Dialog v-model:visible="dictionary_modal_visible"
          modal
          header="Словарь"
          class="relative"
          :style="{ width: '35rem','padding': '0' }">
    <template #closebutton>
      <svg @click="dictionary_modal_visible=false" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="0.5" y="0.5" width="23" height="23" rx="3.5" stroke="#E0E0EB"/>
        <path d="M8 16L16 8" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
        <path d="M8 8L16 16" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
      </svg>
    </template>

    <div class="border border-[#D1D1E0] rounded-lg px-6 py-3 flex items-center justify-between mb-4 cursor-pointer"
         @click="dictionary_direction === 'ruEN' ? dictionary_direction = 'enRU' : dictionary_direction = 'ruEN'">
      <p >{{dictionary_direction==='ruEN' ? 'Русский' : 'Английский'}} </p>
      <svg width="63" height="28" viewBox="0 0 63 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="63" height="28" rx="14" fill="#EFEFF5"/>
        <path d="M24 11.918H39L34 6.91797M39.3329 16.0846H24.3329L29.3329 21.0846" stroke="black" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p >{{dictionary_direction==='ruEN' ? 'Английский' : 'Русский'}} </p>
      <p></p>
    </div>
    <div class="space-y-1 mb-3"
         v-for="group in  module?.module_dictionary_groups.length>0 ? module?.module_dictionary_groups : lesson.dictionary_groups ">
      <TypingText18 :text="group.title"/>
      <CardDictionaryItem :dictionary_direction="dictionary_direction"
                          :item="item"
                          v-for="item in group.items"
                          :opened="opened_dictionary_id === item.id"
                          :show_checkbox="true"
                          @toggle_open="handleToggleDictionaryOpen"
                          @toggle_fav="handleToggleFav"
                          :loading="fav_loading"/>
    </div>

  </Dialog>

  <footer class="block lg:hidden">
    <div class="fixed left-0 bottom-0 w-full h-[60px] bg-white pt-3 flex border-t border-[#EFEFEF] items-center justify-evenly z-50">
      <div @click="toggleMenu" class="footer-link flex flex-col items-center justify-center gap-1" >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 18C3.71667 18 3.47933 17.904 3.288 17.712C3.09667 17.52 3.00067 17.2827 3 17C2.99933 16.7173 3.09533 16.48 3.288 16.288C3.48067 16.096 3.718 16 4 16H20C20.2833 16 20.521 16.096 20.713 16.288C20.905 16.48 21.0007 16.7173 21 17C20.9993 17.2827 20.9033 17.5203 20.712 17.713C20.5207 17.9057 20.2833 18.0013 20 18H4ZM4 13C3.71667 13 3.47933 12.904 3.288 12.712C3.09667 12.52 3.00067 12.2827 3 12C2.99933 11.7173 3.09533 11.48 3.288 11.288C3.48067 11.096 3.718 11 4 11H20C20.2833 11 20.521 11.096 20.713 11.288C20.905 11.48 21.0007 11.7173 21 12C20.9993 12.2827 20.9033 12.5203 20.712 12.713C20.5207 12.9057 20.2833 13.0013 20 13H4ZM4 8C3.71667 8 3.47933 7.904 3.288 7.712C3.09667 7.52 3.00067 7.28267 3 7C2.99933 6.71733 3.09533 6.48 3.288 6.288C3.48067 6.096 3.718 6 4 6H20C20.2833 6 20.521 6.096 20.713 6.288C20.905 6.48 21.0007 6.71733 21 7C20.9993 7.28267 20.9033 7.52033 20.712 7.713C20.5207 7.90567 20.2833 8.00133 20 8H4Z" :fill="showMenu ? '#3333E8' : '#8F8FA3'"/>
        </svg>


        <p :class="showMenu ? 'text-primary' : ''">Меню</p>
      </div>
      <div @click="fetchTable" class="footer-link flex flex-col items-center justify-center gap-1" >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 10H21M10 3V21M3 5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5Z" stroke="#777788" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>


        <p>Таблица</p>
      </div>
      <div @click="toggleView('audio')" class="footer-link flex flex-col items-center justify-center gap-1" >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="24" height="24" fill="white"/>
          <path d="M10.0176 7.91699C10.1071 7.92018 10.1941 7.94779 10.2695 7.99609L15.8457 11.5791C15.9162 11.6243 15.9744 11.6864 16.0146 11.7598C16.0549 11.8333 16.0762 11.9162 16.0762 12C16.0762 12.0839 16.0549 12.1667 16.0146 12.2402C15.9744 12.3137 15.9162 12.3757 15.8457 12.4209L10.2695 16.0049C10.1941 16.0532 10.1071 16.0808 10.0176 16.084C9.92811 16.0871 9.83936 16.0663 9.76074 16.0234C9.68203 15.9805 9.61616 15.9169 9.57031 15.8398C9.52447 15.7628 9.50015 15.6746 9.5 15.585V8.41602C9.50015 8.32634 9.52447 8.23821 9.57031 8.16113C9.61615 8.08411 9.68205 8.02046 9.76074 7.97754C9.83934 7.93473 9.92813 7.91385 10.0176 7.91699Z" fill="#8F8FA3"/>
          <path fill-rule="evenodd" clip-rule="evenodd" d="M12 1C18.075 1 23 5.925 23 12C23 18.075 18.075 23 12 23C5.925 23 1 18.075 1 12C1 5.925 5.925 1 12 1ZM12 2.5C9.48044 2.5 7.06382 3.50063 5.28223 5.28223C3.50063 7.06382 2.5 9.48044 2.5 12C2.5 14.5196 3.50063 16.9362 5.28223 18.7178C7.06382 20.4994 9.48044 21.5 12 21.5C14.5196 21.5 16.9362 20.4994 18.7178 18.7178C20.4994 16.9362 21.5 14.5196 21.5 12C21.5 9.48044 20.4994 7.06382 18.7178 5.28223C16.9362 3.50063 14.5196 2.5 12 2.5Z" fill="#8F8FA3"/>
        </svg>



        <p>Аудиоурок</p>
      </div>

      <div @click="dictionary_modal_visible = true" class="footer-link flex flex-col items-center justify-center gap-1" >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 19.025C2.45 19.025 1.97933 18.8293 1.588 18.438C1.19667 18.0466 1.00067 17.5756 1 17.025V15.025C1 14.7416 1.096 14.5043 1.288 14.313C1.48 14.1216 1.71733 14.0256 2 14.025C2.28267 14.0243 2.52033 14.1203 2.713 14.313C2.90567 14.5056 3.00133 14.743 3 15.025V17.025H21V15.025C21 14.7416 21.096 14.504 21.288 14.312C21.48 14.12 21.7173 14.0243 22 14.025C22.2827 14.0256 22.5203 14.1216 22.713 14.313C22.9057 14.5043 23.0013 14.7416 23 15.025V17.025C23 17.575 22.8043 18.046 22.413 18.438C22.0217 18.83 21.5507 19.0256 21 19.025H3ZM7.35 15.225C6.53333 15.225 5.89167 15.0126 5.425 14.588C4.95833 14.1633 4.725 13.584 4.725 12.85C4.725 12.15 4.996 11.5793 5.538 11.138C6.08 10.6966 6.77567 10.4756 7.625 10.475C8.00833 10.475 8.36267 10.5043 8.688 10.563C9.01333 10.6216 9.29233 10.7173 9.525 10.85V10.5C9.525 10.05 9.371 9.69164 9.063 9.42498C8.755 9.15831 8.334 9.02498 7.8 9.02498C7.55 9.02498 7.31267 9.06264 7.088 9.13798C6.86333 9.21331 6.659 9.31731 6.475 9.44998C6.325 9.56664 6.16267 9.63331 5.988 9.64998C5.81333 9.66664 5.65067 9.61664 5.5 9.49998C5.34933 9.38331 5.25767 9.23764 5.225 9.06298C5.19233 8.88831 5.24233 8.73398 5.375 8.59998C5.675 8.31664 6.02933 8.09998 6.438 7.94998C6.84667 7.79998 7.309 7.72498 7.825 7.72498C8.85833 7.72498 9.65 7.97098 10.2 8.46298C10.75 8.95498 11.025 9.66731 11.025 10.6V14.275C11.025 14.475 10.954 14.646 10.812 14.788C10.67 14.93 10.4993 15.0006 10.3 15C10.0833 15 9.90433 14.929 9.763 14.787C9.62167 14.645 9.55067 14.466 9.55 14.25V14.15H9.475C9.25833 14.4833 8.96667 14.746 8.6 14.938C8.23333 15.13 7.81667 15.2256 7.35 15.225ZM7.9 11.65C7.36667 11.65 6.95833 11.7543 6.675 11.963C6.39167 12.1716 6.25 12.4673 6.25 12.85C6.25 13.1833 6.375 13.4543 6.625 13.663C6.875 13.8716 7.2 13.9756 7.6 13.975C8.13333 13.975 8.58767 13.7876 8.963 13.413C9.33833 13.0383 9.52567 12.584 9.525 12.05C9.29167 11.9166 9.025 11.8166 8.725 11.75C8.425 11.6833 8.15 11.65 7.9 11.65ZM16.325 15.225C15.6417 15.225 15.121 15.075 14.763 14.775C14.405 14.475 14.1757 14.2416 14.075 14.075H14V14.4C14 14.6 13.9293 14.771 13.788 14.913C13.6467 15.055 13.4757 15.1256 13.275 15.125C13.0743 15.1243 12.8993 15.0493 12.75 14.9C12.6007 14.7506 12.5257 14.5756 12.525 14.375V5.74998C12.525 5.53331 12.6 5.34998 12.75 5.19998C12.9 5.04998 13.0833 4.97498 13.3 4.97498C13.5167 4.97498 13.7 5.04998 13.85 5.19998C14 5.34998 14.075 5.53331 14.075 5.74998V7.79998L14 8.79998H14.075C14.125 8.71664 14.325 8.50398 14.675 8.16198C15.025 7.81998 15.575 7.64931 16.325 7.64998C17.3917 7.64998 18.2333 8.03331 18.85 8.79998C19.4667 9.56664 19.775 10.45 19.775 11.45C19.775 12.45 19.471 13.3293 18.863 14.088C18.255 14.8466 17.409 15.2256 16.325 15.225ZM16.1 9.04998C15.4333 9.04998 14.9167 9.29598 14.55 9.78798C14.1833 10.28 14 10.8256 14 11.425C14 12.0416 14.1833 12.5916 14.55 13.075C14.9167 13.5583 15.4333 13.8 16.1 13.8C16.7667 13.8 17.2877 13.5583 17.663 13.075C18.0383 12.5916 18.2257 12.0416 18.225 11.425C18.2243 10.8083 18.037 10.2583 17.663 9.77498C17.289 9.29164 16.768 9.04998 16.1 9.04998Z" fill="#777788"/>
        </svg>

        <p>Словарь</p>
      </div>
      <div @click="$router.push('/profile/favorite')" class="footer-link flex flex-col items-center justify-center gap-1" >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.0017 4.52804C10.8376 3.48411 9.31182 2.93592 7.74946 3.00019C6.1871 3.06447 4.71155 3.73614 3.63705 4.87217C2.56255 6.00819 1.974 7.51881 1.99673 9.08233C2.01946 10.6458 2.65167 12.1387 3.75874 13.243L10.5877 20.071C10.9628 20.446 11.4714 20.6566 12.0017 20.6566C12.5321 20.6566 13.0407 20.446 13.4157 20.071L20.2447 13.243C21.3518 12.1387 21.984 10.6458 22.0067 9.08233C22.0295 7.51881 21.4409 6.00819 20.3664 4.87217C19.2919 3.73614 17.8164 3.06447 16.254 3.00019C14.6917 2.93592 13.1659 3.48411 12.0017 4.52804ZM10.8297 6.17204L11.2947 6.63604C11.4823 6.82351 11.7366 6.92883 12.0017 6.92883C12.2669 6.92883 12.5212 6.82351 12.7087 6.63604L13.1737 6.17204C13.5427 5.79 13.9841 5.48527 14.4721 5.27563C14.9601 5.066 15.485 4.95565 16.0161 4.95104C16.5472 4.94642 17.074 5.04763 17.5656 5.24875C18.0571 5.44988 18.5037 5.74689 18.8793 6.12246C19.2549 6.49803 19.5519 6.94464 19.753 7.43622C19.9541 7.92781 20.0554 8.45453 20.0507 8.98564C20.0461 9.51676 19.9358 10.0416 19.7261 10.5297C19.5165 11.0177 19.2118 11.4591 18.8297 11.828L12.0017 18.657L5.17374 11.828C4.4451 11.0736 4.04193 10.0632 4.05104 9.01443C4.06015 7.96565 4.48083 6.9624 5.22246 6.22076C5.96409 5.47913 6.96734 5.05846 8.01613 5.04934C9.06492 5.04023 10.0753 5.44341 10.8297 6.17204Z" fill="#8F8FA3"/>
        </svg>

        <p>Избранное</p>
      </div>
    </div>
  </footer>
</template>

<style >
.footer-link{
  color: #777788;
  font-size: 11px
}

/* Общие стили таблицы */
table {
  width: 100%;
  border-collapse: collapse; /* убирает двойные границы */

}
td, th {
  border: 1px solid #e3e3e3 !important;
}
/* Заголовки таблицы */
thead th {
  background-color: #f3f4f6; /* светлый серый фон */
  color: #111827; /* тёмный текст */
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.875rem; /* 14px */
}

/* Строки таблицы */
tbody tr {
  border-bottom: 1px solid #e5e7eb;
}

tbody td[rowspan]:nth-child(3) {
  background-color: rgba(225, 225, 225, 0.24);
  font-weight: 600;
  text-align: center;
}

/* Ячейки таблицы */
tbody td {
  padding: 12px 16px;
  font-size: 0.875rem;
  color: #374151;
}

/* Чередование строк */
tbody tr:nth-child(even) {
  background-color: #f9fafb;
}


</style>
