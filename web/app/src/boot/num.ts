import { defineBoot } from '#q-app/wrappers'

export default defineBoot(({ app }) => {
  const $nf = (amount: string | number, toFixed: undefined | number) => {
    if (!amount || Number.isNaN(amount) || amount === 'NaN') {
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
      return (returnAmount).toFixed(toFixed)
    }
  }

  app.config.globalProperties.$nf = $nf
})
