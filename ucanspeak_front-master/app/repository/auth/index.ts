import {useAuthStore} from "~/stores/auth";
import type {User} from "~/repository/auth/types";

export function createAuthRepository(appFetch: typeof $fetch){
    const {setUser} = useAuthStore()

    const authCookie = useCookie('auth_token')
    return{
        register(payload:any){
            return appFetch('/auth/users/', {
                method: 'POST',
                body: {...payload}
            })
        },
        login(body: any){
            return appFetch('/auth/token/login/',{
                method: 'POST',
                body
            })
        },
        force_login(body: any) {
            return appFetch('/api/user/force_login', {
                method: 'POST',
                body
            })
        },
        async logout(all_devices:boolean){
            authCookie.value = null
            await appFetch('/auth/token/logout/',{
                method:'post',
                body:{all_devices}
            })
            window.location.href='/'
        },
        async update(formData: FormData){
            const response = await appFetch<User>('/api/user/update', {
                method: 'patch',
                body: formData
            })
            setUser(response)
        },
        async me(){
            try{
                const response =  await appFetch<User>('/api/user/me')

                setUser(response)
            }catch(error){
                console.log(error)
                authCookie.value = null
                window.location.reload()
            }
        },

        reset_password(body){
            return appFetch('/api/user/reset_password',{
                method: 'POST',
                body
            })
        },

    }
}


