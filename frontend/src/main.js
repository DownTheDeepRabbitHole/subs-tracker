import './assets/tailwind.css'
import './assets/base.css'

import { createApp } from 'vue'
import App from './App.vue'

import router from './router'
import axios from 'axios'
import Cookies from 'js-cookie'

import ToastService from 'primevue/toastservice'

import PrimeVue from 'primevue/config'
import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

import VueApexCharts from "vue3-apexcharts";

axios.defaults.baseURL = 'http://localhost:8000/'
axios.defaults.headers['Content-Type'] = 'application/json'

axios.interceptors.request.use(
  function (config) {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    } else {
      delete config.headers['Authorization']
    }
    return config
  },
  function (error) {
    return Promise.reject(error)
  },
)

const app = createApp(App)

app.use(ToastService)

const MyPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#f3edfa',
      100: '#eadafb',
      200: '#d1aff2',
      300: '#a055eb',
      400: '#7728c6',
      500: '#560ea0',
      600: '#490c85',
      700: '#3c0572',
      800: '#350b5f',
      900: '#29044e',
      950: '#17022c',
    },
    colorScheme: {
      light: {
        surface: {
          0: '#ffffff',
          50: '{zinc.50}',
          100: '{zinc.100}',
          200: '{zinc.200}',
          300: '{zinc.300}',
          400: '{zinc.400}',
          500: '{zinc.500}',
          600: '{zinc.600}',
          700: '{zinc.700}',
          800: '{zinc.800}',
          900: '{zinc.900}',
          950: '{zinc.950}',
        },
        text: {
          default: '{surface.800}',
          muted: '{surface.600}',
          contrast: '{surface.0}',
        },
        border: '{primary.200}',
      },
      dark: {
        surface: {
          0: '{slate.950}',
          50: '{slate.50}',
          100: '{slate.100}',
          200: '{slate.200}',
          300: '{slate.300}',
          400: '{slate.400}',
          500: '{slate.500}',
          600: '{slate.600}',
          700: '{slate.700}',
          800: '{slate.800}',
          900: '{slate.900}',
          950: '{slate.950}',
        },
        text: {
          default: '{surface.0}',
          muted: '{surface.400}',
          contrast: '{surface.900}',
        },
        border: '{surface.700}',
      },
    },
    borderRadius: '6px',
    fontFamily: 'Poppins, sans-serif',
  },
})

app.use(PrimeVue, {
  theme: {
    preset: MyPreset,
    options: {
      cssLayer: {
        name: 'primevue',
        order: 'theme, base, primevue',
      },
    },
  },
})
app.use(VueApexCharts)
app.use(router)

app.mount('#app')
