import { useRoute } from 'vue-router'

function getVoucherUrl(row: { source_type: string, source_id: string | number }) {
  const route = useRoute()

  const source_type = row.source_type
  if (source_type === 'Sales Voucher') {
    return `/${route.params.company}/sales/vouchers/${row.source_id}`
  }
  if (source_type === 'Purchase Voucher') {
    return `/${route.params.company}/purchase/vouchers/${row.source_id}`
  }
  if (source_type === 'Journal Voucher') {
    return `/${route.params.company}/account/journal-vouchers/${row.source_id}`
  }
  if (source_type === 'Credit Note') {
    return `/${route.params.company}/sales/credit-notes/${row.source_id}`
  }
  if (source_type === 'Debit Note') {
    return `/${route.params.company}/purchase/debit-notes/${row.source_id}`
  }
  if (source_type === 'Challan') {
    return `/${route.params.company}/sales/challans/${row.source_id}`
  }
  if (source_type === 'Cheque Deposit') {
    return `/${route.params.company}/banking/cheque-deposit/${row.source_id}`
  }
  if (source_type === 'Payment Receipt') {
    return `/${route.params.company}/payment-receipts/${row.source_id}`
  }
  if (source_type === 'Cheque Issue') {
    return `/${route.params.company}/banking/cheque-issue/${row.source_id}/edit`
  }
  if (source_type === 'Account Opening Balance') {
    return `/${route.params.company}/account/opening-balances/${row.source_id}/edit`
  }
  if (source_type === 'Fund Transfer') {
    return `/${route.params.company}/banking/fund-transfers/${row.source_id}/edit`
  }
  if (source_type === 'Bank Cash Deposit') {
    return `/${route.params.company}/banking/cash-deposit/${row.source_id}/edit`
  }
  if (source_type === 'Tax Payment') {
    return `/${route.params.company}/tax/payments/${row.source_id}/edit`
  }
  if (source_type === 'Inventory Adjustment Voucher') {
    return `/${route.params.company}/inventory/adjustments/${row.source_id}`
  }
  console.error(`${source_type} not handled!`)
}

const getPermissionsWithSourceType = {
  'Account Opening Balance': 'accountopeningbalance.modify',
  'Bank Cash Deposit': 'bankcashdeposit.modify',
  'Challan': 'challan.modify',
  'Cheque Deposit': 'chequedeposit.view',
  'Cheque Issue': 'chequeissue.modify',
  'Credit Note': 'creditnote.view',
  'Debit Note': 'debitnote.view',
  'Fund Transfer': 'fundtransfer.modify',
  'Inventory Adjustment Voucher': 'inventoryadjustmentvoucher.view',
  'Item': 'item.view',
  'Journal Voucher': 'journalvoucher.view',
  'Payment Receipt': 'paymentreceipt.view',
  'Purchase Voucher': 'purchasevoucher.view',
  'Sales Voucher': 'sales.view',
  'Tax Payment': 'taxpayment.modify',
} as const

const getPermissionFromSourceType = (sourceType: string) => {
  return getPermissionsWithSourceType[sourceType as keyof typeof getPermissionsWithSourceType]
}

export { getPermissionFromSourceType, getPermissionsWithSourceType, getVoucherUrl }
