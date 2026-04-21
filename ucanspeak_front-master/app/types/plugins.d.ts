import type { IApi } from './api'


declare module '#app' {
    interface NuxtApp {
        $api: IApi
    }
}

declare module '@vue/runtime-core' {
    interface ComponentCustomProperties {
        $api: IApi
    }
}