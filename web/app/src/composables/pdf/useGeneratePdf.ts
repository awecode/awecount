import DateConverter from 'src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
import numberToText from '../numToText'

type VoucherType = 'salesVoucher' | 'creditNote' | 'debitNote'

export default function useGeneratePdf(voucherType: VoucherType, onlyBody: boolean, invoiceInfo: object, hideRowQuantity: boolean, companyInfo?: Record<string, string | number>, template?: number): string {
  const loginStore = useLoginStore()
  if (!companyInfo) {
    companyInfo = loginStore.companyInfo || {}
  }
  const invoice_template = template || companyInfo.invoice_template
  let sameTax = null
  let taxIndex: number | null = null
  const formatRowDescription = (str: string) => {
    const dataArray = str.split('\n')
    const htmlArray = dataArray.map(data => `<div>${data}</div>`)
    return htmlArray.join(' ')
  }
  const tableRow = (rows: Array<object>): string => {
    let isTaxSame: number | boolean | null = null
    const htmlRows = rows.map((row: Record<string, number | string | object>, index: number) => {
      if (isTaxSame !== false && row.tax_scheme.rate != 0) {
        if (isTaxSame === null) {
          isTaxSame = row.tax_scheme.id
          taxIndex = index
        } else {
          if (isTaxSame !== row.tax_scheme.id) isTaxSame = false
        }
      }
      return `<tr style="color: grey; font-weight: 400;">
      <th style="width: 20px; padding: 10px 0; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;">${index + 1}</th>
      <th style="width: 20px; padding: 10px 0; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;">${row.hs_code ?? ''}  </th>
      <th style="width: 50%; font-weight: 400; text-align:left; padding-left:20px; border-right: #b9b9b9 solid 2px;">${row.item_name}<br><div style="font-size: 12px; ${row.description ? '' : 'display: none;'}" class="text-grey-8; padding:5px">${row.description ? formatRowDescription(row.description) : ''}</div></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;"><span style="${hideRowQuantity ? 'display: none' : ''}">${`${row.quantity}<span style="font-size:13px; color: gray; margin-left: 2px;">${row.unit_name}</span>`}</span></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;"><span style="${hideRowQuantity ? 'display: none' : ''}">${$nf(row.rate)}</span></th>
      <th style="text-align: right; font-weight: 400; padding:5px;">${formatNumberWithComma(row.quantity * row.rate)}</th>
    </tr>
    `
    })
    sameTax = isTaxSame
    return htmlRows.join('')
  }
  const emptyRows = () => {
    const number = 5 - invoiceInfo.rows.length
    return `<tr style="color: grey; font-weight: 400;">
      <th style="width: 20px; height:${80 * number}px; padding: 10px 0; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;"></th>
      <th style="padding: 10px 0; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;"></th>
      <th style="width: 50%; font-weight: 400; text-align:left; padding-left:20px; border-right: #b9b9b9 solid 2px;"></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;"></th>
      <th style="text-align: left; font-weight: 400; padding:5px; border-right: #b9b9b9 solid 2px;"></th>
      <th style="text-align: right; font-weight: 400; padding:5px;"></th>
    </tr>
    `
  }
  let html = ''
  if (!onlyBody) {
    let header = ''
    if ([2, 3].includes(invoice_template)) {
      header = `
    <div>
    <div style="position: relative; margin-bottom: 10px;">
    <img src="${companyInfo.logo_url}" alt="Compony Logo" style="height: 110px; object-fit: contain; max-width:160px; position: absolute; ${companyInfo.logo_url ? '' : 'display: none;'} ${invoice_template == 3 ? 'left: 40px;' : ''}" />
  <div style="text-align:center; padding-left: 10px;">
    <h1 style="line-height: normal; margin: 5px 0; font-size: 35px; font-weight: 700;">${companyInfo.name} ${
      companyInfo.organization_type === 'private_limited'
        ? ' Pvt. Ltd.'
        : ['public_limited', 'corporation'].includes(companyInfo.organization_type)
            ? 'Ltd.'
            : ''
    }</h1>
      <div>${companyInfo.address}</div>
      <div style="font-size: 14px;">
          <div style="display: flex; justify-content: center; flex-direction: column;">
          <div style="display: flex; align-items: center; justify-content: center;">
          <span>Email: ${companyInfo.emails && companyInfo.emails.length ? companyInfo.emails.join(',&nbsp;') : ''}</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: center;">
          <span>Tel: ${companyInfo.contact_no}</span>
        </div>
      </div>
      </div>
  </div>
    </div>
    <div style="display: flex; justify-content: end; font-family: Arial, Helvetica, sans-serif;">
    <div
      style="
        display: flex;
        flex-direction: column;
        gap: 3px;
        align-items: flex-end;
      "
    >
      <div style="font-size: 14px;" >VAT No. <strong>${companyInfo.tax_identification_number}</strong></div>
      <div style="display: ${companyInfo.website ? 'flex' : 'none'}; align-items: center">
        <img
          src="/icons/web-fill.svg"
          alt="Website"
          style="margin-right: 10px; width: 14px"
        /><span style="color: skyblue">${companyInfo.website}</span>
      </div>
    </div>
  </div>
    </div>

  <hr style="margin: 20px 0" />`
    } else {
      header = `<div style="display: flex; justify-content: space-between; font-family: Arial, Helvetica, sans-serif;">
    <div>
      <h1 style="margin: 5px 0; font-size: 35px; font-weight: 700;">${companyInfo.name} ${
        companyInfo.organization_type === 'private_limited'
          ? ' Pvt. Ltd.'
          : ['public_limited', 'corporation'].includes(companyInfo.organization_type)
              ? 'Ltd.'
              : ''
      }</h1>
      <div>${companyInfo.address}</div>
      <div>Tax Reg. No. <strong>${companyInfo.tax_identification_number}</strong></div>
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
        <img src="${companyInfo.logo_url}" alt="Compony Logo" style="height: 70px; max-width: 200px; object-fit: contain; ${companyInfo.logo_url ? '' : 'display: none;'}"/>
      </div>
      <div style="display: flex; align-items: center">
        <img
          src="/icons/telephone-fill.svg"
          alt="Email"
          style="margin-right: 10px; width: 14px"
        />
        <span style="color: skyblue">${companyInfo.contact_no}</span>
      </div>
      <div style="display: flex; align-items: center">
        <img
          src="/icons/envelope-fill.svg"
          alt="Call"
          style="margin-right: 10px; width: 14px"
        /><span style="color: skyblue">${companyInfo.emails && companyInfo.emails.length ? companyInfo.emails.join(',&nbsp;') : ''}</span>
      </div>
    </div>
  </div>
  <hr style="margin: 20px 0" />`
    }
    html = html.concat(header)
  }
  const table = `<div>
  <table style="width: 100%; font-family: Arial, Helvetica, sans-serif; border: 2px solid #b9b9b9;">
    <tr style="color: grey; font-weight: 500;">
    <th style="width: 40px; padding:5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">SN</th>
    <th style="white-space: nowrap; padding:5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">H.S. Code</th>
      <th style="width: 40%; text-align:left; padding-left:20px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">Particular</th>
      <th style="text-align: left; padding:5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">Qty</th>
      <th style="text-align: left; padding:5px; border-right: #b9b9b9 solid 2px; border-bottom: #b9b9b9 solid 2px;">Rate</th>
      <th style="text-align: right; padding:5px; border-bottom: #b9b9b9 solid 2px;">Amount(${companyInfo.config_template === 'np' ? 'NRS' : 'N/A'})</th>

    </tr>
    ${invoiceInfo.rows ? tableRow(invoiceInfo.rows) : ''}
    ${[2, 3].includes(invoice_template) ? `${emptyRows()}` : ''}
  </table>
  <div style="display: flex; justify-content: space-between; align-items: center; font-family: Arial, Helvetica, sans-serif; border: 2px solid #b9b9b9; border-top: none; padding: 20px; padding-top: 0;">
      <div>
      ${
        voucherType === 'creditNote' || voucherType === 'debitNote'
          ? ''
          : `<div style="font-weight: 600; margin-bottom: 10px;">In words:</div>
      <div>${numberToText(invoiceInfo.voucher_meta.grand_total)}</div>`
      }
      </div>
      <div style="width: 250px; padding: 10px 0; padding-left: 10px; border-left: 2px solid #b9b9b9; margin-top: 15px;">
        <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 2px solid #b9b9b9;">
          <span style="font-weight: 600; color: lightgray;">SUB TOTAL</span> <span>${formatNumberWithComma(invoiceInfo.voucher_meta.sub_total)}</span>
        </div>
        <div style="display: ${invoiceInfo.voucher_meta.discount ? 'flex' : 'none'}; justify-content: space-between; margin: 5px 0; border-bottom: 2px solid #b9b9b9;">
          <span style="font-weight: 600; color: lightgray;">DISCOUNT</span> <span>${formatNumberWithComma(invoiceInfo.voucher_meta.discount)}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 2px solid #b9b9b9;">
          <span style="font-weight: 600; color: lightgray;">${
            sameTax
              ? [2, 3].includes(invoice_template)
                  ? `${invoiceInfo.rows[taxIndex].tax_scheme.rate} % ` + `${invoiceInfo.rows[taxIndex].tax_scheme.name}`
                  : `${invoiceInfo.rows[taxIndex].tax_scheme.name} ` + `${invoiceInfo.rows[taxIndex].tax_scheme.rate} %`
              : 'TAX'
          }</span> <span>${formatNumberWithComma(invoiceInfo.voucher_meta.tax)}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 5px 0">
          <span style="font-weight: 600; color: gray;">GRAND TOTAL</span> <span>${formatNumberWithComma(invoiceInfo.voucher_meta.grand_total)}</span>
        </div>
      </div>
  </div>
  ${voucherType === 'creditNote' || voucherType === 'debitNote' ? `<div style="font-weight: 600; margin-bottom: 10px; font-family: Arial, Helvetica, sans-serif;">In words: ${numberToText(invoiceInfo.total_amount)}</div> <div style="margin: 20px 0;"><span style="font-weight: 600;">Remarks:</span> ${invoiceInfo.remarks}</div>` : ''}
  </div>
  <div style="margin-top: 20px">
  </div>
  `
  let body = ''
  if (voucherType === 'salesVoucher') {
    body = `<div style="${onlyBody ? 'margin-top: 80px; margin-bottom: 20px' : 'margin-top: 20px; margin-bottom: 20px'}">
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
      invoiceInfo.status === 'Issued' || invoiceInfo.status === 'Paid' || invoiceInfo.status === 'Partially Paid'
        ? 'TAX INVOICE'
        : invoiceInfo.status === 'Draft'
          ? 'PRO FORMA INVOICE'
          : invoiceInfo.status === 'Cancelled'
            ? 'TAX INVOICE (CANCELLED)'
            : ''
    }</h4>
  </div>
  <div style="text-align:center; ${invoiceInfo.print_count > 1 && ['Issued', 'Paid', 'Partially Paid'].includes(invoiceInfo.status) ? '' : 'display: none'}">
    COPY ${invoiceInfo.print_count - 1} OF ORIGINAL (PRINT COUNT:${invoiceInfo.print_count})
  </div>
  <div style="display: flex; justify-content: space-between">
    <div style="display: flex; flex-direction: column; gap: 2px;">
      <div style="font-weight: 600; color: grey;">Billed To:</div>
      <div>${invoiceInfo.party ? invoiceInfo.customer_name || invoiceInfo.party_name : invoiceInfo.customer_name || ''}</div>
      <div style="${invoiceInfo.address ? '' : 'display: none;'}">${invoiceInfo.address}</div>
    <div style="${[2, 3].includes(invoice_template) && invoiceInfo.party_contact_no ? '' : 'display: none;'}">${invoiceInfo.party_contact_no}</div>
      ${invoiceInfo.tax_identification_number ? `<div style="font-weight: 600; color: grey;">Tax reg. No. ${invoiceInfo.tax_identification_number}</div>` : ''}
    </div>
    <div style="display: flex; flex-direction: column; gap: 2px; text-align: right;">
      <div style="${invoiceInfo.voucher_no ? '' : 'display: none;'}">
      <span><span style="font-weight: 600; color: grey;">INV No.: </span></span>  ${invoiceInfo.fiscal_year}-<span style="font-weight: bold;">${invoiceInfo.voucher_no}
      </span>
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Date: </span></span> ${invoiceInfo.date}
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Miti: </span></span> ${DateConverter.getRepresentation(invoiceInfo.date, 'bs')}
      </div>
      <div>
      <span><span style="font-weight: 600; color: grey;">Mode: </span></span> ${invoiceInfo.mode} ${
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
<div style="font-size: 14px; text-align: right;">
<div style="margin-bottom: 20px; text-align: left; ${invoiceInfo.invoice_footer_text ? '' : 'display: none;'}">${invoiceInfo.invoice_footer_text}
</div>
  <div style="margin-bottom: 5px">
    Generated by ${loginStore.username || 'system'} for ${companyInfo.name} ${companyInfo.organization_type === 'private_limited' ? 'Private Limited' : ''}.
  </div>
  ${
    onlyBody
      ? ''
      : (
          `<div>
  This is a computer generated invoice, produced using awecount.com - IRD Approval No. 7600405
  </div>`
        )
  }
</div>
`
  } else if (voucherType === 'creditNote' || 'debitNote') {
    body = `<div style="font-family: Arial, Helvetica, sans-serif; ${onlyBody ? 'margin-top: 80px;' : ''}
    "
  >
    <div
      style="
        display: flex;
        align-items: center;
        gap: 11px;
        flex-direction: column;
        font-family: Arial, Helvetica, sans-serif;
        margin-bottom: 15px;
      "
    >
      <h4 style="margin: 0; font-size: 1.4rem">${voucherType === 'creditNote' ? 'Credit Note' : 'Debit Note'}</h4>
      <span style="text-align:center; font-size: 1rem; ${invoiceInfo.print_count > 1 && ['Issued', 'Paid', 'Partially Paid'].includes(invoiceInfo.status) ? '' : 'display: none'}">
        COPY ${invoiceInfo.print_count - 1} OF ORIGINAL (PRINT COUNT:${invoiceInfo.print_count})
        </span>


    </div>
    <div style="display: flex; justify-content: space-between;">
      <div style="display: flex; flex-direction: column; gap: 5px">
        <div><span style="font-weight: 600; color: dimgray;">${voucherType === 'creditNote' ? 'Credit Note No:' : 'Debit Note No:'}</span>  ${invoiceInfo.voucher_no || '-'}</div>
            <div style="${invoiceInfo.party_name ? '' : 'display: none;'}"><span style="font-weight: 600; color: dimgray;">Party:</span> ${invoiceInfo.party_name}
        </div>
        <div style="${invoiceInfo.customer_name ? '' : 'display: none;'}"><span style="font-weight: 600; color: dimgray;">Customer:</span> ${invoiceInfo.customer_name}
        </div>
        <div style="${invoiceInfo.address ? '' : 'display: none;'}"><span style="font-weight: 600; color: dimgray;">Address:</span> ${invoiceInfo.address}
        </div>
            <div style="${invoiceInfo.customer_name ? '' : 'display: none;'}"><span style="font-weight: 600; color: dimgray;">Customer:</span> ${invoiceInfo.customer_name}</div>
        <div style="${invoiceInfo?.tax_identification_number ? '' : 'display: none;'}"><span style="font-weight: 600; color: dimgray;">Tax Reg.:</span> ${invoiceInfo.tax_identification_number || '-'}</div>
        <div style="font-weight: 600">Ref. Invoice No.: # ${invoiceInfo?.invoice_data?.length > 0 ? invoiceInfo.invoice_data[0]?.voucher_no : '-'}</div>
    </div>
      <div>
      <div><span style="font-weight: 600; color: dimgray;">Date:</span> ${invoiceInfo.date}</div>
      </div>
    </div>
  </div>
  <hr style="border: 0.5px solid #b9b9b9; height: 0; margin: 20px 0" />
  ${table}
  <div style="font-size: 14px; text-align: right">
    <div style="margin-bottom: 5px">
      Generated by ${loginStore.username || 'system'} for ${companyInfo.name} ${companyInfo.organization_type === 'private_limited' ? 'Private Limited' : ''}
    </div>
    ${
      onlyBody
        ? ''
        : (
            `
    <div>
      This is a computer generated invoice, produced using awecount.com - IRD
      Approval No. 7600405
    </div>
    `
          )
    }
  </div>
`
  }
  return html.concat(body)
}
