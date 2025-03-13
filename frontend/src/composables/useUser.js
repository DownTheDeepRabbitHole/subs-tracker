import { reactive } from 'vue'
import axios from 'axios'
import router from '@/router'

import { registerOneSignal, logoutOneSignal } from '@/services/oneSignalService'
import { useHelpers } from './useHelpers'

export const userStore = reactive({
  profile: {
    id: 0,
    avatar_url: 'https://avatar.iran.liara.run/public',
    email: 'guest@example.com',
    first_name: 'John',
    last_name: 'Doe',
  },
  loaded: false,
  loggedIn: false,

  setProfile(profile) {
    this.profile = profile
    this.loaded = true
    this.loggedIn = true
  },

  login() {
    this.loggedIn = true
  },

  logout() {
    this.loggedIn = false
    this.resetProfile()
  },

  resetProfile() {
    this.profile = {
      id: 0,
      avatar_url: 'https://avatar.iran.liara.run/public',
      email: 'guest@example.com',
      first_name: 'John',
      last_name: 'Doe',
    }
    this.loaded = false
  },
})

export function useUser() {
  const { showToast, handleError } = useHelpers()

  const fetchUserProfile = async () => {
    if (userStore.loaded) return
    try {
      const response = await axios.get('/api/user/profile')
      userStore.setProfile(response.data)
      return userStore.profile
    } catch (error) {
      handleError('Error fetching user profile.', error)
    }
  }

  const login = async (username, password, rememberMe) => {
    try {
      await axios.post('/api/auth/login/', { username, password })
      await fetchUserProfile()
      await registerOneSignal(userStore.profile.id)
      router.push('/')
    } catch (error) {
      handleError('Failed to log in.', error)
    }
  }

  const register = async (username, password, rememberMe) => {
    try {
      await axios.post('/api/auth/register/', { username, password })
      await fetchUserProfile()
      await registerOneSignal(userStore.profile.id)
      showToast('success', 'Success', 'Registered successfully!')
      router.push('/')
    } catch (error) {
      handleError('Failed to register user.', error)
    }
  }

  const logout = async () => {
    try {
      await axios.post('/api/auth/logout/')
      userStore.logout()
      logoutOneSignal()
      router.push('/login')
    } catch (error) {
      handleError('Failed to log out.', error)
    }
  }

  return {
    userStore,
    fetchUserProfile,
    login,
    register,
    logout,
  }
}
