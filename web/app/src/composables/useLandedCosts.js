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
    NPR: '1.6015',
  },
  NPR: {
    USD: '0.0075',
    INR: '0.62',
  },
}

export const LANDED_COST_TYPES = [
  'Tax on Purchase',
  'Freight',
  'Customs Valuation Uplift',
  'Duty',
  'Labor',
  'Insurance',
  'Brokerage',
  'Storage',
  'Packaging',
  'Loading',
  'Unloading',
  'Regulatory Fee',
  'Customs Declaration',
  'Other Charges',
]
// Available currencies
const AVAILABLE_CURRENCIES = ['USD', 'INR', 'NPR']

export const useLandedCosts = (fields, { roundUp }) => {
  if (!fields.value.landed_cost_rows) {
    fields.value.landed_cost_rows = []
  }
  if (!fields.value.rows) {
    fields.value.rows = []
  }
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

  const roundUpIfNeeded = (amount) => {
    return roundUp.value ? amount.ceil() : amount
  }

  const invoiceTotal = computed(() => {
    const total = fields.value.rows.reduce((sum, row) =>
      sum.add(new Decimal(row.rate || '0').mul(row.quantity || '0')), new Decimal('0'))
    return roundUpIfNeeded(total)
  })

  // Function to update landed cost row amount and cascade updates
  const updateLandedCostRow = (index) => {
    if (!fields.value.landed_cost_rows[index]) return

    const row = fields.value.landed_cost_rows[index]

    if (row.is_percentage && row.value) {
      // Calculate base amount including invoice total and previous landed costs
      let baseAmount = invoiceTotal.value

      // Add amounts from previous landed cost rows
      if (row.type !== 'Tax on Purchase') {
        for (let i = 0; i < index; i++) {
          const prevRow = fields.value.landed_cost_rows[i]
          if (prevRow.amount && prevRow.type !== 'Tax on Purchase') {
            baseAmount = baseAmount.add(new Decimal(prevRow.amount))
          }
        }
      }

      // Calculate percentage amount based on total base amount
      const newAmount = baseAmount.mul(row.value).div('100')
      fields.value.landed_cost_rows[index] = { ...row, amount: roundUpIfNeeded(newAmount) }
    } else if (row.value) {
      // For fixed amounts, convert to target currency if needed
      const newAmount = convertCurrency(row.value, row.currency, loginStore.companyInfo.currency_code || 'USD')
      fields.value.landed_cost_rows[index] = { ...row, amount: roundUpIfNeeded(newAmount) }
    }

    // Update subsequent rows if they are percentages
    for (let i = index + 1; i < fields.value.landed_cost_rows.length; i++) {
      const subsequentRow = fields.value.landed_cost_rows[i]
      if (subsequentRow.is_percentage && subsequentRow.value && subsequentRow.type !== 'Tax on Purchase') {
        let baseAmount = invoiceTotal.value

        // Add amounts from all previous rows
        for (let j = 0; j < i; j++) {
          const prevRow = fields.value.landed_cost_rows[j]
          if (prevRow.amount && prevRow.type !== 'Tax on Purchase') {
            baseAmount = baseAmount.add(new Decimal(prevRow.amount))
          }
        }

        const newAmount = baseAmount.mul(subsequentRow.value).div('100')
        fields.value.landed_cost_rows[i] = { ...subsequentRow, amount: roundUpIfNeeded(newAmount) }
      }
    }
  }

  // Watch for changes in invoice rows
  watch(
    () => fields.value.rows,
    () => {
      if (!fields.value.landed_cost_rows.length) return

      const updatedLandedCostRows = fields.value.landed_cost_rows.map((row, index) => {
        if (row.is_percentage && row.value) {
          let baseAmount = invoiceTotal.value

          if (row.type !== 'Tax on Purchase') {
          // Add amounts from previous landed cost rows
            for (let i = 0; i < index; i++) {
              const prevRow = fields.value.landed_cost_rows[i]
              if (prevRow.amount && prevRow.type !== 'Tax on Purchase') {
                baseAmount = baseAmount.add(new Decimal(prevRow.amount))
              }
            }
          }

          const newAmount = baseAmount.mul(row.value).div('100')
          return { ...row, amount: roundUpIfNeeded(newAmount) }
        } else if (row.value) {
          const newAmount = convertCurrency(row.value, row.currency, loginStore.companyInfo.currency_code || 'USD')
          return { ...row, amount: roundUpIfNeeded(newAmount) }
        }
        return row
      })

      fields.value.landed_cost_rows = updatedLandedCostRows
    },
    { deep: true },
  )

  // Watch for initial data to copy amount to value
  watch(
    () => fields.value.landed_cost_rows,
    (newRows) => {
      if (newRows.length) {
        const updatedRows = newRows.map((row) => {
          return {
            ...row,
            currency: row.currency || loginStore.companyInfo.currency_code || 'USD',
          }
        })
        if (JSON.stringify(updatedRows) !== JSON.stringify(newRows)) {
          fields.value.landed_cost_rows = updatedRows
        }
        showLandedCosts.value = true
      }
    },
    { once: true },
  )

  // TODO Only set presets for non-default values, ie. is_percentage:true
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
    if (fields.value.landed_cost_rows) {
      fields.value.landed_cost_rows = [...fields.value.landed_cost_rows, newRow]
    } else {
      fields.value.landed_cost_rows = [newRow]
    }
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
    if (!fields.value.rows || !fields.value.landed_cost_rows.length) return 0

    // Calculate landed costs total
    const totalLandedCosts = fields.value.landed_cost_rows.reduce((sum, row) => {
      return sum.add(row.amount)
    }, new Decimal('0'))

    const totalQuantity = fields.value.rows.reduce((sum, row) =>
      sum.add(new Decimal(row.quantity || '0')), new Decimal('0'))

    return invoiceTotal.value.add(totalLandedCosts).div(totalQuantity).toNumber()
  })

  const duty = computed(() => {
    const includedTypes = ['Duty']
    return fields.value.landed_cost_rows.reduce((sum, row) => {
      if (includedTypes.includes(row.type)) {
        return sum.add(row.amount)
      }
      return sum
    }, new Decimal('0'))
  })

  const taxOnPurchase = computed(() => {
    const total = fields.value.landed_cost_rows.reduce((sum, row) => {
      if (row.type === 'Tax on Purchase' && row.amount) {
        return sum.add(new Decimal(row.amount))
      }
      return sum
    }, new Decimal('0'))
    return roundUpIfNeeded(total)
  })

  const taxBeforeDeclaration = computed(() => {
    // Calculate taxes for all rows above customs declaration, except tax on purchase which will be added separately
    let declarationFound = false
    const taxesExceptPurchaseBeforeDeclaration = fields.value.landed_cost_rows.reduce((sum, row) => {
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
    return roundUpIfNeeded(taxesExceptPurchaseBeforeDeclaration.add(taxOnPurchase.value))
  })

  const taxOnDeclaration = computed(() => {
    const includedTypes = ['Customs Declaration']
    const total = fields.value.landed_cost_rows.reduce((sum, row) => {
      if (includedTypes.includes(row.type) && row.tax_scheme && row.tax_scheme.rate) {
        const rowAmount = new Decimal(row.amount)
        const taxAmount = rowAmount.mul(row.tax_scheme.rate).div('100')
        return sum.add(taxAmount)
      }
      return sum
    }, new Decimal('0'))
    return roundUpIfNeeded(total)
  })

  const declarationFees = computed(() => {
    const includedTypes = ['Customs Declaration']
    const total = fields.value.landed_cost_rows.reduce((sum, row) => {
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
    return roundUpIfNeeded(total)
  })

  const totalOnDeclaration = computed(() => {
    return duty.value.add(taxBeforeDeclaration.value).add(declarationFees.value)
  })

  const totalTax = computed(() => {
    const total = fields.value.landed_cost_rows.reduce((sum, row) => {
      return sum.add(getRowTaxAmount(row))
    }, new Decimal('0'))
    return roundUpIfNeeded(total)
  })

  const totalAdditionalCost = computed(() => {
    const total = fields.value.landed_cost_rows.reduce((sum, row) => {
      if (!['Tax on Purchase', 'Customs Valuation Uplift'].includes(row.type)) {
        return sum.add(row.amount)
      }
      return sum
    }, new Decimal('0')).add(totalTax.value)
    return roundUpIfNeeded(total)
  })

  // Watch dependencies and update row.updated_cost_price
  watch(
    [() => fields.value.rows, () => totalAdditionalCost.value, () => totalTax.value, () => invoiceTotal.value],
    () => {
      if (!fields.value.rows || !fields.value.landed_cost_rows.length) return

      fields.value.rows.forEach((row) => {
        const rowRate = new Decimal(row.rate || '0')
        const rowAmount = rowRate.mul(row.quantity || '1')
        const additionalCost = totalAdditionalCost.value.sub(totalTax.value).div(invoiceTotal.value).mul(rowAmount).div(row.quantity || '1')
        const totalCost = rowRate.add(additionalCost)
        row.updated_cost_price = totalCost.toNumber()
      })
    },
    { deep: true },
  )

  const averageRatePerItem = computed(() => {
    if (!fields.value.rows) return []
    return fields.value.rows.map((row) => {
      const rowRate = new Decimal(row.rate || '0')
      const additionalCost = new Decimal(row.updated_cost_price || '0').sub(rowRate)
      return {
        ...row,
        additionalCost,
        totalCost: new Decimal(row.updated_cost_price || '0'),
      }
    })
  }, {
    deep: true,
  })

  const removeLandedCostRow = (index) => {
    fields.value.landed_cost_rows = fields.value.landed_cost_rows.filter((_, i) => i !== index)
  }

  return {
    showLandedCosts,
    LANDED_COST_TYPES,
    landedCostColumns,
    AVAILABLE_CURRENCIES,
    addLandedCostRow,
    handleTypeChange,
    removeLandedCostRow,
    updateLandedCostRow,
    averageRate,
    duty,
    taxBeforeDeclaration,
    declarationFees,
    totalOnDeclaration,
    totalTax,
    averageRatePerItem,
    totalAdditionalCost,
    taxOnDeclaration,
  }
}
