<script setup>
import { ref } from 'vue'
import { useUser } from '@/composables'

const { userStore } = useUser()

const showDialog = ref(false)
</script>

<template>
  <Toolbar class="bg-white rounded-none border-0 sticky top-0 p-3 z-10">
    <template #start>
      <!-- Left aligned things (to potentially add later) -->
      <div class="flex-1"></div>
    </template>

    <template #end>
      <div class="flex items-center gap-3">
        <Button
          @click="showDialog = true"
          icon="pi pi-question-circle"
          variant="text"
          size="large"
          aria-label="Help"
        />

        <Button icon="pi pi-bell" variant="text" size="large" aria-label="Notifications" />

        <RouterLink to="/settings">
          <Button icon="pi pi-cog" variant="text" size="large" aria-label="Settings" />
        </RouterLink>

        <RouterLink to="/profile">
          <Button variant="text" aria-label="Profile">
            <template #icon>
              <img
                v-if="userStore.loaded"
                :src="userStore.profile.avatar_url"
                alt="Profile"
                class="object-cover !w-8 !h-8 rounded-full items-center"
              />
              <i v-else class="pi pi-user"></i>
            </template>
          </Button>
        </RouterLink>
      </div>
    </template>
  </Toolbar>

  <Dialog v-model:visible="showDialog" header="How to use" modal closable class="w-1/2">
    <Tabs value="0">
      <TabList>
        <Tab value="0">Overview</Tab>
        <Tab value="1">Getting Started</Tab>
        <Tab value="2">Notifications</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <p>
            Subs-tracker is an all-in-one website used to manage and track all your subscriptions.
          </p>

          <p>
            Choose subscriptions from a shared list or create custom subscriptions with your own
            information. Recieve notifications for upcoming payments, and integrate with
            RescueTime's screentime tracker to be notified of unused payments.
          </p>
        </TabPanel>

        <TabPanel value="1">
          <h3>Home View</h3>
          <p>
            The "Home View" provides a quick overview of your subscriptions, including your most
            used subscriptions, spending by category, upcoming payments, and unused subscriptions.
          </p>

          <Divider />

          <h3>Add a Subscription</h3>
          <p>
            To begin tracking your subscriptions, head to the "Shared List" section. You can find a
            subscription from the existing database using the search and sort filters. As well, you
            can add your own subscriptions using the "Add Plan" button.
          </p>
          <p>
            Once you have found a subscription, press the "+" button to add it to your own list.
            Select your most closest payment date from the calendar pop-up.
          </p>

          <Divider />

          <h3>Manage your subscriptions</h3>
          <p>
            "My List" section provides a detailed view of your subscriptions. Subscription
            information such as category, cost, and due date are displayed to help manage your
            subscriptions. Click the arrow buttons to sort, and filter icons to apply filters on the
            relevant columns.
          </p>
          <p>
            For example, you can find your most expensive subscriptions on a monthly basis by
            setting the period filter to "Month", which will display normalized costs per month, and
            applying a sort to the cost column.
          </p>
          <p>
            You will also see a "usage score" column. This grades your usage of a particular
            subscription based on optional integrated screentime data from Rescuetime. If you allow
            notifications in settings, you will also be notified of any unused subscriptions based
            on a user-defined threshold for usage.
          </p>

          <Divider />

          <h3>Create New Subscription</h3>
          <p>
            The "Add New Plan" page allows you to add a custom subscription to your list, which will
            also be displayed on the shared list. Subscription details can be inputted on the form,
            with a realtime preview displayed alongside.
          </p>
          <p>
            The "subscription" field allows you to input an existing service or create your own with
            the "+" button. Choosing a category will then update the service with the new category.
          </p>
          <p>
            The "track usage" and "next payment date" fields are specific to the subscription added
            to your list, and will not display on the shared list.
          </p>

          <Divider />

          <h3>My Budget</h3>
          <p>
            Finally, head to the "My Budget" section to create a budget for your subscriptions.
            Input a maximum value, and optionally select a category to apply the budget to. Press
            the "Set Budget" button to apply.
          </p>
          <p>
            The website will then find relevant subscription to fit within your budget while
            prioritizing useful subscriptions (highest usage scores). As well, the dropdown arrow
            will display your current subscriptions that are selected in budget.
          </p>
        </TabPanel>

        <TabPanel value="2">
          <p>
            To set up notifications for upcoming payments and unused subscriptions, head to the
            "Settings" section of the website.
          </p>
          <p>
            Under the "Notifications" section, enable the toggle for "Notify me about upcoming
            payments" to receive alerts for any upcoming subscription renewals. You can also set a
            custom threshold for unused subscriptions and be notified when a subscription's usage
            drops below that threshold, based on your RescueTime screentime data.
          </p>
          <p>
            To integrate with RescueTime's screentime tracker, you need to input your RescueTime API
            key. Simply navigate to the "API Integration" section within the settings and paste your
            API key in the designated field.
          </p>
          <p>
            Once entered, the integration will be active, and you will start receiving notifications
            based on your screentime usage. You can adjust the thresholds and notification
            preferences as needed to fit your tracking needs.
          </p>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </Dialog>
</template>

<style scoped>
p {
  margin-bottom: 1rem;
}
</style>
