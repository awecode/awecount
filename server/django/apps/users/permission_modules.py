def get_default_permissions_from_model(model_name):
    return [model_name + 'View', model_name + 'Create', model_name + 'Modify', model_name + 'Delete']


gdp = get_default_permissions_from_model

MODULES = [
    # aggregated
    'Dashboard',
    'LogEntryView',
    # Product
    *gdp('Item'),
    *gdp('Unit'),
    *gdp('Brand'),
    *gdp('InventoryAccount'),
    *gdp('InventoryCategory'),
    *gdp('Book'),
    # Ledger
    *gdp('Category'),
    *gdp('Party'),
    *gdp('Account'),
    # Tax
    *gdp('TaxScheme'),
    # Voucher
    *gdp('Sales'), 'SalesIssuedModify', 'SalesCancel',
    *gdp('PurchaseVoucher'),
    *gdp('CreditNote'), 'CreditNoteIssuedModify', 'CreditNoteCancel',
    *gdp('DebitNote'), 'DebitNoteIssuedModify', 'DebitNoteCancel',
    *gdp('SalesDiscount'),
    *gdp('PurchaseDiscount'),
    *gdp('JournalVoucher'),
    *gdp('InvoiceDesign'),
    # Bank
    *gdp('BankAccount'),
    *gdp('BankBranch'),
    *gdp('ChequeIssue'),
    *gdp('ChequeDeposit'),
    *gdp('SalesAgent'),
    *gdp('Widget'),
    *gdp('TaxPayment'),
    *gdp('PurchaseSetting'),
    *gdp('SalesSetting'),
    *gdp('PaymentReceipt'),
    *gdp('TransactionCharge'),
    *gdp('AccountOpeningBalance'),
]

MODULES.sort()
module_pairs = [(module, module) for module in MODULES]
