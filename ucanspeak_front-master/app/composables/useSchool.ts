export const useSchool = () => {
    const route = useRoute()
    const {$api} = useNuxtApp()

    // cookie (сохраняется между страницами)
    const school_slug = useCookie<string | null>('school_slug', {
        maxAge: 60 * 60 * 24 * 30,
    })

    const logo = ref<string | null>(null)
    const loading = ref(false)

    // ✅ установить slug из URL
    const setSchool = (schoolslug) => {
        if (schoolslug) {
            school_slug.value = String(schoolslug)
        }
    }

    // ✅ загрузка логотипа
    const fetchLogo = async (schoolslug) => {
        setSchool(schoolslug)
        if (!school_slug.value) {
            logo.value = null
            return
        }

        try {
            loading.value = true
            logo.value = await $api.school.logo(school_slug.value)
        } catch (e) {
            console.error('Ошибка загрузки школы', e)
            logo.value = null
        } finally {
            loading.value = false
        }
    }

    // ✅ авто-реакция на slug
    watch(school_slug, fetchLogo, { immediate: true })

    return {
        logo,
        fetchLogo,
    }
}