<script setup>
import { reactive } from 'vue'

import { useUser } from '@/composables'

const {register} = useUser()

const form = reactive({
  username: '',
  password: '',
  rememberMe: true,
})

const handleSubmit = () => {
  register(form.username, form.password)
}
</script>

<template>
  <Card class="w-100">
    <template #content>
      <h2 class="text-2xl font-semibold text-center mb-6">Create Account</h2>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label
            for="username"
            class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"
            >Username</label
          >
          <InputText
            id="username"
            v-model="form.username"
            placeholder="Enter your username"
            required
            fluid
          />
        </div>

        <div class="mb-4">
          <label
            for="password"
            class="block text-sm font-medium text-text-muted-color dark:text-text-muted-color"
            >Password</label
          >
          <Password
            id="password"
            v-model="form.password"
            placeholder="Enter your password"
            toggleMask
            required
            fluid
          />
        </div>

        <div class="mb-6 flex items-center">
          <Checkbox inputId="remember-me" v-model="form.rememberMe" binary />
          <label for="remember-me" class="ml-2 text-sm">Remember me</label>
        </div>

        <div class="mb-6">
          <Button label="Register" type="submit" class="w-full p-button-lg p-button-primary" />
        </div>
      </form>

      <div class="text-center mt-4">
        <p class="text-sm">
          Already have an account?
          <RouterLink to="/login" class="text-blue-500 hover:underline">Sign In</RouterLink>
        </p>
      </div>
    </template>
  </Card>
</template>

<style>
.full-width {
  width: 100%;
}

.full-width .p-inputtext {
  width: 100%;
}
</style>
