module.exports = {
    content: [
        "./pages/**/*.{vue,js}",
        "./components/**/*.{vue,js}",
        "./layouts/**/*.{vue,js}",
        "./plugins/**/*.{js,ts}",
        "./nuxt.config.{js,ts}"
    ],
    darkMode: '.p-dark',
    theme: {
        container: {
            center: true,
            padding: {
                DEFAULT: '16px',   // по умолчанию (мобилки)
                sm: '10px',
                md: '20px',
                lg: '20px',
                xl: '40px',
                '2xl': '48px'
            },
            screens: {
                sm: '990px',
                md: '1024px',
                lg: '1200px',
                xl: '1400px',
                '2xl': '1400px'
            }
        },
        extend: {
            colors: {
                primary: '#3333E8', // Добавляем свой основной цвет
                secondary: '#9333EA', // Добавляем второй цвет
                customGray: '#B0B0B0', // Добавляем пользовательский серый
            },
            fontFamily: {
                'onest': ['Onest', 'sans-serif'],
            },
        },
    },
    plugins: [require('tailwindcss-primeui')]
}
