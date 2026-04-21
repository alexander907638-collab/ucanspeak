export interface User {
    id: number
    email: string
    full_name: string | null
    phone: string | null
    avatar: string | null
    is_school: boolean
    is_pupil: boolean
    is_superuser: boolean
    is_subscription_expired: boolean
    subscription_expire: string | null
    max_logins: number | null
    last_lesson_url: string | null
    school: {
        slug: string | null
        image: string | null
    } | null
}
