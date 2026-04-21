// import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip';


export default defineNuxtPlugin({
    name: 'primevue',
    parallel: true,
    setup(nuxtApp){
        nuxtApp.vueApp.directive('tooltip', Tooltip);
        //nuxtApp.vueApp.use(ToastService);
        // return {
        //     provide: {
        //         toast: nuxtApp.vueApp.config.globalProperties.$toast
        //     }
        // }
    }
});