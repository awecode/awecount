# Partner Journal Voucher API

### Fields:

- `date`, `narration`, `status`: string (default = "Approved")
- `voucher_no`: integer (default = "autoincrement")
- `rows`: `JournalVoucherRow[]`

### Journal Voucher Rows:

- `type`: "Cr" | "Dr"
- `amount`: decimal
- `account_id`: int?
- `account`: `Record<AccountKwargs>`

### AccountKwargs Examples:

- `{id: 1}`
- `{code: 'CASH'}`
- `{name: 'Cash Account'}`
- `{supplier_detail__tax_identification_number: '601855494'}` \
  Finds supplier account for Party with TRN 601855494.
- `{customer_detail__tax_identification_number: '601855494'}`

### Whitelisted Fields:

- `id`, `code`, `*name*`, `parent_id`, `parent__id`, `parent__code`, `parent__name`, `category_id`, `category__id`, `*category__name*`, `category__code`
- `supplier_detail__name`, `supplier_detail__email`, `supplier_detail__contact_no`, `supplier_detail__tax_identification_number`
- `customer_detail__name`, `customer_detail__email`, `customer_detail__contact_no`, `customer_detail__tax_identification_number`
