<script setup lang="ts">
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
</script>

<template>
<footer class="block lg:hidden relative z-[1000]">
  <div class="fixed bottom-[-1px] w-full h-[60px] bg-white pt-1 flex items-center justify-evenly border-t border-[#EFEFEF]">
    <NuxtLink class="footer-link flex flex-col items-center justify-center gap-1" exact-active-class="active" active-class="active" to="/courses">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5 20L5 4C5 3.44772 5.44771 3 6 3L13 3V8.5L13.5528 8.22361C13.8343 8.08284 14.1657 8.08284 14.4472 8.22361L15 8.5V3L18 3C18.5523 3 19 3.44772 19 4V20C19 20.5523 18.5523 21 18 21H6C5.44772 21 5 20.5523 5 20Z" stroke="#8F8FA3" stroke-width="2"/>
      </svg>
      <p>Курсы</p>
    </NuxtLink>
    <NuxtLink class="footer-link flex flex-col items-center justify-center gap-1" exact-active-class="active" active-class="active" to="/courses/trainer">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8.5 19H8.51" stroke="#8F8FA3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M13 5H18M13 8H15.5M14 15.999V16.999C14 19.357 14 20.535 13.268 21.268C12.536 22 11.357 22 9 22H8C5.643 22 4.464 22 3.732 21.268C3 20.535 3 19.357 3 16.999V10.999C3 8.641 3 7.462 3.732 6.729C4.352 6.11 5.293 6.015 7 6M10 6V7C10 8.886 10 9.828 10.586 10.414C11.172 11 12.114 11 14 11V13L17 11C18.886 11 19.828 11 20.414 10.414C21 9.828 21 8.886 21 7V6C21 4.114 21 3.172 20.414 2.586C19.828 2 18.886 2 17 2H14C12.114 2 11.172 2 10.586 2.586C10 3.172 10 4.114 10 6Z" stroke="#8F8FA3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>



      <p>Тренажёр</p>
    </NuxtLink>
    <NuxtLink v-if="user?.last_lesson_url" :to="user?.last_lesson_url" class="footer-link flex flex-col items-center justify-center gap-1" exact-active-class="active" active-class="active">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.523 22 22 17.523 22 12C22 6.477 17.523 2 12 2C6.477 2 2 6.477 2 12C2 17.523 6.477 22 12 22Z" stroke="#8F8FA3" stroke-width="2" stroke-linejoin="round"/>
        <path d="M10 12V8.53601L13 10.268L16 12L13 13.732L10 15.464V12Z" stroke="#8F8FA3" stroke-width="2" stroke-linejoin="round"/>
      </svg>



      <p>Продолжить</p>
    </NuxtLink>
    <NuxtLink v-if="user" class="footer-link flex flex-col items-center justify-center gap-1" exact-active-class="active" active-class="active" to="/profile/favorite">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12.0017 4.52804C10.8376 3.48411 9.31182 2.93592 7.74946 3.00019C6.1871 3.06447 4.71155 3.73614 3.63705 4.87217C2.56255 6.00819 1.974 7.51881 1.99673 9.08233C2.01946 10.6458 2.65167 12.1387 3.75874 13.243L10.5877 20.071C10.9628 20.446 11.4714 20.6566 12.0017 20.6566C12.5321 20.6566 13.0407 20.446 13.4157 20.071L20.2447 13.243C21.3518 12.1387 21.984 10.6458 22.0067 9.08233C22.0295 7.51881 21.4409 6.00819 20.3664 4.87217C19.2919 3.73614 17.8164 3.06447 16.254 3.00019C14.6917 2.93592 13.1659 3.48411 12.0017 4.52804ZM10.8297 6.17204L11.2947 6.63604C11.4823 6.82351 11.7366 6.92883 12.0017 6.92883C12.2669 6.92883 12.5212 6.82351 12.7087 6.63604L13.1737 6.17204C13.5427 5.79 13.9841 5.48527 14.4721 5.27563C14.9601 5.066 15.485 4.95565 16.0161 4.95104C16.5472 4.94642 17.074 5.04763 17.5656 5.24875C18.0571 5.44988 18.5037 5.74689 18.8793 6.12246C19.2549 6.49803 19.5519 6.94464 19.753 7.43622C19.9541 7.92781 20.0554 8.45453 20.0507 8.98564C20.0461 9.51676 19.9358 10.0416 19.7261 10.5297C19.5165 11.0177 19.2118 11.4591 18.8297 11.828L12.0017 18.657L5.17374 11.828C4.4451 11.0736 4.04193 10.0632 4.05104 9.01443C4.06015 7.96565 4.48083 6.9624 5.22246 6.22076C5.96409 5.47913 6.96734 5.05846 8.01613 5.04934C9.06492 5.04023 10.0753 5.44341 10.8297 6.17204Z" fill="#8F8FA3"/>
      </svg>


      <p>Избранное</p>
    </NuxtLink>
    <NuxtLink v-if="user" class="footer-link flex flex-col items-center justify-center gap-1" exact-active-class="active" active-class="active" to="/profile">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 18C4 16.9391 4.42143 15.9217 5.17157 15.1716C5.92172 14.4214 6.93913 14 8 14H16C17.0609 14 18.0783 14.4214 18.8284 15.1716C19.5786 15.9217 20 16.9391 20 18C20 18.5304 19.7893 19.0391 19.4142 19.4142C19.0391 19.7893 18.5304 20 18 20H6C5.46957 20 4.96086 19.7893 4.58579 19.4142C4.21071 19.0391 4 18.5304 4 18Z" stroke="#8F8FA3" stroke-width="2" stroke-linejoin="round"/>
        <path d="M12 10C13.6569 10 15 8.65685 15 7C15 5.34315 13.6569 4 12 4C10.3431 4 9 5.34315 9 7C9 8.65685 10.3431 10 12 10Z" stroke="#8F8FA3" stroke-width="2"/>
      </svg>


      <p>Профиль</p>
    </NuxtLink>
    <NuxtLink v-else class="footer-link flex flex-col items-center justify-center gap-1" exact-active-class="active" active-class="active" to="/login">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 18C4 16.9391 4.42143 15.9217 5.17157 15.1716C5.92172 14.4214 6.93913 14 8 14H16C17.0609 14 18.0783 14.4214 18.8284 15.1716C19.5786 15.9217 20 16.9391 20 18C20 18.5304 19.7893 19.0391 19.4142 19.4142C19.0391 19.7893 18.5304 20 18 20H6C5.46957 20 4.96086 19.7893 4.58579 19.4142C4.21071 19.0391 4 18.5304 4 18Z" stroke="#8F8FA3" stroke-width="2" stroke-linejoin="round"/>
        <path d="M12 10C13.6569 10 15 8.65685 15 7C15 5.34315 13.6569 4 12 4C10.3431 4 9 5.34315 9 7C9 8.65685 10.3431 10 12 10Z" stroke="#8F8FA3" stroke-width="2"/>
      </svg>


      <p>Авторизация</p>
    </NuxtLink>
  </div>
</footer>
</template>

<style lang="sass">
.footer-link
  color: #777788
  p
    font-size: 11px

  &.active
    color: #3333E8
    svg
      path
        stroke: #3333E8
</style>