import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

import { jwtDecode } from 'jwt-decode'
import Cookies from 'js-cookie'

// From https://medium.com/@tahnyybelguith/authentication-and-authorization-implementation-with-vue-js-6afcbb821c85
router.beforeEach((to, from, next) => {
  const token = Cookies.get('access_token')

  // Check for token expiry to ensure users have authenticated to access webpages
  if (token) {
    const jwtPayload = jwtDecode(token)

    if (jwtPayload.exp < Date.now() / 1000) {
      Cookies.remove('access_token')
      next('/login')
      return
    }
  }

  // If the user is already authenticated and is trying to access login or register
  if ((to.name === 'login' || to.name === 'register') && token) {
    // Redirect to the home page or the previous route (from.path)
    next(from.path || '/')
  } else if (to.meta.requiresAuth && !token) {
    // If the route requires authentication and no token is found, redirect to login
    next('/login')
  } else {
    // If not, directs to normal route
    next()
  }
})

export default router
