import { boot } from 'quasar/wrappers'

export default boot(({ app }) => {
  const $nf = (amount: string | number, toFixed: undefined | number) => {
    if (!amount || isNaN(amount) || amount === 'NaN') {
      amount = 0
    }
    if (typeof amount !== 'number') {
      amount = Number.parseFloat(amount)
    }
    // return amount.toFixed(2);
    const returnAmount = Math.round((amount + Number.EPSILON) * 100) / 100
    if (toFixed === undefined) {
      return returnAmount
    } else {
      return returnAmount.toFixed(toFixed)
    }
  }
  app.config.globalProperties.$nf = $nf
})
