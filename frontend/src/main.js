import './assets/tailwind.css'
import './assets/base.css'

import { createApp } from 'vue'
import App from './App.vue'

import router from './router'
import axios from 'axios'
import Cookies from 'js-cookie'

import ToastService from 'primevue/toastservice'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';

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

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
        cssLayer: {
            name: 'primevue',
            order: 'theme, base, primevue'
        }
    }
}
})
app.use(router)

app.mount('#app')