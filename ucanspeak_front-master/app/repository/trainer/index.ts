
export function createTrainerRepository(appFetch: typeof $fetch){

    return {
        courses(){
            return appFetch('/api/trainer/courses/')
        },
        course(slug: string){
            return appFetch(`/api/trainer/courses/${slug}/levels/`)
        },
        topics(slug: string){
            return appFetch(`api/trainer/levels/${slug}/topics/`)
        },
        topic(slug: string){
            return appFetch(`/api/trainer/topics/${slug}/`)
        },
        toggle_trainer_favorite(body){
            return appFetch(`/api/trainer/toggle_favorite/`,{
                method:'POST',
                body
            })
        },
        topic_done(topic_id){
            return appFetch(`/api/trainer/topic_done/`,{
                method:'POST',
                body:{topic_id}
            })
        },
        favorites(){
            return appFetch('/api/trainer/favorites/')
        },
        clear_favorites() {
            return appFetch('/api/trainer/favorites/clear/', { method: 'POST' })
        },
    }

}
