import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import RegisterView from '@/views/RegisterView.vue'
import LoginView from '@/views/LoginView.vue'
import SharedListView from '@/views/SharedListView.vue'
import MyListView from '@/views/MyListView.vue'
import AddPlanView from '@/views/AddPlanView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/shared-list',
      name: 'shared list',
      component: SharedListView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/my-list',
      name: 'my list',
      component: MyListView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/new-plan',
      name: 'new plan',
      component: AddPlanView,
      meta: {
        requiresAuth: true,
      },
    },
  ],
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
    next(from.path ? from.path : '/')
  } else if (to.meta.requiresAuth && !token) {
    // If the route requires authentication and no token is found, redirect to login
    next('/login')
  } else {
    // Otherwise, proceed to the requested route
    next()
  }
})

export default router
