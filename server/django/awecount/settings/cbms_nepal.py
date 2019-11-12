CBMS_NEPAL = {
    'TEST':
        {
            'base_url': 'http://103.1.92.174:9050/',
            'sales_invoice_endpoint': 'api/bill',
            'credit_note_endpoint': 'api/billreturn',
            'username': 'Test_CBMS',
            'password': 'test@321',
            'data': {
                'seller_pan': '999999999',
                'buyer_pan': '123456789',
                'buyer_name': '',
                'fiscal_year': '2073.074',

                'total_sales': 1130,
                'taxable_sales_vat': 1000,
                'vat': 130,
                'excisable_amount': 0,
                'excise': 0,
                'taxable_sales_hst': 0,
                'hst': 0,
                'amount_for_esf': 0,
                'esf': 0,
                'export_sales': 0,
                'tax_exempted_sales': 0,
            },
            'sales_invoice_data': {
                'invoice_number': 'sajhydawe78e4',
                'invoice_date': '2074.07.06',
            },
            'credit_note_data': {
                'ref_invoice_number': 'sajhydawe78e4',
                'credit_note_number': 'utyijd9pwe',
                'credit_note_date': '2074.07.06',
                'reason_for_return': 'defect in piece',
            }
        },
    'LIVE':
        {
            'base_url': 'http://103.1.92.174:9050/',
            'sales_invoice_endpoint': 'api/bill',
            'credit_note_endpoint': 'api/billreturn',
            'username': 'Test_CBMS',
            'password': 'test@321',
            'data': {
                'fiscal_year': '2075.076',
                'excisable_amount': 0,
                'excise': 0,
                'taxable_sales_hst': 0,
                'hst': 0,
                'amount_for_esf': 0,
                'esf': 0,
            },
            'sales_invoice_data': {
            },
            'credit_note_data': {
            }
        }
}
