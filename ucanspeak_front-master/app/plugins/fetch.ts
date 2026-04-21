import { createAuthRepository } from "~/repository/auth";
import { createLessonsRepository } from "~/repository/lessons";
import { createTrainerRepository } from "~/repository/trainer";
import { createSchoolRepository } from "~/repository/school";

export default defineNuxtPlugin({
  name: 'fetch',
  parallel: true,
  async setup(nuxtApp){
    const config = useRuntimeConfig();

    const appFetch = $fetch.create({
      baseURL: config.public.apiUrl as string,
      retry: false,
      onRequest({ options }) {
        options.headers.append('Accept', 'application/json');

        const auth_token = useCookie('auth_token')

        if(auth_token.value){
          options.headers.append('Authorization', `Token ${auth_token.value}`);
        }
       
      },
      async onResponseError({ response }) {

        if(response.status == 401){
          const authCookie = useCookie('auth_token')
          authCookie.value = null
          nuxtApp.runWithContext(() => navigateTo('/'));
        }
      }
    });

    const api = {
      auth: createAuthRepository(appFetch),
      lessons: createLessonsRepository(appFetch),
      trainer: createTrainerRepository(appFetch),
      school: createSchoolRepository(appFetch),
    };
    
    return {
      provide: {
        appFetch,
        api
      }
    }
  }
});