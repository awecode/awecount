type VoucherType = 'salesVoucher' | 'creditNote'
import { useLoginStore } from 'src/stores/login-info'
import numberToText from '../numToText'
const loginStore: Record<string, string | number | object> = useLoginStore()
const compayInfo: Record<string, string | number> = loginStore.companyInfo

export default function useGeneratePdf(
  voucherType: VoucherType,
  onlyBody: boolean,
  invoiceInfo: object
): string {
  let sameTax = null
  const tableRow = (rows: Array<object>): string => {
    let isTaxSame: number | boolean | null = null
    const htmlRows = rows.map(
      (row: Record<string, number | string | object>, index: number) => {
        // debugger
        // console.log(row, 'ahvsyvas row')
        if (isTaxSame !== false) {
          if (index === 0) isTaxSame = row.tax_scheme.id
          else {
            if (isTaxSame !== row.tax_scheme.id) isTaxSame = false
          }
        }
        return `<tr style="color: grey; font-weight: 400;">
      <th style="width: 20px; padding: 10px 0; font-weight: 400;">${
        index + 1
      }</th>
      <th style="width: 50%; font-weight: 400;">${row.item_name}</th>
      <th style="text-align: right; font-weight: 400;">${row.quantity}</th>
      <th style="text-align: right; font-weight: 400;">${row.rate}</th>
      <th style="text-align: right; font-weight: 400;">${
        row.quantity * row.rate
      }</th>
    </tr>
    `
      }
    )
    sameTax = isTaxSame
    return htmlRows.join('')
  }
  let html = ''
  if (!onlyBody) {
    const header = `<div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif;">
    <div>
      <h1 style="margin: 5px 0">${compayInfo.name} ${
      compayInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.' : 'Ltd.'
    }</h1>
      <div>${compayInfo.address}</div>
      <div>Tax Reg. No. <strong>${
        compayInfo.tax_registration_number
      }</strong></div>
    </div>

    <div
      style="
        display: flex;
        flex-direction: column;
        gap: 5px;
        align-items: flex-end;
      "
    >
      <div style="margin-bottom: 5px;">
        <img src="/img/awecount.png" alt="Compony Logo" style="height: 70px" />
      </div>
      <div style="display: flex; align-items: center">
        <img
          src="/icons/telephone-fill.svg"
          alt="Email"
          style="margin-right: 10px; width: 14px"
        />
        <span style="color: skyblue">${compayInfo.contact_no}</span>
      </div>
      <div style="display: flex; align-items: center">
        <img
          src="/icons/envelope-fill.svg"
          alt="Call"
          style="margin-right: 10px; width: 14px"
        /><span style="color: skyblue">${compayInfo.email}</span>
      </div>
    </div>
  </div>
  <hr style="margin: 20px 0" />`
    html = html.concat(header)
  }
  const table = `<div>
  <table style="width: 100%; font-family: Arial, Helvetica, sans-serif;">
    <tr style="color: grey; font-weight: 500;">
      <th style="width: 20px;">SN</th>
      <th style="width: 50%;">Particular</th>
      <th style="text-align: right;">Qty</th>
      <th style="text-align: right;">Rate</th>
      <th style="text-align: right;">Amount(${
        compayInfo.config_template === 'np' ? 'NRS' : 'N/A'
      })</th>

    </tr>
    ${invoiceInfo.rows ? tableRow(invoiceInfo.rows) : ''}
  </table>
  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-family: Arial, Helvetica, sans-serif;">
      <div>
      ${
        voucherType === 'creditNote'
          ? ''
          : `<div style="font-weight: 600; margin-bottom: 10px;">In words:</div>
      <div>${numberToText(invoiceInfo.total_amount)}</div>`
      }
      </div>
      <div style="border-top: 1px solid lightgrey; width: 250px; padding: 10px 0">
        <div style="display: flex; justify-content: space-between; margin: 15px 0">
          <span style="font-weight: 600; color: lightgray;">SUB TOTAL</span> <span>${
            invoiceInfo.voucher_meta.sub_total
          }</span>
        </div>
        <div style="display: ${
          invoiceInfo.voucher_meta.discount ? 'flex' : 'none'
        }; justify-content: space-between; margin: 15px 0">
          <span style="font-weight: 600; color: lightgray;">DISCOUNT</span> <span>${
            invoiceInfo.voucher_meta.discount
          }</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 15px 0">
          <span style="font-weight: 600; color: lightgray;">${
            sameTax
              ? `${invoiceInfo.rows[0].tax_scheme.name} ` +
                `${invoiceInfo.rows[0].tax_scheme.rate} %`
              : 'TAX'
          }</span> <span>${invoiceInfo.meta_tax}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 15px 0">
          <span style="font-weight: 600; color: gray;">GRAND TOTAL</span> <span>${
            invoiceInfo.voucher_meta.grand_total
          }</span>
        </div>
      </div>
  </div>
  ${
    voucherType === 'creditNote'
      ? `<div style="font-weight: 600; margin-bottom: 10px; font-family: Arial, Helvetica, sans-serif;">In words: ${numberToText(
          invoiceInfo.total_amount
        )}</div> <div style="margin: 20px 0;"><span style="font-weight: 600;">Remarks:</span> ${
          invoiceInfo.remarks
        }</div>`
      : ''
  }
  </div>
  <hr style="border: 0.5px solid lightgrey; height: 0; margin: 20px 0;">
  `
  let body = ''
  if (voucherType === 'salesVoucher') {
    body = `<div style="${onlyBody ? 'margin-top: 80px;' : ''}">
  <div
    style="
      display: flex;
      align-items: center;
      gap: 11px;
      flex-direction: column;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
    <h4 style="margin: 0; font-size: 1.4rem">TAX INVOICE</h4>
    <span>COPY ${invoiceInfo.print_count} OF ORIGINAL (PRINT COUNT:${
      invoiceInfo.print_count + 1
    })</span>
  </div>
  <div style="display: flex; justify-content: space-between">
    <div style="display: flex; flex-direction: column; gap: 2px;">
      <div style="font-weight: 600; color: grey;">Billed To:</div>
      <div>${
        invoiceInfo.party ? invoiceInfo.party : invoiceInfo.customer_name
      }</div>
      <div style="${invoiceInfo.address ? '' : 'display: none;'}">${
      invoiceInfo.address
    }</div>
      <div style="font-weight: 600; color: grey;">Tax reg. No.</div>
    </div>
    <div style="display: flex; flex-direction: column; gap: 2px; text-align: right;">
      <div>
      <span><span style="font-weight: 600; color: grey;">INV No.: </span></span> ${
        invoiceInfo.voucher_no
      }
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Date: </span></span> ${
        invoiceInfo.date
      }
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Miti: </span></span> ${'miti'}
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Mode: </span></span> ${
        invoiceInfo.mode
      }
      </div>
    </div>
  </div>
</div>
<hr style="border: 0.5px solid lightgrey; height: 0; margin: 20px 0;">
${table}
<div style="font-size: 14px; text-align: right;">
  <div style="margin-bottom: 5px">
    Generated by ${loginStore.username} for Test Company Pvt. Ltd
  </div>
  ${
    onlyBody
      ? ''
      : `<div>
  This is a computer generated invoice, produced using awecount.com - IRD Approval No. 7600405
  </div>`
  }
</div>
`
  } else if (voucherType === 'creditNote') {
    body = `<div style="font-family: Arial, Helvetica, sans-serif; ${
      onlyBody ? 'margin-top: 80px;' : ''
    }
    "
  >
    <div
      style="
        display: flex;
        align-items: center;
        gap: 11px;
        flex-direction: column;
        font-family: Arial, Helvetica, sans-serif;
      "
    >
      <h4 style="margin: 0; font-size: 1.4rem">Credit Note</h4>
      <span>Copy of Original (${invoiceInfo.print_count + 1})</span>
    </div>
    <div>
      <div style="display: flex; flex-direction: column; gap: 5px">
        <div><span style="font-weight: 600; color: dimgray;">Credit Note No:</span>  (${
          invoiceInfo.status
        })</div>
        <div style="${
          invoiceInfo.party_name ? '' : 'display: none;'
        }"><span style="font-weight: 600; color: dimgray;">Party:</span> ${
      invoiceInfo.party_name
    }</div>
        <div style="${
          invoiceInfo.status ? '' : 'display: none;'
        }"><span style="font-weight: 600; color: dimgray;">Customer:</span> ${
      invoiceInfo.status
    }</div>
        <div><span style="font-weight: 600; color: dimgray;">Date:</span> 2023-03-03</div>
        <div style="font-weight: 600">Ref. Invoice No.: #${
          invoiceInfo.voucher_no
        }</div>
      </div>
    </div>
  </div>
  <hr style="border: 0.5px solid lightgrey; height: 0; margin: 20px 0" />
  ${table}
  <div style="font-size: 14px; text-align: right">
    <div style="margin-bottom: 5px">
      Generated by ${loginStore.username} for Test Company Pvt. Ltd
    </div>
    ${
      onlyBody
        ? ''
        : `
    <div>
      This is a computer generated invoice, produced using awecount.com - IRD
      Approval No. 7600405
    </div>
    `
    }
  </div>
  <style>
    table {
      tr {
        border-bottom: 1px solid #ddd;
      }
    }
  </style>
`
  }
  return html.concat(body)
}
