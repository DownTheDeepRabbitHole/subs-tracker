import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
          meta: { title: 'Home' },
        },
        {
          path: 'shared-list',
          name: 'shared list',
          component: () => import('@/views/SharedListView.vue'),
          meta: { title: 'Shared List' },
        },
        {
          path: 'my-list',
          name: 'my list',
          component: () => import('@/views/MyListView.vue'),
          meta: { title: 'My List' },
        },
        {
          path: 'new-plan',
          name: 'new plan',
          component: () => import('@/views/AddPlanView.vue'),
          meta: { title: 'New Plan' },
        },
        {
          path: 'test',
          name: 'test',
          component: () => import('@/views/TestView.vue'),
          meta: { title: 'Test' },
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { title: 'My Profile' },
        },
        {
          path: 'budget',
          name: 'budget',
          component: () => import('@/views/BudgetView.vue'),
          meta: { title: 'My Budgets' },
        },
      ],
    },

    {
      path: '/',
      component: () => import('@/layouts/PublicLayout.vue'),
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('@/views/LoginView.vue'),
          meta: { title: 'Login' },
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('@/views/RegisterView.vue'),
          meta: { title: 'Register' },
        },
        {
          path: ':catchAll(.*)',
          name: 'not-found',
          component: () => import('@/views/NotFoundView.vue'),
          meta: { title: 'Page Not Found' },
        },
      ],
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
