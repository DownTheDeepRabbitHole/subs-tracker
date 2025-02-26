<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import PanelMenu from 'primevue/panelmenu'
import Button from 'primevue/button'
import Cookies from 'js-cookie'

const router = useRouter()

// Reactive variable for sidebar collapse state
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

const isActive = (path) => {
  return router.currentRoute.value.path === path
}

// Function to toggle sidebar collapse state
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <div
    :class="{ 'w-16': isCollapsed, 'w-64': !isCollapsed }"
    class="flex-shrink-0 overflow-x-hidden transition-all duration-300"
  >
    <aside
      :class="[
        'fixed top-0 left-0 z-10 h-screen bg-white border-r dark:bg-gray-800 dark:border-gray-700 transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-64',
      ]"
    >
      <div class="flex items-center justify-between p-4">
        <!-- Logo/Brand -->
        <span v-if="!isCollapsed" class="text-xl font-bold text-primary">Sub Tracker</span>
        <!-- Toggle Button -->
        <Button icon="pi pi-bars" class="p-button-text p-2" @click="toggleSidebar" />
      </div>

      <!-- PanelMenu -->
      <PanelMenu
        :model="
          menuItems.map((item) => ({
            label: isCollapsed ? '' : item.label,
            icon: item.icon,
            command: () => router.push(item.route),
            class: isActive(item.route) ? 'bg-primary text-white' : '',
          }))
        "
        class="p-3"
      />

      <!-- Logout Button -->
      <div class="p-4">
        <Button
          label="Logout"
          icon="pi pi-sign-out"
          class="w-full p-button-danger"
          @click="logout"
        />
      </div>
    </aside>
  </div>
</template>

<style scoped>
.p-panelmenu .p-menuitem-link {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.p-panelmenu .p-menuitem-link:hover {
  background-color: #e5e7eb;
}

.dark .p-panelmenu .p-menuitem-link:hover {
  background-color: #4b5563;
}
</style>