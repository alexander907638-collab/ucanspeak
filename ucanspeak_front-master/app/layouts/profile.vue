<script setup lang="ts">
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)

const links = [
  {title:'Профиль', to:'/profile'},
  {title:'Избранное', to:'/profile/favorite'},

]

if (!user.value.is_school && !user.value.is_pupil) {
  links.push(
      {title:'Прогресс', to:'/profile/progress'},
  )
}

if (user.value.is_school){
  links.push(
      {title:'Ученики', to:'/profile/pupils'},
  )
}
const headerText = useState('header_text')
headerText.value = 'Профиль'


</script>

<template>
  <BlockHeader/>

  <div class="container pt-16 lg:pt-24 pb-10 md:pb-0">
    <BlockBaseBreadcrumbs
        :items="[
    { label: 'Главная', to: '/' },
    { label: 'Профиль'},

  ]"/>

    <div class="grid grid-cols-12 gap-5">
      <div class="col-span-12 md:col-span-3">
        <CardBase padding="sm" class="sticky top-5 space-y-1">
          <nuxt-link
              v-for="(link, i) in links"
              :key="i"
              :to="link.to"
              exact-active-class="bg-[#F6F6FB]"
              active-class="bg-[#F6F6FB]"
              class="w-full flex items-center justify-between  cursor-pointer border border-[#E8E8E9] gap-2 p-3 rounded-lg hover:bg-[#F6F6FB] transition-[0.2s] duration-[ease-in-out] ease-[all]"

          >
            <span> {{ i + 1 }}. {{ link.title }}</span>

          </nuxt-link>
        </CardBase>
      </div>
      <div class="col-span-12 md:col-span-9">
        <slot/>
      </div>
    </div>

  </div>
  <BlockFooter/>
</template>
