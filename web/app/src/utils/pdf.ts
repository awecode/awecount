import DateConverter from 'src/components/date/VikramSamvat.js'
import numberToText from 'src/composables/numToText'
import { useLoginStore } from 'src/stores/login-info'

function formatNumberWithComma(number: number): string {
  return Number(number || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })
}

function $nf(value: number): string {
  return value.toLocaleString('en-IN', { maximumFractionDigits: 2 })
}

export function generateQuotationPDF(onlyBody: boolean, quotationInfo: Record<string, any>, companyInfo?: Record<string, any>): string {
  const loginStore = useLoginStore()
  if (!companyInfo) {
    companyInfo = loginStore.companyInfo ?? {}
  }

  let sameTax = null
  let taxIndex: number | null = null

  const formatRowDescription = (str: string) => {
    return str
      .split('\n')
      .map((line) => `<div>${line}</div>`)
      .join(' ')
  }

  const tableRow = (rows: Array<any>): string => {
    let isTaxSame: number | boolean | null = null

    const htmlRows = rows.map((row, index) => {
      if (isTaxSame !== false && row.tax_scheme.rate !== 0) {
        if (isTaxSame === null) {
          isTaxSame = row.tax_scheme.id
          taxIndex = index
        } else if (isTaxSame !== row.tax_scheme.id) {
          isTaxSame = false
        }
      }

      return `
      <tr style="color: #444; font-weight: 400;">
        <td style="padding: 8px; border: 1px solid #ccc; text-align: center;">${index + 1}</td>
        <td style="padding: 8px; border: 1px solid #ccc; text-align: center;">${row.hs_code ?? ''}</td>
        <td style="padding: 8px; border: 1px solid #ccc;">
          <strong>${row.item_name}</strong>
          ${row.description ? `<div style="font-size: 12px; color: #888;">${formatRowDescription(row.description)}</div>` : ''}
        </td>
        <td style="padding: 8px; border: 1px solid #ccc;">${row.quantity} <span style="font-size: 12px; color: gray;">${row.unit_name}</span></td>
        <td style="padding: 8px; border: 1px solid #ccc;">${$nf(row.rate)}</td>
        <td style="padding: 8px; border: 1px solid #ccc; text-align: right;">${formatNumberWithComma(row.quantity * row.rate)}</td>
      </tr>`
    })

    sameTax = isTaxSame
    return htmlRows.join('')
  }

  let html = ''
  if (!onlyBody) {
    html += `
    <div style="display: flex; justify-content: space-between; align-items: flex-start; font-family: Arial, sans-serif;">
      <div>
        <h1 style="margin: 0; font-size: 28px;">${companyInfo.name}${companyInfo.organization_type === 'private_limited' ? ' Pvt. Ltd.' : ''}</h1>
        <p style="margin: 5px 0;">${companyInfo.address}</p>
        <p style="margin: 5px 0;">Tax Reg. No.: <strong>${companyInfo.tax_identification_number}</strong></p>
      </div>
      <div style="text-align: right;">
        ${companyInfo.logo_url ? `<img src="${companyInfo.logo_url}" alt="Logo" style="height: 60px; max-width: 200px; object-fit: contain;" />` : ''}
        <p style="margin: 5px 0; color: #007bff;"><img src="/icons/telephone-fill.svg" style="width: 14px; vertical-align: middle; margin-right: 5px;" /> ${companyInfo.contact_no}</p>
        <p style="margin: 5px 0; color: #007bff;"><img src="/icons/envelope-fill.svg" style="width: 14px; vertical-align: middle; margin-right: 5px;" /> ${companyInfo.emails?.join(', ') ?? ''}</p>
      </div>
    </div>
    <hr style="margin: 20px 0;" />
    `
  }

  const customerSection = `
  <div style="margin: ${onlyBody ? '80px 0 20px' : '20px 0'}; font-family: Arial, sans-serif;">
    <h2 style="text-align: center; margin-bottom: 20px;">Quotation</h2>
    <div style="display: flex; justify-content: space-between;">
      <div>
        <p><strong>To:</strong></p>
        <p>${quotationInfo.party ? quotationInfo.customer_name || quotationInfo.party_name : quotationInfo.customer_name || ''}</p>
        ${quotationInfo.address ? `<p>${quotationInfo.address}</p>` : ''}
      </div>
      <div style="text-align: right;">
        ${quotationInfo.number ? `<p><strong>QT No.:</strong> ${quotationInfo.number}</p>` : ''}
        <p><strong>Date:</strong> ${quotationInfo.date}</p>
        <p><strong>Miti:</strong> ${DateConverter.getRepresentation(quotationInfo.date, 'bs')}</p>
        ${quotationInfo.expiry_date ? `<p><strong>Expiry Date:</strong> ${quotationInfo.expiry_date}</p>` : ''}
        ${quotationInfo.expiry_date ? `<p><strong>Myad Sakine Miti:</strong> ${DateConverter.getRepresentation(quotationInfo.expiry_date, 'bs')}</p>` : ''}
      </div>
    </div>
  </div>`

  const tableHeader = `
  <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px;">
    <thead>
      <tr style="background-color: #f2f2f2;">
        <th style="padding: 8px; border: 1px solid #ccc;">SN</th>
        <th style="padding: 8px; border: 1px solid #ccc;">HS Code</th>
        <th style="padding: 8px; border: 1px solid #ccc;">Particulars</th>
        <th style="padding: 8px; border: 1px solid #ccc;">Qty</th>
        <th style="padding: 8px; border: 1px solid #ccc;">Rate</th>
        <th style="padding: 8px; border: 1px solid #ccc;">Amount (${companyInfo.config_template === 'np' ? 'NRS' : 'N/A'})</th>
      </tr>
    </thead>
    <tbody>
      ${quotationInfo.rows ? tableRow(quotationInfo.rows) : ''}
    </tbody>
  </table>
  `

  const totals = `
  <div style="display: flex; justify-content: space-between; margin-top: 20px; font-family: Arial, sans-serif;">
    <div>
      <p><strong>In words:</strong> ${numberToText(quotationInfo.quotation_meta.grand_total)}</p>
    </div>
    <div style="width: 250px; border: 1px solid #ccc; padding: 10px;">
      <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #ccc; padding: 4px 0;">
        <span><strong>Sub Total</strong></span><span>${formatNumberWithComma(quotationInfo.quotation_meta.sub_total)}</span>
      </div>
      ${
        quotationInfo.quotation_meta.discount
          ? `
      <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #ccc; padding: 4px 0;">
        <span><strong>Discount</strong></span><span>${formatNumberWithComma(quotationInfo.quotation_meta.discount)}</span>
      </div>`
          : ''
      }
      <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #ccc; padding: 4px 0;">
        <span><strong>${sameTax ? `${quotationInfo.rows[taxIndex].tax_scheme.name} (${quotationInfo.rows[taxIndex].tax_scheme.rate}%)` : 'Tax'}</strong></span>
        <span>${formatNumberWithComma(quotationInfo.quotation_meta.tax)}</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding-top: 6px;">
        <span><strong>Grand Total</strong></span><span>${formatNumberWithComma(quotationInfo.quotation_meta.grand_total)}</span>
      </div>
    </div>
  </div>
  `

  const footer = `
  <div style="margin-top: 30px; font-family: Arial, sans-serif;">
    ${quotationInfo.total_amount ? `<p><strong>Total in words:</strong> ${numberToText(Number(quotationInfo.total_amount))}</p>` : ''}
    ${quotationInfo.remarks ? `<p><strong>Remarks:</strong> ${quotationInfo.remarks}</p>` : ''}
    ${quotationInfo.footer_text ? `<p>${quotationInfo.footer_text}</p>` : ''}
    <div style="margin-top: 20px; text-align: right;">
      <p style="margin: 5px 0;">Generated by ${loginStore.username || 'system'} for ${companyInfo.name}</p>
      ${onlyBody ? '' : `<p style="margin: 5px 0;">This is a computer-generated quotation from <strong>awecount.com</strong> - IRD Approval No. 7600405</p>`}
    </div>
  </div>`

  return html + customerSection + tableHeader + totals + footer
}
