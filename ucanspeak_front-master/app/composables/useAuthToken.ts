export const useAuthToken = () => {
    const token = useCookie<string | null>('auth_token')
    const reset_token = () => token.value = null
    return {
        authToken: token,
        reset_token
    }
}
