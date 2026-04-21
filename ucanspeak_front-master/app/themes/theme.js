
import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/lara';

const CustomTheme = definePreset(Aura, {
    semantic: {
        primary: {
            50: '#fffbe6',
            100: '#dfcde9',
            200: '#bca0ea',
            300: '#9374ea',
            400: '#5e49e9',
            500: '#3333E8',
            600: '#3333E8',
            700: '#5c2164',
            800: '#531d35',
            900: '#451a03',
            950: '#1a0000'
        },
        colorScheme: {
            light: {
                primary: {
                    color: '#3333E8',
                    inverseColor: '#ffffff',
                    hoverColor: '#3333E8',
                    activeColor: '#3333E8'
                },
                highlight: {
                    background: '#dfcde9',
                    focusBackground: '#bca0ea',
                    color: '#451a03',
                    focusColor: '#451a03'
                }
            },
            dark: {
                primary: {
                    color: '#bca0ea',
                    inverseColor: '#451a03',
                    hoverColor: '#dfcde9',
                    activeColor: '#3333E8'
                },
                highlight: {
                    background: 'rgba(255, 251, 235, .08)',
                    focusBackground: 'rgba(255, 251, 235, .12)',
                    color: 'rgba(255,251,235,.95)',
                    focusColor: 'rgba(255,251,235,.95)'
                }
            }
        }
    },
    rules: {
        global: {
            fontSize: '0.75rem',
            borderRadius: '0.2rem'
        },
        button: {
            fontSize: '0.75rem',
            padding: '0.25rem 0.5rem',
            gap: '0.3rem'
        },
        input: {
            fontSize: '0.75rem',
            padding: '0.3rem 0.5rem'
        },
        dropdown: {
            fontSize: '0.75rem',
            itemPadding: '0.25rem 0.5rem'
        },
        datatable: {
            cellPadding: '0.25rem 0.5rem',
            fontSize: '0.75rem'
        },
        dialog: {
            padding: '0.75rem',
            headerFontSize: '0.9rem',
            contentFontSize: '0.75rem'
        },
        card: {
            padding: '0.75rem'
        },
        tabview: {
            fontSize: '0.75rem'
        },
        checkbox: {
            size: '1rem'
        },
        radiobutton: {
            size: '1rem'
        }
    }
});

export default {
    preset: CustomTheme,
    options: {
        darkModeSelector: '.p-dark'
    }
};
