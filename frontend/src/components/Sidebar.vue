<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Cookies from 'js-cookie'

import MobileOverlay from '@/components/MobileOverlay.vue'

const SIDEBAR_WIDTH = {
  COLLAPSED: 'w-20',
  EXPANDED: 'w-60',
  MOBILE_BREAKPOINT: 768,
}

const MENU_ITEMS = [
  { label: 'Home', icon: 'pi pi-home', route: '/' },
  { label: 'Shared List', icon: 'pi pi-users', route: '/shared-list' },
  { label: 'My List', icon: 'pi pi-list', route: '/my-list' },
  { label: 'Budget', icon: 'pi pi-book', route: '/budget' },
  { label: 'Add Plan', icon: 'pi pi-plus', route: '/add-plan' },
]

const router = useRouter()

const sidebarState = ref({
  isCollapsed: false,
  isHovered: false,
  isMobile: false,
})

const currentWidth = computed(() =>
  sidebarState.value.isMobile || sidebarState.value.isCollapsed
    ? SIDEBAR_WIDTH.COLLAPSED
    : SIDEBAR_WIDTH.EXPANDED,
)

const shouldExpand = computed(
  () =>
    (!sidebarState.value.isMobile && sidebarState.value.isHovered) ||
    (sidebarState.value.isMobile && !sidebarState.value.isCollapsed),
)

const checkMobile = () => {
  sidebarState.value.isMobile = window.innerWidth < SIDEBAR_WIDTH.MOBILE_BREAKPOINT
}

const toggleSidebar = () => {
  sidebarState.value.isCollapsed = !sidebarState.value.isCollapsed
}

const logout = () => {
  Cookies.remove('access_token')
  Cookies.remove('refresh_token')
  router.push('/login')
}

const isActive = computed(() => (path) => router.currentRoute.value.path === path)

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
</script>

<template>
  <!-- Darkens mobile screens on sidebar expand -->
  <MobileOverlay v-if="!sidebarState.isCollapsed && sidebarState.isMobile" @click="toggleSidebar" />

  <!-- Sidebar Container -->
  <div :class="[currentWidth]" class="flex-shrink-0 overflow-x-hidden transition-all duration-300">
    <aside
      class="fixed top-0 left-0 z-50 h-screen bg-white border-r border-gray-200 shadow-lg flex flex-col transition-all duration-300 ease-out"
      :class="[currentWidth, { [SIDEBAR_WIDTH.EXPANDED]: shouldExpand }]"
      @mouseenter="sidebarState.isHovered = true"
      @mouseleave="sidebarState.isHovered = false"
    >
      <div class="p-3 flex flex-col flex-1">
        <!-- Header Section -->
        <header class="flex items-center justify-between h-14 mb-4">
          <div class="flex flex-shrink-0 items-center gap-3">
            <RouterLink to="/">
              <img src="/favicon.ico" class="w-10" />
            </RouterLink>
            <span
              v-if="sidebarState.isHovered || !sidebarState.isCollapsed"
              class="text-xl font-bold text-gray-800 truncate transition-opacity duration-200"
              :class="{
                'opacity-0 w-0': sidebarState.isCollapsed && !sidebarState.isHovered,
                'opacity-100': !sidebarState.isCollapsed || sidebarState.isHovered,
              }"
            >
              SubsTracker
            </span>
          </div>
          <Button
            :icon="sidebarState.isCollapsed ? 'pi pi-chevron-right' : 'pi pi-chevron-left'"
            @click="toggleSidebar"
            class="!w-8 !h-8 shrink-0"
            variant="text"
            rounded
          />
        </header>

        <!-- Navigation Section -->
        <nav class="flex-1">
          <ul class="space-y-1">
            <li v-for="item in MENU_ITEMS" :key="item.route">
              <Button
                @click="router.push(item.route)"
                class="w-full justify-start group"
                :class="[
                  '!px-4 !py-3 font-semibold',
                  {
                    '!bg-primary-500 !text-white': isActive(item.route),
                    'hover:!bg-gray-100 text-gray-700': !isActive(item.route),
                  },
                ]"
                variant="text"
              >
                <i :class="item.icon" class="mr-3 text-lg" />
                <span
                  class="truncate transition-opacity duration-200"
                  :class="{
                    'opacity-0 w-0': sidebarState.isCollapsed && !sidebarState.isHovered,
                    'opacity-100': !sidebarState.isCollapsed || sidebarState.isHovered,
                  }"
                >
                  {{ item.label }}
                </span>
              </Button>
            </li>
          </ul>
        </nav>

        <!-- Footer Section -->
        <div class="pt-3">
          <Divider />
          <Button
            @click="logout"
            class="!px-4 !py-3 w-full justify-start"
            variant="text"
            severity="danger"
          >
            <i class="pi pi-sign-out mr-3 text-lg" />
            <span
              class="truncate transition-opacity duration-200"
              :class="{
                'opacity-0 w-0': sidebarState.isCollapsed && !sidebarState.isHovered,
                'opacity-100': !sidebarState.isCollapsed || sidebarState.isHovered,
              }"
            >
              Logout
            </span>
          </Button>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.sidebar-transition {
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
