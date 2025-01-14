const calcDiscount = (type, totalAmount, discount, discountOptions) => {
  if (!type) return 0
  if (type === 'Percent') {
    return totalAmount * (discount / 100)
  } else if (type === 'Amount') {
    return discount
  } else if (typeof type === 'number') {
    const index = discountOptions.findIndex(item => type === item.id)
    // To Handle case where the discountOptions is not yet fetched
    if (index < 0) return 0
    const discountObj = discountOptions[index]
    if (discountObj.type === 'Percent') {
      return totalAmount * (discountObj.value / 100)
    } else {
      return discountObj.value
    }
  }
}
export default calcDiscount
