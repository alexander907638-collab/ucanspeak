export function createSchoolRepository(appFetch: typeof $fetch) {
    return {
        // Получить всех учеников школы
        list() {
            return appFetch(`/api/user/school-pupils/`)
        },

        // Получить конкретного ученика
        retrieve(id: string) {
            return appFetch(`/api/user/school-pupils/${id}/`)
        },
        logo(slug: string) {
            return appFetch(`/api/user/school?slug=${slug}`)
        },


        // Создать нового ученика
        create(body: object) {
            return appFetch(`/api/user/school-pupils/`, {
                method: 'POST',
                body
            })
        },

        // Редактировать ученика (частичное обновление)
        update(id: string, body: object) {
            return appFetch(`/api/user/school-pupils/${id}/`, {
                method: 'PATCH',
                body
            })
        },

        // Разлогинить ученика на всех устройствах
        force_logout_pupil(id: string | number) {
            return appFetch(`/api/user/school-pupils/${id}/force_logout/`, {
                method: 'POST'
            })
        },

        // Удалить ученика из школы
        destroy(id: string) {
            return appFetch(`/api/user/school-pupils/${id}/`, {
                method: 'DELETE'
            })
        },

    }
}