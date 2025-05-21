import Decimal from 'decimal.js'
import { useLoginStore } from 'src/stores/login-info'
import { computed, ref, watch } from 'vue'

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

export const useLandedCosts = (fields) => {
  const loginStore = useLoginStore()
  const showLandedCosts = ref(false)

  // Utility function to convert currency
  const convertCurrency = (amount, fromCurrency, toCurrency) => {
    if (!amount) return new Decimal(0)

    if (!fromCurrency) {
      fromCurrency = loginStore.companyInfo.currency_code || 'USD'
    }

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

  // Create a reactive reference to landed_cost_rows
  const landedCostRows = computed({
    get: () => fields.value?.landed_cost_rows || [],
    set: (value) => {
      if (fields.value) {
        fields.value.landed_cost_rows = value
      }
    },
  })

  const invoiceTotal = computed(() => {
    return fields.value.rows.reduce((sum, row) =>
      sum.add(new Decimal(row.rate || '0').mul(row.quantity || '0')), new Decimal('0'))
  })

  // TODO Refactor, make DRY

  // Watch for changes in individual row values
  watch(
    () => landedCostRows.value.map(row => ({
      value: row.value,
      is_percentage: row.is_percentage,
      currency: row.currency,
      type: row.type,
    })),
    (newRows, oldRows) => {
      if (!newRows || !oldRows) return

      // Find which row changed
      const changedIndex = newRows.findIndex((row, index) =>
        JSON.stringify(row) !== JSON.stringify(oldRows[index]),
      )

      if (changedIndex === -1) return

      const changedRow = landedCostRows.value[changedIndex]
      const updatedRows = [...landedCostRows.value]

      if (changedRow.is_percentage && changedRow.value) {
        // Calculate base amount including invoice total and previous landed costs
        let baseAmount = invoiceTotal.value

        // Add amounts from previous landed cost rows
        if (changedRow.type !== 'Tax on Purchase') {
          for (let i = 0; i < changedIndex; i++) {
            const prevRow = updatedRows[i]
            if (prevRow.amount && prevRow.type !== 'Tax on Purchase') {
              baseAmount = baseAmount.add(new Decimal(prevRow.amount))
            }
          }
        }

        // Calculate percentage amount based on total base amount
        const newAmount = baseAmount.mul(changedRow.value).div('100')
        updatedRows[changedIndex] = { ...changedRow, amount: newAmount }
      } else if (changedRow.value) {
        // For fixed amounts, convert to target currency if needed
        const newAmount = convertCurrency(changedRow.value, changedRow.currency, loginStore.companyInfo.currency_code || 'USD')
        updatedRows[changedIndex] = { ...changedRow, amount: newAmount }
      }

      // Update subsequent rows if they are percentages
      for (let i = changedIndex + 1; i < updatedRows.length; i++) {
        const row = updatedRows[i]
        if (row.is_percentage && row.value && row.type !== 'Tax on Purchase') {
          let baseAmount = invoiceTotal.value

          // Add amounts from all previous rows
          for (let j = 0; j < i; j++) {
            const prevRow = updatedRows[j]
            if (prevRow.amount && prevRow.type !== 'Tax on Purchase') {
              baseAmount = baseAmount.add(new Decimal(prevRow.amount))
            }
          }

          const newAmount = baseAmount.mul(row.value).div('100')
          updatedRows[i] = { ...row, amount: newAmount }
        }
      }

      fields.value.landed_cost_rows = updatedRows
    },
    { deep: true },
  )

  // Watch for changes in invoice rows
  watch(
    () => fields.value.rows,
    () => {
      if (!landedCostRows.value.length) return

      const updatedRows = landedCostRows.value.map((row, index) => {
        if (row.is_percentage && row.value) {
          let baseAmount = invoiceTotal.value

          // Add amounts from previous landed cost rows
          for (let i = 0; i < index; i++) {
            const prevRow = landedCostRows.value[i]
            if (prevRow.amount && prevRow.type !== 'Tax on Purchase') {
              baseAmount = baseAmount.add(new Decimal(prevRow.amount))
            }
          }

          const newAmount = baseAmount.mul(row.value).div('100')
          return { ...row, amount: newAmount }
        } else if (row.value) {
          const newAmount = convertCurrency(row.value, row.currency, loginStore.companyInfo.currency_code || 'USD')
          return { ...row, amount: newAmount }
        }
        return row
      })

      fields.value.landed_cost_rows = updatedRows
    },
    { deep: true },
  )

  // Watch for initial data to copy amount to value
  watch(
    () => fields.value?.landed_cost_rows,
    (newRows) => {
      if (newRows?.length) {
        const updatedRows = newRows.map((row) => {
          return {
            ...row,
            currency: loginStore.companyInfo.currency_code || 'USD',
          }
        })
        if (JSON.stringify(updatedRows) !== JSON.stringify(newRows)) {
          fields.value.landed_cost_rows = updatedRows
        }
        showLandedCosts.value = true
      }
    },
    { immediate: true },
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
    'Tax on Purchase': {
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
    const newRow = {
      type: '',
      value: 0,
      amount: 0,
      description: '',
      is_percentage: false,
      currency: loginStore.companyInfo.currency_code || 'USD',
      tax_scheme: null,
      credit_account: null,
    }
    landedCostRows.value = [...landedCostRows.value, newRow]
  }

  // Handle type selection to apply presets
  const handleTypeChange = (row) => {
    if (row.type && LANDED_COST_PRESETS[row.type]) {
      const preset = LANDED_COST_PRESETS[row.type]
      row.is_percentage = preset.is_percentage
      row.currency = preset.default_currency
    }
  }

  const getRowTaxAmount = (row) => {
    if (row.type === 'Tax on Purchase') {
      return row.amount
    } else if (row.tax_scheme && row.tax_scheme.rate) {
      const rowAmount = new Decimal(row.amount)
      return rowAmount.mul(row.tax_scheme.rate).div('100')
    }
    return new Decimal('0')
  }

  const averageRate = computed(() => {
    if (!fields.value.rows || !landedCostRows.value.length) return 0

    // Calculate landed costs total
    const totalLandedCosts = landedCostRows.value.reduce((sum, row) => {
      return sum.add(row.amount)
    }, new Decimal('0'))

    const totalQuantity = fields.value.rows.reduce((sum, row) =>
      sum.add(new Decimal(row.quantity || '0')), new Decimal('0'))

    return invoiceTotal.value.add(totalLandedCosts).div(totalQuantity).toNumber()
  })

  const duty = computed(() => {
    const includedTypes = ['Duty']
    return landedCostRows.value.reduce((sum, row) => {
      if (includedTypes.includes(row.type)) {
        return sum.add(row.amount)
      }
      return sum
    }, new Decimal('0'))
  })

  const taxOnPurchase = computed(() => {
    return landedCostRows.value.reduce((sum, row) => {
      if (row.type === 'Tax on Purchase' && row.amount) {
        return sum.add(new Decimal(row.amount))
      }
      return sum
    }, new Decimal('0'))
  })

  const taxBeforeDeclaration = computed(() => {
    // Calculate taxes for all rows above customs declaration, except tax on purchase which will be added separately
    let declarationFound = false
    const taxesExceptPurchaseBeforeDeclaration = landedCostRows.value.reduce((sum, row) => {
      if (row.type === 'Customs Declaration') {
        declarationFound = true
        return sum
      }

      if (declarationFound) {
        return sum
      }

      // For Tax on Purchase rows, skip because they will be added differently
      if (row.type === 'Tax on Purchase' && row.amount) {
        return sum
      }

      // For other rows, compute tax if they have a tax scheme
      if (row.tax_scheme?.rate && row.value) {
        const rowAmount = convertCurrency(row.amount, row.currency, loginStore.companyInfo.currency_code || 'USD')
        const taxAmount = rowAmount.mul(row.tax_scheme.rate).div('100')
        return sum.add(taxAmount)
      }

      return sum
    }, new Decimal('0'))
    return taxesExceptPurchaseBeforeDeclaration.add(taxOnPurchase.value)
  })

  const declarationFees = computed(() => {
    const includedTypes = ['Customs Declaration']
    return landedCostRows.value.reduce((sum, row) => {
      if (includedTypes.includes(row.type)) {
        let rowAmount = new Decimal(row.amount)
        // Add tax if present
        if (row.tax_scheme && row.tax_scheme.rate) {
          const taxAmount = rowAmount.mul(row.tax_scheme.rate).div('100')
          rowAmount = rowAmount.add(taxAmount)
        }
        return sum.add(rowAmount)
      }
      return sum
    }, new Decimal('0'))
  })

  const totalOnDeclaration = computed(() => {
    return duty.value.add(taxBeforeDeclaration.value).add(declarationFees.value)
  })

  const totalTax = computed(() => {
    return landedCostRows.value.reduce((sum, row) => {
      return sum.add(getRowTaxAmount(row))
    }, new Decimal('0'))
  })

  const removeLandedCostRow = (index) => {
    landedCostRows.value = landedCostRows.value.filter((_, i) => i !== index)
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
    landedCostRows,
  }
}
