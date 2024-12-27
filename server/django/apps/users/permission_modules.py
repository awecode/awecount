def get_default_permissions_from_model(model_name):
    return [
        model_name + "View",
        model_name + "Create",
        model_name + "Modify",
        model_name + "Delete",
    ]


gdp = get_default_permissions_from_model

MODULES = [
    # aggregated
    "Dashboard",
    "LogEntryView",
    # Product
    *gdp("Item"),
    *gdp("Unit"),
    *gdp("Brand"),
    *gdp("InventoryAccount"),
    *gdp("InventoryCategory"),
    *gdp("Book"),
    *gdp("BillOfMaterial"),
    # Ledger
    *gdp("Category"),
    *gdp("Party"),
    *gdp("Account"),
    *gdp("AccountClosing"),
    # Tax
    *gdp("TaxScheme"),
    # Voucher
    *gdp("Sales"),
    "SalesIssuedModify",
    "SalesCancel",
    *gdp("PurchaseVoucher"),
    "PurchaseVoucherCancel",
    *gdp("CreditNote"),
    "CreditNoteIssuedModify",
    "CreditNoteCancel",
    *gdp("DebitNote"),
    "DebitNoteIssuedModify",
    "DebitNoteCancel",
    *gdp("SalesDiscount"),
    *gdp("PurchaseDiscount"),
    *gdp("JournalVoucher"),
    "JournalVoucherCancel",
    *gdp("Challan"),
    *gdp("InvoiceDesign"),
    *gdp("PurchaseOrder"),
    "PurchaseOrderCancel",
    *gdp("InventoryConversionVoucher"),
    *gdp("InventoryAdjustmentVoucher"),

    # Bank
    *gdp("BankAccount"),
    *gdp("BankBranch"),
    *gdp("ChequeIssue"),
    "ChequeIssueCancel",
    *gdp("FundTransfer"),
    "FundTransferCancel",
    *gdp("ChequeDeposit"),
    "ChequeDepositCancel",
    *gdp("BankCashDeposit"),
    "BankCashDepositCancel",
    *gdp("SalesAgent"),
    *gdp("Widget"),
    *gdp("TaxPayment"),
    "TaxPaymentCancel",
    *gdp("PurchaseSetting"),
    *gdp("SalesSetting"),
    *gdp("InventorySetting"),
    *gdp("PaymentReceipt"),
    "PaymentReceiptCancel",
    *gdp("TransactionCharge"),
    *gdp("AccountOpeningBalance"),
    *gdp("Transaction"),
    *gdp("PaymentMode"),
]

MODULES.sort()
module_pairs = [(module, module) for module in MODULES]
