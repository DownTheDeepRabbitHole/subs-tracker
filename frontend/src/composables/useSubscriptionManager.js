import { ref } from 'vue'
import axios from 'axios'
import { useHelpers } from './useHelpers'

export function useSubscriptionManager() {
  const subscriptions = ref([])
  const categories = ref([])
  const userPlans = ref([])
  const loading = ref({
    subscriptions: false,
    categories: false,
    userPlans: false,
  })

  const { showToast, handleError, formatDate } = useHelpers()

  const fetchSubscriptions = async () => {
    try {
      loading.value.subscriptions = true
      const response = await axios.get('/api/subscriptions/')
      subscriptions.value = response.data
      return response.data
    } catch (error) {
      handleError('Error fetching subscriptions', error)
    } finally {
      loading.value.subscriptions = false
    }
  }

  const fetchCategories = async () => {
    try {
      loading.value.categories = true
      const response = await axios.get('/api/categories/')
      categories.value = response.data
      return response.data
    } catch (error) {
      handleError('Error fetching categories', error)
    } finally {
      loading.value.categories = false
    }
  }

  const fetchPlan = async (planId) => {
    try {
      const response = await axios.get(`/api/plans/${planId}/`)
      return response.data
    } catch (error) {
      handleError('Error fetching plan', error)
    }
  }

  const fetchUserPlans = async (params = {}) => {
    try {
      loading.value.userPlans = true
      const response = await axios.get('/api/user-plans/', { params: params })
      userPlans.value = response.data.results
      return response.data.results
    } catch (error) {
      handleError('Error fetching user plans', error)
    } finally {
      loading.value.userPlans = false
    }
  }

  const fetchUserPlan = async (planId) => {
    try {
      const response = await axios.get(`/api/user-plans/${planId}/`)
      return response.data
    } catch (error) {
      handleError('Error fetching user plan', error)
      return null
    }
  }

  const deleteUserPlan = async (planId) => {
    try {
      await axios.delete(`/api/user-plans/${planId}/`)
      await fetchUserPlans()
      showToast('success', 'Plan removed', 'The plan was successfully removed from your list')
      return true
    } catch (error) {
      handleError('Error deleting user plan', error)
      return false
    }
  }

  const toggleUsage = async (planId, currentTrackUsage) => {
    try {
      await axios.patch(`/api/user-plans/${planId}/toggle-usage/`, {
        track_usage: !currentTrackUsage,
      })
      await fetchUserPlans()
      return true
    } catch (error) {
      handleError('Error toggling usage tracking', error)
      return false
    }
  }

  const addToUserPlans = async (planId, paymentDate, trackUsage = false) => {
    try {
      if (!paymentDate) {
        showToast('error', 'Invalid data', 'Please select a next payment date')
        return false
      }

      await axios.post('/api/user-plans/', {
        plan_id: planId,
        payment_date: formatDate(paymentDate),
        track_usage: trackUsage,
      })
      showToast('success', 'Plan added', 'Successfully added to your list')
      await fetchUserPlans()
      return true
    } catch (error) {
      handleError("Couldn't add to list", error)
      return false
    }
  }

  const deletePlan = async (planId) => {
    try {
      await axios.delete(`/api/plans/${planId}/`)
      await fetchSubscriptions()
      showToast('success', 'Plan removed', 'The plan was successfully deleted')
      return true
    } catch (error) {
      handleError('Error deleting plan', error)
      return false
    }
  }

  const createPlan = async (planData) => {
    const { name, cost, period, subscription } = planData
    if (!name || !period || !subscription) {
      showToast('error', 'Invalid data', 'Please provide all required fields.')
      return false
    }

    try {
      const response = await axios.post('/api/plans/', {
        name,
        cost,
        period: period.toLowerCase(),
        subscription: subscription.id,
      })
      showToast('success', 'Success', 'Plan created successfully.')
      await fetchSubscriptions()
      return response.data
    } catch (error) {
      handleError('Error creating plan', error)
      return null
    }
  }

  const createSubscription = async (name, categoryId) => {
    if (!name || !categoryId) {
      showToast('error', 'Invalid data', 'Please provide all fields.')
      return null
    }

    try {
      const response = await axios.post('/api/subscriptions/', {
        name,
        category: categoryId,
      })
      showToast('success', 'Success', 'Subscription added.')
      await fetchSubscriptions()
      return response.data
    } catch (error) {
      handleError('Error adding subscription', error)
      return null
    }
  }

  const updateSubscriptionCategory = async (subscriptionId, newCategoryId) => {
    if (!subscriptionId || !newCategoryId) {
      showToast('error', 'Invalid data', 'Subscription ID and new category are required.')
      return null
    }

    try {
      const response = await axios.patch(`/api/subscriptions/${subscriptionId}/`, {
        category: newCategoryId,
      })
      showToast('success', 'Success', 'Subscription category updated.')
      await fetchSubscriptions()
      return response.data
    } catch (error) {
      handleError('Error updating subscription category', error)
      return null
    }
  }

  const updatePlan = async (planData) => {
    const { name, cost, period, subscription } = planData
    if (!name || !cost || !period || !subscription) {
      showToast('error', 'Invalid data', 'Please provide all required fields.')
      return false
    }
    try {
      const response = await axios.put(`/api/plans/${planData.id}/`, {
        name,
        cost,
        period: period.toLowerCase(),
        subscription: subscription.id,
      })
      showToast('success', 'Success', 'Plan updated.')
      await fetchSubscriptions()
      return response.data
    } catch (error) {
      handleError('Error updating plans', error)
      return null
    }
  }

  const updateUserPlan = async (planId, paymentDate, trackUsage) => {
    try {
      if (!paymentDate) {
        showToast('error', 'Invalid data', 'Payment date is required.')
        return false
      }

      const response = await axios.patch(`/api/user-plans/${planId}/`, {
        payment_date: formatDate(paymentDate),
        track_usage: trackUsage,
      })
      showToast('success', 'Plan updated', 'Successfully updated user plan')
      await fetchUserPlans()
      return response.data
    } catch (error) {
      handleError('Error updating user plan', error)
      return null
    }
  }

  // ** Helper functions **
  const generateDummyUserPlan = (form) => {
    const dummy = {
      id: 0,
      plan: 0,
      payment_date: '2025-03-09',
      last_updated: '2025-02-28',
      total_spent: 100,
      track_usage: true,
      usage_score: 5,
      average_usage: 5,
      user: 'user',
      cost: 11.99,
      plan_id: 8,
      plan_name: 'Plan Name',
      period: 'month',
      free_trial: false,
      subscription_id: 2,
      subscription_name: 'Subscription',
      category_id: 2,
      icon_url: 'https://icons.veryicon.com/png/o/business/settlement-platform-icon/default-16.png',
    }

    return {
      ...dummy,
      cost: form.plan?.cost ?? dummy.cost,
      plan_name: form.plan?.name || dummy.plan_name,
      period: form.plan?.period || dummy.period,
      free_trial: form.plan?.freeTrial ?? dummy.free_trial,
      payment_date: form.userPlan?.paymentDate || dummy.payment_date,
      track_usage: form.userPlan?.trackUsage ?? dummy.track_usage,
      subscription_id: form.plan?.subscription?.id ?? dummy.subscription_id,
      subscription_name: form.plan?.subscription?.name || dummy.subscription_name,
      category_id:
        form.plan?.subscription?.category?.id ??
        form.plan?.subscription?.category ??
        dummy.category_id,
      icon_url: form.plan?.subscription?.icon_url || dummy.icon_url,
    }
  }

  const getCategoryName = (categoryId) => {
    const category = categories.value.find((cat) => cat.id === categoryId)
    return category ? category.name : 'Unknown'
  }

  const initData = async () => {
    await Promise.all([fetchCategories(), fetchSubscriptions(), fetchUserPlans()])
  }

  return {
    subscriptions,
    categories,
    userPlans,
    loading,

    fetchSubscriptions,
    fetchCategories,
    fetchPlan,
    fetchUserPlans,
    fetchUserPlan,
    deleteUserPlan,
    toggleUsage,
    updateSubscriptionCategory,
    updatePlan,
    updateUserPlan,
    addToUserPlans,
    deletePlan,
    createPlan,
    createSubscription,
    getCategoryName,
    generateDummyUserPlan,
    initData,
  }
}
