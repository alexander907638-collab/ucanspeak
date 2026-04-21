
export function createLessonsRepository(appFetch: typeof $fetch){

    return {
        search(q){
            return appFetch(`/api/search/?q=${q}`)
        },
        tariffs(){
            return appFetch('/api/lesson/tariffs/')
        },
        dictionary_favorites(){
            return appFetch('/api/lesson/dictionary_favorites/')
        },
        lesson_item_favorites(){
            return appFetch('/api/lesson/lesson_item_favorites/')
        },
        courses(){
            return appFetch('/api/lesson/courses/')
        },
        course(slug: string){
            return appFetch(`/api/lesson/courses/${slug}`)
        },
        level(slug: string){
            return appFetch(`/api/lesson/levels/${slug}`)
        },
        lesson(slug: string){
            return appFetch(`/api/lesson/lessons/${slug}`)
        },
        lesson_table(slug: string){
            return appFetch(`/api/lesson/lessons/${slug}/get_table/`)
        }
        ,
        lesson_videos(slug: string){
            return appFetch(`/api/lesson/lessons/${slug}/videos/`)
        }
        ,
        module(id: string){
            return appFetch(`/api/lesson/modules/${id}`)
        },
        toggle_block(body){
            return appFetch(`/api/lesson/modules/toggle_block/`,{
                method:'POST',
                body
            })
        },
        toggle_dictionary_favorite(body){
            return appFetch(`/api/lesson/dictionary-items/${body.id}/toggle_favorite/`,{
                method:'POST',
                body
            })
        },
        toggle_phrase_favorite(body){
            return appFetch(`/api/lesson/modules/toggle_favorite/`,{
                method:'POST',
                body
            })
        },
        update_phrase(id: number, body: any) {
            return appFetch(`/api/lesson/phrases/${id}/`, {
                method: 'PATCH',
                body
            })
        },
        delete_phrase(id: number) {
            return appFetch(`/api/lesson/phrases/${id}/`, {
                method: 'DELETE'
            })
        },
        reorder_phrases(video_id: number, ids: number[]) {
            return appFetch(`/api/lesson/videos/${video_id}/reorder_phrases/`, {
                method: 'POST',
                body: { ids }
            })
        },
        clear_dictionary_favorites() {
            return appFetch('/api/lesson/dictionary_favorites/clear/', { method: 'POST' })
        },
        clear_lesson_item_favorites() {
            return appFetch('/api/lesson/lesson_item_favorites/clear/', { method: 'POST' })
        },

    }

}
