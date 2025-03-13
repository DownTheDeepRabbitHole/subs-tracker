import { useHelpers } from "./useHelpers"

export function useValidateForms() {
  const MAX_INPUT = 50

  const { showToast } = useHelpers()

  const validatePlan = (plan) => {
    if (!plan.name?.trim() || !plan.period?.trim() || !plan.subscription) {
      showToast(
        'error',
        'Validation Error',
        'Missing required fields. Fill out name, period, or subscription.',
      )
      return false
    }
    if (plan.name.length > MAX_INPUT) {
      showToast('error', 'Validation Error', 'Plan name is too long')
      return false
    }
    if (plan.cost < 0) {
      showToast('error', 'Validation Error', 'Plan cost must be greater than zero')
      return false
    }
    return true
  }

  const validateUserPlan = (userPlan) => {
    if (!userPlan.paymentDate) {
      showToast('error', 'Validation Error', 'Payment date is required')
      return false
    }
    if (userPlan.paymentDate && isNaN(Date.parse(userPlan.paymentDate))) {
      showToast('error', 'Validation Error', 'Payment date is invalid')
      return false
    }
    if (typeof userPlan.trackUsage !== 'boolean') {
      showToast('error', 'Validation Error', 'Track uage field must be a boolean value')
      return false
    }
    return true
  }

  const validateSubscription = (subscription) => {
    if (!subscription.name || !subscription.category) {
      showToast(
        'error',
        'Validation Error',
        'Missing required fields. Fill out subscription name or category.',
      )
      return false
    }
    if (subscription.category === null || subscription.category === undefined) {
      showToast('error', 'Validation Error', 'Subscription category is required')
      return false
    }
    return true
  }

  return {
    validatePlan,
    validateUserPlan,
    validateSubscription,
  }
}
