/**
 https://github.com/garora/number2text/
 Stripped down for Indian System Only, Several other fixes
 */

export default function numberToText(num: number | string, isCurrency: boolean = true) {
  if (Number.isNaN(num)) return '-'

  if (typeof num === 'string') {
    num = Number.parseInt(num)
  }

  // num = Math.round(num * 100) / 100
  num = Math.round((num + Number.EPSILON) * 100) / 100
  if (num >= 0) {
    return toText(num, isCurrency)
  } else {
    return `Negative ${toText(num * -1, isCurrency)}`
  }
}

function toText(num: number, isCurrency: boolean) {
  let res
  const fract_part: number = Math.round(frac_one(num) * 100)

  let fract_num = ''
  const USE_AND_EVEN_IF_DECIMAL = false
  const useAnd: boolean = !(fract_part > 0) || USE_AND_EVEN_IF_DECIMAL

  if (fract_part > 0) {
    if (isCurrency) fract_num = `and ${toIndianText(fract_part, isCurrency, false)} Paisa`
    else fract_num = ` Point ${toIndianText(fract_part, isCurrency)}`
  }

  if (isCurrency) {
    const rupeeString = Math.floor(num) == 1 ? ' Rupee ' : ' Rupees '
    res = `${toIndianText(num, isCurrency, useAnd) + rupeeString + fract_num} only`
  } else {
    res = toIndianText(num, isCurrency, useAnd) + fract_num
  }

  return res
}

function frac_one(num: number) {
  return num % 1
}

function toIndianText(num: number, isCurrency?: boolean, useAnd?: boolean) {
  const Gn = Math.floor(num / 10000000) /* Crore */
  num -= Gn * 10000000
  const kn = Math.floor(num / 100000) /* lakhs */
  num -= kn * 100000
  const Hn = Math.floor(num / 1000) /* thousand */
  num -= Hn * 1000
  const Dn = Math.floor(num / 100) /* Tens (deca) */
  num = num % 100 /* Ones */
  const tn = Math.floor(num / 10)
  const one = Math.floor(num % 10)

  let res = ''

  if (Gn > 0) {
    res += `${toIndianText(Gn)} Crore`
  }
  if (kn > 0) {
    res += `${(res == '' ? '' : ' ') + toIndianText(kn)} Lakh`
  }
  if (Hn > 0) {
    res += `${(res == '' ? '' : ' ') + toIndianText(Hn)} Thousand`
  }

  if (Dn) {
    res += `${(res == '' ? '' : ' ') + toIndianText(Dn)} Hundred`
  }

  const ones: Array<string> = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
  const tens: Array<string> = ['', '', 'Twenty', 'Thirty', 'Fourty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

  if (tn > 0 || one > 0) {
    if (isCurrency && useAnd) {
      if (!(res == '')) res += ' and '
    }

    if (!(res == '')) res += ' '

    if (tn < 2) {
      res += ones[tn * 10 + one]
    } else {
      res += tens[tn]
      if (one > 0) {
        res += `-${ones[one]}`
      }
    }
  }

  if (res == '') {
    res = 'Zero'
  }
  return res
}
