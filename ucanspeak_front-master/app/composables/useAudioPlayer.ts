const audio = new Audio()
const currentPlayingId = ref<string | null>(null)
const isPlaying = ref(false)

export const useAudioPlayer = () => {
    const play = (id: string, src: string) => {
        // Если играет тот же трек - пауза
        if (currentPlayingId.value === id && isPlaying.value) {
            audio.pause()
            isPlaying.value = false
            return
        }

        // Если играет другой трек - переключаемся
        audio.src = src
        audio.play()
        currentPlayingId.value = id
        isPlaying.value = true
    }

    const pause = () => {
        audio.pause()
        isPlaying.value = false
    }

    audio.addEventListener('ended', () => {
        isPlaying.value = false
        currentPlayingId.value = null
    })

    return {
        play,
        pause,
        currentPlayingId: readonly(currentPlayingId),
        isPlaying: readonly(isPlaying)
    }
}