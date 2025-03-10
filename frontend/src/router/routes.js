const routes = [
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
        path: 'add-plan/',
        name: 'add plan',
        component: () => import('@/views/AddPlanView.vue'),
        meta: { title: 'Add Plan' },
      },
      {
        path: 'edit-plan/:planId',
        name: 'edit plan',
        component: () => import('@/views/EditPlanView.vue'),
        meta: { title: 'Edit Plan' },
      },
      {
        path: 'edit-user-plan/:userPlanId',
        name: 'edit user plan',
        component: () => import('@/views/EditUserPlanView.vue'),
        meta: { title: 'Edit Plan' },
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
]

export default routes
