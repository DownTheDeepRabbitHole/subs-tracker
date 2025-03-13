import { useToast } from 'primevue/usetoast'
import { formatDistanceToNow } from 'date-fns'

export function useHelpers() {
  const toast = useToast()

  const showToast = (severity, summary, detail) => {
    toast.add({ severity, summary, detail, life: 3000 })
  }

  const handleError = (message, error) => {
    console.error(message, error)
    showToast('error', 'Error', error.response?.data?.error || message)
  }

  const formatDate = (date) => {
    // Source: https://stackoverflow.com/questions/67969651/regex-to-check-the-format-yyyy-mm-ddthhmmss-000-javascript
    if (typeof date === 'string' && date.match(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z/)) {
      return date // Checks if it's already in isoFormat
    }
    if (date instanceof Date) {
      return date.toISOString().split('T')[0]
    }
    return date
  }

  const formatCurrency = (value) => {
    if (isNaN(value)) return ''
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(Number(value))
  }

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`
  }

  const formatPaymentDate = (date) => {
    return formatDistanceToNow(new Date(date), { addSuffix: true })
  }

  return {
    formatCurrency,
    formatPercentage,
    showToast,
    handleError,
    formatDate,
    formatPaymentDate,
  }
}
