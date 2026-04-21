import Aura from '@primeuix/themes/lara';

export default defineNuxtConfig({
  devtools: { enabled: true },

  future: {
    compatibilityVersion: 4
  },
  app: {
    head: {
      link: [
        {
          rel: 'icon',
          type: 'image/png',
          href: '/fav.png'
        }
      ]
    }
  },

  modules: [
    '@pinia/nuxt',
    "@nuxtjs/tailwindcss",
    "@primevue/nuxt-module",
    'nuxt3-notifications',
    'vue3-carousel-nuxt',
  ],

  css: [
    '~/assets/styles/tailwind.css',
    '~/assets/styles/sass/style.sass',
    'primeicons/primeicons.css',
    '~/assets/styles/vars.css',
  ],

  ssr: false,

  primevue: {

    autoImport: true,
    components: {
      exclude: ['form', 'carousel','chart']
    },
    options: {

      theme: {
        preset: Aura
      }
    },
    importTheme: { from: '~/themes/theme.js' },
  },

  runtimeConfig: {
    public:{
      //apiUrl: 'http://localhost:8000',
      apiUrl: 'https://new.ucanspeak.ru',
    }
  },
  compatibilityDate: '2025-04-07',
})