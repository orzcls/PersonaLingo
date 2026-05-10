/** @type {import('tailwindcss').Config} */
// Soft Scholar theme tokens.
// Legacy key names (primary/secondary/accent/dark) are preserved so existing
// class names in .vue files visually map onto the new palette without edits.
// Semantic aliases (paper/ink/indigo/ochre/rouge/sage) are exposed for new code.

const paper = {
  50: '#FBF7EE',   // page background (ivory)
  100: '#F3ECDC',  // block surface
  200: '#E8DEC6',  // subtle divider surface
  300: '#D9CBA8',
  400: '#C7B48A',
  500: '#B39E74'
}

const ink = {
  50: '#F6F1E7',
  100: '#E8DEC6',
  200: '#C4BBA8',
  300: '#9A9487',   // annotation grey
  400: '#7A7668',
  500: '#5A5E6E',   // secondary text
  600: '#3F4352',
  700: '#2F3342',   // body text
  800: '#23273A',
  900: '#1B1F2A',   // heading ink
  950: '#0F1220'
}

const indigo = {
  50: '#EEF1F8',
  100: '#DCE2EF',
  200: '#B6C0DC',
  300: '#8B9AC5',
  400: '#5D6FA6',
  500: '#3B4F88',
  600: '#2C3E6B',   // primary brand
  700: '#243458',
  800: '#1C2A52',   // hover/active
  900: '#14204A',
  950: '#0C1538'
}

const ochre = {
  50: '#FAF1E3',
  100: '#F2DFBF',
  200: '#E8C796',
  300: '#E3B98E',   // soft highlight
  400: '#D49B5E',
  500: '#B8692B',   // accent numerals / waves
  600: '#9C5520',
  700: '#7C411A',
  800: '#5E3115',
  900: '#422210',
  950: '#2A1609'
}

const rouge = {
  500: '#C35344',
  600: '#A8402E',   // destructive only
  700: '#882F20'
}

const sage = {
  50: '#EEF3EE',
  100: '#D8E3D9',
  200: '#B3C7B5',
  300: '#8DAB90',
  400: '#6B8A6E',
  500: '#6B8A6E',   // success / positive
  600: '#547056',
  700: '#3F5642',
  800: '#2D3E30',
  900: '#1D2A20',
  950: '#0F1711'
}

export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        // Semantic palette
        paper,
        ink,
        indigo,
        ochre,
        rouge,
        sage,

        // Legacy alias remap (keeps old class names visually on-brand)
        // dark-*  →  paper/ink (inverted lightness)
        dark: {
          50: '#FBF7EE',
          100: '#F3ECDC',
          200: '#E8DEC6',
          300: ink[300],
          400: ink[400],
          500: ink[500],
          600: ink[600],
          700: paper[200], // border-dark-700 → soft ivory divider
          800: paper[100], // bg-dark-800 → block surface
          900: paper[50],  // bg-dark-900 → page
          950: paper[50]   // bg-dark-950 → page
        },
        // accent-* → indigo
        accent: indigo,
        // secondary-* → ochre (mapping 500 to 500 for saturation parity)
        secondary: ochre,
        // primary-* → sage
        primary: sage
      },

      fontFamily: {
        sans: [
          'IBM Plex Sans',
          'Noto Sans SC',
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'sans-serif'
        ],
        serif: [
          'Fraunces',
          'Noto Serif SC',
          'Georgia',
          'Cambria',
          'serif'
        ],
        display: [
          'Fraunces',
          'Noto Serif SC',
          'Georgia',
          'serif'
        ],
        mono: [
          'JetBrains Mono',
          'ui-monospace',
          'SFMono-Regular',
          'monospace'
        ]
      },

      letterSpacing: {
        display: '-0.015em',
        uppercase: '0.22em',
        chapter: '0.28em'
      },

      boxShadow: {
        paper:
          '0 1px 0 rgba(27,31,42,.06), 0 18px 40px -28px rgba(27,31,42,.18)',
        hairline: '0 1px 0 rgba(27,31,42,.08)',
        inset: 'inset 0 1px 0 rgba(255,255,255,.4), inset 0 -1px 0 rgba(27,31,42,.05)'
      },

      borderRadius: {
        card: '4px',
        frame: '10px'
      },

      transitionTimingFunction: {
        scholar: 'cubic-bezier(.2,.8,.2,1)'
      },

      keyframes: {
        'ink-rise': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        'ink-blot': {
          '0%': { transform: 'scale(.6)', opacity: '0.25' },
          '50%': { transform: 'scale(1)', opacity: '0.85' },
          '100%': { transform: 'scale(1.4)', opacity: '0' }
        },
        'underline-draw': {
          '0%': { strokeDashoffset: '120' },
          '100%': { strokeDashoffset: '0' }
        },
        'ink-breath': {
          '0%, 100%': { opacity: '1', filter: 'blur(0px)' },
          '50%': { opacity: '.7', filter: 'blur(.3px)' }
        }
      },

      animation: {
        'ink-rise': 'ink-rise .42s cubic-bezier(.2,.8,.2,1) both',
        'ink-blot': 'ink-blot 1.8s cubic-bezier(.2,.8,.2,1) infinite',
        'ink-breath': 'ink-breath 2.6s ease-in-out infinite'
      }
    }
  },
  plugins: []
}
