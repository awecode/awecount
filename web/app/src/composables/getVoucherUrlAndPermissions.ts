
function getVoucherUrl(row: {
  source_type: string
  source_id: string | number
}) {
  if (!row.source_id) return ''
  const source_type = row.source_type
  if (source_type === 'Sales Voucher')
    return `/sales-voucher/${row.source_id}/view/`
  if (source_type === 'Purchase Voucher')
    return `/purchase-voucher/${row.source_id}/view`
  if (source_type === 'Journal Voucher')
    return `/journal-voucher/${row.source_id}/view`
  if (source_type === 'Credit Note')
    return `/credit-note/${row.source_id}/view`
  if (source_type === 'Debit Note')
    return `/debit-note/${row.source_id}/view`
  // if (source_type === 'Tax Payment') return 'Tax Payment Edit'
  // TODO: add missing links
  if (source_type === 'Cheque Deposit')
    return `/cheque-deposit/${row.source_id}/view/`
  if (source_type === 'Payment Receipt')
    return `/payment-receipt/${row.source_id}/view/`
  if (source_type === 'Cheque Issue')
    return `/cheque-issue/${row.source_id}/`
  if (source_type === 'Challan') return `/challan/${row.source_id}/`
  if (source_type === 'Account Opening Balance')
    return `/account-opening-balance/${row.source_id}/`
  if (source_type === 'Item') return `/items/details/${row.source_id}/`
  // added
  if (source_type === 'Fund Transfer')
    return `/fund-transfer/${row.source_id}/`
  if (source_type === 'Bank Cash Deposit')
    return `/bank/cash/cash-deposit/${row.source_id}/edit/`
  if (source_type === 'Tax Payment') return `/tax-payment/${row.source_id}/`
  if (source_type === 'Inventory Adjustment Voucher') return `/items/inventory-adjustment/${row.source_id}/view/`
  console.error(source_type + ' not handled!')
}
const getPermissionsWithSourceType = {
  'Sales Voucher': 'SalesView',
  'Purchase Voucher': 'PurchaseVoucherView',
  'Journal Voucher': 'JournalVoucherView',
  'Credit Note': 'CreditNoteView',
  'Debit Note': 'DebitNoteView',
  'Cheque Deposit': 'ChequeDepositView',
  'Payment Receipt': 'PaymentReceiptView',
  'Cheque Issue': 'ChequeIssueModify',
  'Challan': 'ChallanModify',
  'Account Opening Balance': 'AccountOpeningBalanceModify',
  'Fund Transfer': 'FundTransferModify',
  'Bank Cash Deposit': 'BankCashDepositModify',
  'Tax Payment': 'TaxPaymentModify',
  'Item': 'ItemView',
  'Inventory Adjustment Voucher': 'InventoryAdjustmentVoucherView'
} as const

const getPermissionFromSourceType = (sourceType: string) => {
  return getPermissionsWithSourceType[sourceType as keyof typeof getPermissionsWithSourceType]
}



export { getVoucherUrl, getPermissionFromSourceType, getPermissionsWithSourceType }
