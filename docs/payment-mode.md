# Payment Mode

- Vouchers like Sales (and Credit Note) and Purchase (and Debit Note) have a payment mode field.

- Payment Mode is a model.
- Fields:
  - `name`: Name of the payment mode.
  - `enable_for_sales`: Whether the payment mode is enabled for sales. Defaults to `True`.
  - `enable_for_purchase`: Whether the payment mode is enabled for purchase. Defaults to `True`.
  - `account`: The account to be used for the payment mode. This account will be used to record the journal entry for the payment mode. For sales, it will be debited and for purchase, it will be credited.
  - `transaction_fee`: In percentage, the transaction fee for the payment mode. Defaults to `0`.
  - `transaction_fee_account`: The account to be used for the transaction fee. This account will be used to record the journal entry for the transaction fee. It will always be debited.


- Transaction fees can be fixed percentage or fixed amount.
- Transaction fee can either be in percentage or fixed amount, whichever is higher.
- Transaction fee can either be in percentage or fixed amount, whichever is lower.
- Transaction fee can be in percentage for different ranges.
- Transaction fee can be in fixed amount for different ranges.
