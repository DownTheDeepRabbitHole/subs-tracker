// useSubscriptionManager.js
import { ref, computed } from 'vue'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'

export function useSubscriptionManager() {
  // Data refs
  const subscriptions = ref([])
  const categories = ref([])
  const userPlans = ref([])
  const loading = ref({
    subscriptions: false,
    categories: false,
    userPlans: false
  })
  const toast = useToast()
  
  // Fetch subscriptions
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
  
  // Fetch categories
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
  
  // Fetch user plans
  const fetchUserPlans = async (params = {}) => {
    try {
      loading.value.userPlans = true
      const response = await axios.get('/api/user-plans/', { params: params })
      userPlans.value = response.data
      return response.data
    } catch (error) {
      handleError('Error fetching user plans', error)
    } finally {
      loading.value.userPlans = false
    }
  }
  
  // Delete user plan
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
  
  // Toggle usage tracking
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
  
  // Add plan to user list
  const addToUserPlans = async (planId, paymentDate) => {
    try {
      if (!paymentDate) {
        showToast('error', 'Invalid data', 'Please select a next payment date')
        return false
      }
      
      await axios.post('/api/user-plans/', {
        plan_id: planId,
        payment_date: paymentDate.toISOString().split('T')[0],
      })
      showToast('success', 'Plan added', 'Successfully added to your list')
      await fetchUserPlans()
      return true
    } catch (error) {
      handleError("Couldn't add to list", error)
      return false
    }
  }
  
  // Set budget
  const setBudget = async (budget, categoryId = null) => {
    if (!budget) {
      showToast('error', 'Error', 'Please enter a budget.')
      return null
    }
    
    try {
      const response = await axios.get('/api/analytics/set-budget/', {
        params: {
          budget: budget,
          ...(categoryId && { category_id: categoryId }),
        },
      })
      
      const categoryText = categoryId ? 
        `for ${categories.value.find(c => c.id === categoryId)?.name || 'selected category'}` : 
        ''
      
      showToast('success', 'Budget Applied', `Budget of $${budget} has been set ${categoryText}`)
      return response.data.subscriptions
    } catch (error) {
      handleError('Error setting budget', error)
      return null
    }
  }
  
  // Create new plan
  const createPlan = async (planData) => {
    const { name, cost, period, subscription } = planData
    if (!name || !cost || !period || !subscription) {
      showToast('error', 'Invalid data', 'Please provide all required fields.')
      return false
    }
    
    try {
      await axios.post('/api/plans/', {
        name,
        cost,
        period: period.toLowerCase(),
        subscription: subscription.id,
      })
      showToast('success', 'Success', 'Plan created successfully.')
      await fetchSubscriptions()
      return true
    } catch (error) {
      handleError('Error creating plan', error)
      return false
    }
  }
  
  // Create new subscription
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
  
  // Helper: get category name by id
  const getCategoryName = (categoryId) => {
    const category = categories.value.find((cat) => cat.id === categoryId)
    return category ? category.name : 'Unknown'
  }
  
  // Helper: show toast notifications
  const showToast = (severity, summary, detail) => {
    toast.add({ severity, summary, detail, life: 3000 })
  }
  
  // Helper: handle errors
  const handleError = (message, error) => {
    console.error(message, error)
    showToast('error', 'Error', error.response?.data?.error || message)
  }
  
  // Initialize all data
  const initData = async () => {
    await Promise.all([
      fetchCategories(),
      fetchSubscriptions(),
      fetchUserPlans()
    ])
  }

  return {
    subscriptions,
    categories,
    userPlans,
    loading,
    
    fetchSubscriptions,
    fetchCategories,
    fetchUserPlans,
    deleteUserPlan,
    toggleUsage,
    addToUserPlans,
    setBudget,
    createPlan,
    createSubscription,
    getCategoryName,
    showToast,
    initData
  }
}