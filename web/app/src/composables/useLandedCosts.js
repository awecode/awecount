import { ref, computed, watch } from 'vue'
import Decimal from 'decimal.js'
import { useLoginStore } from 'src/stores/login-info'

// Currency conversion matrix for USD, INR, and NPR
const EXCHANGE_RATES = {
  USD: {
    INR: '83.12',
    NPR: '135.76',
  },
  INR: {
    USD: '0.012',
    NPR: '1.60',
  },
  NPR: {
    USD: '0.0075',
    INR: '0.62',
  },
}

// Available currencies
const AVAILABLE_CURRENCIES = ['USD', 'INR', 'NPR']

// Utility function to convert currency
const convertCurrency = (amount, fromCurrency, toCurrency) => {
  if (!amount) return new Decimal(0)

  amount = new Decimal(amount)

  if (fromCurrency === toCurrency) return amount

  // Get exchange rate
  const rate = new Decimal(EXCHANGE_RATES[fromCurrency]?.[toCurrency] || '0')
  if (!rate) {
    console.warn(`Exchange rate not found for ${fromCurrency} to ${toCurrency}`)
    return amount
  }

  return amount.mul(rate)
}

export const useLandedCosts = (fields) => {
  const loginStore = useLoginStore()
  const showLandedCosts = ref(false)

  // Initialize landed costs if not present
  watch(
    () => fields.value,
    (newFields) => {
      if (newFields && !newFields.landed_cost_rows) {
        newFields.landed_cost_rows = []
      }
    },
    { immediate: true }
  )

  const landedCostTypes = [
    { label: 'Tax on Purchase', value: 'Tax on Purchase' },
    { label: 'Freight', value: 'Freight' },
    { label: 'Customs Valuation Uplift', value: 'Customs Valuation Uplift' },
    { label: 'Duty', value: 'Duty' },
    { label: 'Labor', value: 'Labor' },
    { label: 'Insurance', value: 'Insurance' },
    { label: 'Brokerage', value: 'Brokerage' },
    { label: 'Storage', value: 'Storage' },
    { label: 'Packaging', value: 'Packaging' },
    { label: 'Loading', value: 'Loading' },
    { label: 'Unloading', value: 'Unloading' },
    { label: 'Regulatory Fee', value: 'Regulatory Fee' },
    { label: 'Customs Declaration', value: 'Customs Declaration' },
    { label: 'Other Charges', value: 'Other Charges' },
  ]

  // Presets for landed cost types
  const LANDED_COST_PRESETS = {
    'Duty': {
      is_percentage: true,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Freight': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Brokerage': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Insurance': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Storage': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Labor': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Regulatory Fee': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Customs Declaration': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Packaging': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Loading': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Unloading': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
    'Other Charges': {
      is_percentage: false,
      default_currency: loginStore.companyInfo.currency_code || 'USD',
    },
  }

  const landedCostColumns = [
    {
      name: 'type',
      label: 'Cost Type',
      field: 'type',
      align: 'left',
      sortable: true,
      style: 'width: 150px',
    },
    {
      name: 'is_percentage',
      label: 'Amount Type',
      field: 'is_percentage',
      align: 'center',
      style: 'width: 120px',
    },
    {
      name: 'currency',
      label: 'Currency',
      field: 'currency',
      align: 'center',
      style: 'width: 100px',
    },
    {
      name: 'amount',
      label: 'Amount',
      field: 'amount',
      align: 'right',
      sortable: true,
      style: 'width: 200px',
    },
    {
      name: 'tax_scheme',
      label: 'Tax Scheme',
      field: 'tax_scheme',
      align: 'left',
      style: 'width: 150px',
    },
    {
      name: 'credit_account',
      label: 'Credit Account',
      field: 'credit_account',
      align: 'left',
      style: 'width: 150px',
    },
    {
      name: 'actions',
      label: 'Actions',
      field: 'actions',
      align: 'center',
      style: 'width: 80px',
    },
  ]

  const addLandedCostRow = () => {
    if (!fields.value.landed_cost_rows) {
      fields.value.landed_cost_rows = []
    }
    fields.value.landed_cost_rows.push({
      type: '',
      value: 0,
      amount: 0,
      description: '',
      is_percentage: false,
      currency: loginStore.companyInfo.currency_code || 'USD',
      tax_scheme: null,
      credit_account: null,
    })
  }

  // Handle type selection to apply presets
  const handleTypeChange = (row) => {
    if (row.type && LANDED_COST_PRESETS[row.type]) {
      const preset = LANDED_COST_PRESETS[row.type]
      row.is_percentage = preset.is_percentage
      row.currency = preset.default_currency
    }
  }

  // Function to convert percentage amounts to fixed amounts based on invoice total
  const convertPercentagesToFixedAmounts = () => {
    if (!fields.value.landed_cost_rows) return

    // Calculate invoice total (sum of all row amounts)
    const invoiceTotal = fields.value.rows?.reduce((sum, row) => sum.add(new Decimal(row.rate || '0').mul(row.quantity || '0')), new Decimal('0')) || new Decimal('0')

    const targetCurrency = loginStore.companyInfo.currency_code || 'USD'

    fields.value.landed_cost_rows.forEach((row, index) => {
      if (row.is_percentage && row.value) {
        // Calculate base amount including invoice total and previous landed costs
        let baseAmount = invoiceTotal

        // Add amounts from previous landed cost rows
        for (let i = 0; i < index; i++) {
          const prevRow = fields.value.landed_cost_rows[i]
          if (prevRow.amount) {
            baseAmount = baseAmount.add(prevRow.amount)
          }
        }

        // Calculate percentage amount based on total base amount
        row.amount = baseAmount.mul(row.value).div('100')
      } else {
        // For fixed amounts, convert to target currency if needed
        row.amount = convertCurrency(row.value, row.currency, targetCurrency)
      }
    })
  }

  const averageRate = computed(() => {
    if (!fields.value.rows || !fields.value.landed_cost_rows) return 0
    const totalAmount = fields.value.rows.reduce((sum, row) => sum.add(new Decimal(row.rate || '0').mul(row.quantity || '0')), new Decimal('0'))
    const totalLandedCosts = fields.value.landed_cost_rows.reduce((sum, row) => sum.add(row.amount || '0'), new Decimal('0'))
    const totalQuantity = fields.value.rows.reduce((sum, row) => sum.add(row.quantity || '0'), new Decimal('0'))
    return totalAmount.add(totalLandedCosts).div(totalQuantity).toNumber()
  })

  const duty = computed(() => {
    const includedTypes = ['Duty']
    return fields.value.landed_cost_rows.reduce((sum, row) => {
      if (includedTypes.includes(row.type)) {
        return sum.add(new Decimal(row.value || '0'))
      }
      return sum
    }, new Decimal('0'))
  })

  const taxBeforeDeclaration = computed(() => {
    const includedTypes = ['Tax on Purchase']
    return fields.value.landed_cost_rows.reduce((sum, row) => {
      if (includedTypes.includes(row.type)) {
        return sum.add(new Decimal(row.value || '0'))
      }
      return sum
    }, new Decimal('0'))
  })

  const declarationFees = computed(() => {
    const includedTypes = ['Customs Declaration']
    return fields.value.landed_cost_rows.reduce((sum, row) => {
      if (includedTypes.includes(row.type)) {
        return sum.add(new Decimal(row.total_amount || '0'))
      }
      return sum
    }, new Decimal('0'))
  })

  const totalOnDeclaration = computed(() => {
    return duty.value.add(taxBeforeDeclaration.value).add(declarationFees.value)
  })

  const totalTax = computed(() => {
    return fields.value.landed_cost_rows.reduce((sum, row) => {
      return sum.add(new Decimal(row.tax_amount || '0'))
    }, new Decimal('0'))
  })

  // Watch for initial data to copy amount to value
  watch(
    () => fields.value.landed_cost_rows,
    (newRows) => {
      if (newRows?.length) {
        newRows.forEach((row) => {
          if (row.amount && !row.value) {
            row.value = row.amount
            row.is_percentage = false
            row.currency = loginStore.companyInfo.currency_code || 'USD'
          }
        })
        showLandedCosts.value = true
      }
    },
    { immediate: true },
  )

  // Watch for changes in rows to update fixed amounts
  watch(
    () => fields.value.rows,
    () => {
      // Only update if there are landed cost rows with percentage values
      if (fields.value.landed_cost_rows?.some(row => row.is_percentage && row.value)) {
        convertPercentagesToFixedAmounts()
      }
    },
    { deep: true },
  )

  // Watch for changes in landed cost rows to update fixed amounts
  watch(
    () => fields.value.landed_cost_rows?.map(row => ({
      is_percentage: row.is_percentage,
      value: row.value,
      currency: row.currency,
    })),
    () => {
      convertPercentagesToFixedAmounts()
    },
    { deep: true },
  )

  const removeLandedCostRow = (index) => {
    fields.value.landed_cost_rows.splice(index, 1)
  }

  return {
    showLandedCosts,
    landedCostTypes,
    landedCostColumns,
    AVAILABLE_CURRENCIES,
    addLandedCostRow,
    handleTypeChange,
    removeLandedCostRow,
    averageRate,
    duty,
    taxBeforeDeclaration,
    declarationFees,
    totalOnDeclaration,
    totalTax,
  }
} 