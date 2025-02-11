import './assets/tailwind.css'
import './assets/base.css'

import { createApp } from 'vue'
import App from './App.vue'

import router from './router'
import axios from 'axios'

import ToastService from 'primevue/toastservice'

import PrimeVue from 'primevue/config'

axios.defaults.baseURL = 'http://localhost:8000/'
axios.defaults.headers['Content-Type'] = 'application/json'

axios.interceptors.request.use(
  function (config) {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
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
  theme: 'none',
})
app.use(router)

app.mount('#app')