<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Menu from 'primevue/menu'
import Button from 'primevue/button'
import Cookies from 'js-cookie'

const router = useRouter()
const isCollapsed = ref(false)

const menuItems = [
  { label: 'Home', icon: 'pi pi-home', route: '/' },
  { label: 'Shared List', icon: 'pi pi-users', route: '/shared-list' },
  { label: 'My List', icon: 'pi pi-list', route: '/my-list' },
  { label: 'Add Plan', icon: 'pi pi-plus', route: '/new-plan' },
]

const logout = () => {
  Cookies.remove('access_token')
  Cookies.remove('refresh_token')
  router.push('/login')
}

const isActive = (path) => router.currentRoute.value.path === path

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <div
    :class="{ 'w-[70px]': isCollapsed, 'w-64': !isCollapsed }"
    class="flex-shrink-0 overflow-x-hidden transition-all duration-300"
  >
    <aside
      class="fixed top-0 left-0 z-10 h-screen bg-white border-r border-gray-200 shadow-md flex flex-col p-3"
      :class="isCollapsed ? 'w-[70px]' : 'w-64'"
    >
      <div class="flex items-center justify-between px-3 h-14">
        <span v-if="!isCollapsed" class="text-lg font-semibold text-gray-800">SubsTracker</span>
        <Button icon="pi pi-bars" @click="toggleSidebar" rounded variant="text" />
      </div>

      <nav class="mt-4">
        <ul>
          <li v-for="item in menuItems" :key="item.route" class="mb-2">
            <Button
              severity="secondary"
              class="w-full flex justify-start items-center min-h-11"
              :class="{ 'text-primary-500 bg-primary-100': isActive(item.route) }"
              @click="router.push(item.route)"
              variant="text"
            >
              <i :class="item.icon"></i>
              <span v-if="!isCollapsed" class="ml-2">{{ item.label }}</span>
            </Button>
          </li>
        </ul>
      </nav>

      <div class="mt-auto border-t pt-3">
        <Button
          :label="!isCollapsed ? 'Logout' : ''"
          icon="pi pi-sign-out"
          severity="danger"
          variant="text"
          @click="logout"
          fluid
        />
      </div>
    </aside>
  </div>
</template>
