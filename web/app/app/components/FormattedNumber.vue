<script setup lang="ts">
import { useLoginStore } from '@/stores/login-info'

import Decimal from 'decimal.js'
import { computed } from 'vue'

type FormatType = 'decimal' | 'currency' | 'unit' | 'percent'
type UnitDisplay = 'short' | 'long' | 'narrow'

const {
  value,
  type = 'decimal',
  locale = 'en-US',
  currency,
  unit = 'kilobyte',
  unitDisplay = 'short',
  nullValue = '-',
  zeroValue,
} = defineProps<{
  value: number | string | Decimal | null
  type?: FormatType
  locale?: string
  currency?: string
  unit?: string
  unitDisplay?: UnitDisplay
  nullValue?: string
  zeroValue?: string
}>()

const store = useLoginStore()

const formatted = computed(() => {
  if ((value === null || value === undefined) && nullValue) {
    return nullValue
  }

  const _value = typeof value === 'number' ? value : new Decimal(value as string | Decimal).toNumber()

  if (_value === 0 && zeroValue) {
    return zeroValue
  }

  let _locale = locale

  const options: Intl.NumberFormatOptions = {
    style: type,
    signDisplay: 'never',
  }

  if (type === 'currency') {
    options.currency = currency || store.companyInfo.currency_code
    options.currencySign = 'accounting'
    options.currencyDisplay = 'narrowSymbol'
    if (options.currency === 'NPR' || options.currency === 'INR') {
      _locale = 'en-IN' // only en-IN has lakhs and crores separators
    }
  } else if (type === 'unit') {
    options.unit = unit
    options.unitDisplay = unitDisplay
  }

  const formattedValue = new Intl.NumberFormat(_locale, options).format(_value)

  // Add brackets for negative values for decimal and unit types
  if (_value < 0) {
    return `(${formattedValue})`
  }

  return formattedValue
})
</script>

<template>
  <span>{{ formatted }}</span>
</template>
