export const $nf = (amount: string | number) => {
  if (!amount || Number.isNaN(amount) || amount === 'NaN') {
    amount = 0
  }
  if (typeof amount !== 'number') {
    amount = Number.parseFloat(amount)
  }
  // return amount.toFixed(2);
  return Math.round((amount + Number.EPSILON) * 100) / 100
}

export const humanizeWord = (word: string) => {
  if (!word) return ''
  word = word.replace(/_/g, ' ')
  return word.charAt(0).toUpperCase() + word.slice(1)
}
