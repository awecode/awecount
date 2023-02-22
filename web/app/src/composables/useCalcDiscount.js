const calcDiscount = (type, totalAmount, discount, discountOptions) => {
  if (type === 'Percent') {
    return totalAmount * (discount / 100)
  } else if (type === 'Amount') return discount
  else if (typeof type === 'number') {
    const index = discountOptions.findIndex((item) => type === item.id)
    const discountObj = discountOptions[index]
    if (discountObj.type === 'Percent') {
      return totalAmount * (discountObj.value / 100)
    } else return discountObj.value
  }
}
export default calcDiscount
