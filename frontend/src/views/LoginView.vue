<script setup>
import { ref } from 'vue'
import { useUser } from '@/composables'

import { RouterLink } from 'vue-router'

const { login } = useUser()

const username = ref('')
const password = ref('')
const rememberMe = ref(true)
</script>

<template>
  <Card class="w-100">
    <template #content>
      <h2 class="text-center text-2xl font-semibold mb-6 text-text-color dark:text-text-color">
        Login
      </h2>

      <form @submit.prevent="login(username, password, rememberMe)">
        <div class="mb-4">
          <label
            for="username"
            class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"
          >
            Username
          </label>
          <InputText
            inputId="username"
            v-model="username"
            placeholder="Enter your username"
            fluid
            required
          />
        </div>

        <div class="mb-4">
          <label
            for="password"
            class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"
          >
            Password
          </label>
          <Password
            id="password"
            v-model="password"
            placeholder="Enter your password"
            type="password"
            :feedback="false"
            toggleMask
            fluid
            required
          />
        </div>

        <div class="mb-6 flex items-center">
          <Checkbox inputId="remember-me" v-model="rememberMe" binary />
          <label for="remember-me" class="ml-2 text-sm">Remember me</label>
        </div>

        <div class="mb-6">
          <Button
            label="Login"
            type="submit"
            icon="pi pi-sign-in"
            class="w-full p-button-lg p-button-primary"
          />
        </div>
      </form>

      <div class="text-center mt-4">
        <p class="text-sm">
          New user?
          <RouterLink to="/register" class="text-blue-500 hover:underline"
            >Create account</RouterLink
          >
        </p>
      </div>
    </template>
  </Card>
</template>
