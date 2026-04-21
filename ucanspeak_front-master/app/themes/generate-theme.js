#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import chroma from 'chroma-js';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const colorArg = args.find(arg => arg.startsWith('--color='));
const outArg = args.find(arg => arg.startsWith('--out='));

if (!colorArg) {
    console.error('❌ Please provide a base color: --color=#f59e0b');
    process.exit(1);
}

const baseColorHex = colorArg.split('=')[1];
const outputPath = outArg ? outArg.split('=')[1] : './themeConfig.js';

function generateThemeConfig(baseColorHex) {
    const scale = chroma.scale(['#fffbe6', baseColorHex, '#451a03']).mode('lab').colors(10);
    const [c50, c100, c200, c300, c400, c500, c600, c700, c800, c900] = scale;
    const c950 = chroma(c900).darken(1.5).hex();

    return `
import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/lara';

const CustomTheme = definePreset(Aura, {
    semantic: {
        primary: {
            50: '${c50}',
            100: '${c100}',
            200: '${c200}',
            300: '${c300}',
            400: '${c400}',
            500: '${c500}',
            600: '${c600}',
            700: '${c700}',
            800: '${c800}',
            900: '${c900}',
            950: '${c950}'
        },
        colorScheme: {
            light: {
                primary: {
                    color: '${c500}',
                    inverseColor: '#ffffff',
                    hoverColor: '${c600}',
                    activeColor: '${c700}'
                },
                highlight: {
                    background: '${c100}',
                    focusBackground: '${c200}',
                    color: '${c900}',
                    focusColor: '${c900}'
                }
            },
            dark: {
                primary: {
                    color: '${c200}',
                    inverseColor: '${c900}',
                    hoverColor: '${c100}',
                    activeColor: '${c500}'
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
`;
}

const themeCode = generateThemeConfig(baseColorHex);
fs.writeFileSync(outputPath, themeCode);
console.log(`✅ Theme config generated at: ${outputPath}`);
