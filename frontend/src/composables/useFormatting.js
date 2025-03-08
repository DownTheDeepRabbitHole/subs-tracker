export function useFormatting() {
  function formatCurrency(value) {
    if (isNaN(value)) return ''
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(Number(value))
  }

  function formatPercentage(value) {
    return `${value.toFixed(1)}%`
  }

  return {
    formatCurrency,
    formatPercentage,
  }
}
