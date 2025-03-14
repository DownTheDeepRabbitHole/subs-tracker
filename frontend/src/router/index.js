import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import axios from 'axios'

import { userStore } from '@/composables'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

// From https://medium.com/@tahnyybelguith/authentication-and-authorization-implementation-with-vue-js-6afcbb821c85
router.beforeEach(async (to, from, next) => {
  if (userStore.loggedIn) {
    // Already authenticated, redirect to home or previous route
    if (to.name === 'login' || to.name === 'register') {
      return next(from.path || '/')
    }
  } else {
    if (to.meta.requiresAuth) {
      try {
        const response = await axios.post('/api/auth/verify/') // Verify user's session (access token)
        if (response.status === 200) {
          // Valid session, proceed to requested route
          userStore.login()
          return next()
        }
      } catch (error) {
        userStore.logout()
        return next('/login')
      }
    }
  }

  next() // If route doesn't require auth or user is logged in
})
export default router
