import { boot } from 'quasar/wrappers'

export default boot(({ app }) => {
  const $nf = (amount: string | number) => {
    if (!amount || isNaN(amount) || amount === 'NaN') {
      amount = 0
    }
    if (typeof amount !== 'number') {
      amount = parseFloat(amount)
    }
    // return amount.toFixed(2);
    return Math.round((amount + Number.EPSILON) * 100) / 100
  }
  app.config.globalProperties.$nf = $nf
})
