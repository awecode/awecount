import { useLoginStore } from 'src/stores/login-info'
import numberToText from '../numToText'
import DateConverter from 'src/components/date/VikramSamvat.js'

export default function useGeneratePosPdf(
  invoiceInfo: object,
  tax_scheme_obj: object | null,
  partyObj: object | null,
  hideRowQuantity: boolean
): string {
  const loginStore: Record<string, string | number | object> = useLoginStore()
  const compayInfo: Record<string, string | number> = loginStore.companyInfo
  let sameTax = null
  const tableRow = (rows: Array<object>): string => {
    let isTaxSame: number | boolean | null = null
    const htmlRows = rows.map(
      (row: Record<string, number | string | object>, index: number) => {
        if (isTaxSame !== false) {
          if (index === 0) isTaxSame = row.tax_scheme_id
          else {
            if (isTaxSame !== row.tax_scheme_id) isTaxSame = false
          }
        }
        return `<tr style="color: grey; font-weight: 400;">
      <th style="width: 20px; padding: 10px 0; font-weight: 400; padding:5px; border-right: LightGrey solid 1px; ${
        index + 1 !== rows.length ? 'border-bottom: LightGrey solid 1px;' : ''
      }">${index + 1}</th>
      <th style="width: 50%; font-weight: 400; text-align:left; padding-left:20px; border-right: LightGrey solid 1px; ${
        index + 1 !== rows.length ? 'border-bottom: LightGrey solid 1px;' : ''
      }">${row.item_name}<br><span style="font-size: 12px; ${
          row.description ? '' : 'display: none;'
        }" class="text-grey-8; padding:5px">(${row.description})</span></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: LightGrey solid 1px; ${
        index + 1 !== rows.length ? 'border-bottom: LightGrey solid 1px;' : ''
      }"><span style="${hideRowQuantity ? 'display: none' : ''}">${
          row.quantity +
          `<span style="font-size:13px; color: gray; margin-left: 2px;">${row.unit_name || ''}</span>`
        }</span></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: LightGrey solid 1px; ${
        index + 1 !== rows.length ? 'border-bottom: LightGrey solid 1px;' : ''
      }"><span style="${hideRowQuantity ? 'display: none' : ''}">${
          row.rate
        }</span></th>
      <th style="text-align: right; font-weight: 400; padding:5px; ${
        index + 1 !== rows.length ? 'border-bottom: LightGrey solid 1px;' : ''
      }">${row.quantity * row.rate}</th>
    </tr>
    `
      }
    )
    sameTax = isTaxSame
    const totalValue = htmlRows.join('')
    return totalValue
  }
  const emptyRows = () => {
    const number = 5 - invoiceInfo.rows.length
    return `<tr style="color: grey; font-weight: 400;">
      <th style="width: 20px; height:${80 * number}px; padding: 10px 0; font-weight: 400; padding:5px; border-right: LightGrey solid 1px;"></th>
      <th style="width: 50%; font-weight: 400; text-align:left; padding-left:20px; border-right: LightGrey solid 1px;"></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: LightGrey solid 1px;"></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: LightGrey solid 1px;"></th>
      <th style="text-align: right; font-weight: 400; padding:5px;"></th>
    </tr>
    `
  }
  let html = ''
  let header = ''
    if (compayInfo.invoice_template === 2) {
      header = `
    <div>
    <div style="display:flex; align-items: center; position: relative; margin-bottom: 10px;">
    <img src="${
      compayInfo.logo_url
    }" alt="Compony Logo" style="height: 60px; max-width: 200px; object-fit: contain; ${
    compayInfo.logo_url ? '' : 'display: none;'
  }"/>
    <h1 style="width: 600px; text-align:center; padding-left: 20px; line-height: normal; margin: 5px 0; font-size: 35px; font-weight: 500;">${
      compayInfo.name
    } ${
        compayInfo.organization_type === 'private_limited'
          ? ' Pvt. Ltd.'
          : ['public_limited', 'corporation'].includes(
              compayInfo.organization_type
            )
          ? 'Ltd.'
          : ''
      }</h1>
    </div>
    <div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif;">
    <div>
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
    </div>
  <hr style="margin: 20px 0" />`
    } else {
      header = `<div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif;">
    <div>
      <h1 style="margin: 5px 0; font-size: 35px; font-weight: 500;">${
        compayInfo.name
      } ${
        compayInfo.organization_type === 'private_limited'
          ? ' Pvt. Ltd.'
          : ['public_limited', 'corporation'].includes(
              compayInfo.organization_type
            )
          ? 'Ltd.'
          : ''
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
        <img src="${
          compayInfo.logo_url
        }" alt="Compony Logo" style="height: 70px; max-width: 200px; object-fit: contain; ${
        compayInfo.logo_url ? '' : 'display: none;'
      }"/>
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
    }

  html = html.concat(header)
  const table = `<div style="margin-top: 20px">
  <table style="width: 100%; font-family: Arial, Helvetica, sans-serif; border: 1px solid LightGrey;">
    <tr style="color: grey; font-weight: 500;">
      <th style="width: 40px; padding:5px; border-right: LightGrey solid 1px; border-bottom: LightGrey solid 1px;">SN</th>
      <th style="width: 40%; text-align:left; padding-left:20px; border-right: LightGrey solid 1px; border-bottom: LightGrey solid 1px;">Particular</th>
      <th style="text-align: left; padding:5px; border-right: LightGrey solid 1px; border-bottom: LightGrey solid 1px;">Qty</th>
      <th style="text-align: left; padding:5px; border-right: LightGrey solid 1px; border-bottom: LightGrey solid 1px;">Rate</th>
      <th style="text-align: right; padding:5px; border-bottom: LightGrey solid 1px;">Amount(${
        compayInfo.config_template === 'np' ? 'NRS' : 'N/A'
      })</th>
    </tr>
    ${invoiceInfo.rows ? tableRow(invoiceInfo.rows) : ''}
    ${compayInfo.invoice_template === 2 ? `${emptyRows()}` : ''}
  </table>
  <div style="display: flex; justify-content: space-between; align-items: center; font-family: Arial, Helvetica, sans-serif; border: 1px solid LightGrey; border-top: none; padding: 20px; padding-top: 0;">
      <div>
      <div style="font-weight: 600; margin-bottom: 10px;">In words:</div>
      <div>${numberToText(invoiceInfo.voucher_meta.grand_total)}</div>
      </div>
      <div style="width: 250px; padding: 10px 0; padding-left: 10px; border-left: 1px solid LightGrey; margin-top: 15px;">
        <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid LightGrey;">
          <span style="font-weight: 600; color: lightgray;">SUB TOTAL</span> <span>${
            invoiceInfo.voucher_meta.sub_total
          }</span>
        </div>
        <div style="display: ${
          invoiceInfo.voucher_meta.discount ? 'flex' : 'none'
        }; justify-content: space-between; margin: 5px 0; border-bottom: 1px solid LightGrey;">
          <span style="font-weight: 600; color: lightgray;">DISCOUNT</span> <span>${
            invoiceInfo.voucher_meta.discount
          }</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid LightGrey;>
          <span style="font-weight: 600; color: lightgray;">${
            sameTax
              ? `${tax_scheme_obj.name} ` + `${tax_scheme_obj.rate} %`
              : 'TAX'
          }</span> <span>${invoiceInfo.meta_tax}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px 0">
          <span style="font-weight: 600; color: gray;">GRAND TOTAL</span> <span>${
            invoiceInfo.voucher_meta.grand_total
          }</span>
        </div>
      </div>
  </div>
  <div style="margin-top: 20px">
  </div>
  </div>
  `
  const body = `<div style="margin-top: 20px; margin-bottom: 20px">
  <div
    style="
      display: flex;
      align-items: center;
      gap: 11px;
      flex-direction: column;
      font-family: Arial, Helvetica, sans-serif;
    "
  >
  <h4 style="margin: 0; font-size: 1.4rem">${
    (invoiceInfo.status === 'Issued' || invoiceInfo.status === 'Paid')
      ? 'TAX INVOICE'
      : invoiceInfo.status === 'Draft'
      ? 'PRO FORMA INVOICE'
      : ''
  }</h4>
  </div>
  <div style="display: flex; justify-content: space-between">
    <div style="display: flex; flex-direction: column; gap: 2px;">
      <div style="font-weight: 600; color: grey;">Billed To:</div>
      <div>${partyObj ? partyObj.name : (invoiceInfo.customer_name || '')}</div>
      <div>${partyObj && partyObj.address ? partyObj.address : ''}</div>
  ${
    invoiceInfo.tax_registration_number
      ? `<div style="font-weight: 600; color: grey;">Tax reg. No. ${invoiceInfo.tax_registration_number}</div>`
      : ''
  }
    </div>
    <div style="display: flex; flex-direction: column; gap: 2px; text-align: right;">
      <div>
      <span><span style="font-weight: 600; color: grey;">INV No.: </span></span>${loginStore.companyInfo.current_fiscal_year}- <span style="font-weight: 700;">${
        invoiceInfo.voucher_no
      }</span>
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Date: </span></span> ${
        invoiceInfo.date
      }
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Miti: </span></span> ${DateConverter.getRepresentation(
        invoiceInfo.date,
        'bs'
      )}
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Mode: </span></span> ${
        invoiceInfo.mode
      } ${
    invoiceInfo.status === 'Draft'
      ? '(Draft)'
      : invoiceInfo.status === 'Paid'
      ? '(Paid)'
      : ''
  }
      </div>
    </div>
  </div>
</div>
${table}
<div style="font-size: 14px; text-align: right">
    <div style="margin-bottom: 5px">
      Generated by ${loginStore.username} for ${loginStore.companyInfo.name} ${
        loginStore.companyInfo.organization_type === 'private_limited'
          ? 'Private Limited'
          : ''
      }
    </div>
    <div>
      This is a computer generated invoice, produced using awecount.com - IRD
      Approval No. 7600405
    </div>
  </div>
`
  return html.concat(body)
}
