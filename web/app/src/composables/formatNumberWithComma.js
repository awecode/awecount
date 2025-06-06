function formatNumberWithCommas(number, toFixed) {
  if (!number || isNaN(number) || number === 'NaN') {
    number = 0
  }
  if (typeof number !== 'number') {
    number = Number.parseFloat(number)
  }
  const multiplier = 10 ** (toFixed || 2)
  const roundNumber = Math.round(number * multiplier) / multiplier
  // Convert the number to a string
  const numStr = roundNumber.toString()

  // Split the string into integer and decimal parts (if any)
  const parts = numStr.split('.')
  const integers = parts[0].split('').reverse()
  let tempGroup = ''
  const commaCount = 0
  const numbersArray = []
  for (let i = 0; i <= integers.length - 1; i++) {
    tempGroup = tempGroup + integers[i]
    if (i === 2 && commaCount === 0) {
      numbersArray.push(tempGroup)
      tempGroup = ''
    } else if (i % 2 == 0 && i > 3) {
      numbersArray.push(tempGroup)
      tempGroup = ''
    } else if (i == integers.length - 1) {
      numbersArray.push(tempGroup)
    }
  }
  // Join the groups with commas and return the formatted string
  const totalString = numbersArray.join(',')
  return `${totalString.split('').reverse().join('')}${parts[1] ? `.${parts[1]}` : ''}`
}
export default formatNumberWithCommas
