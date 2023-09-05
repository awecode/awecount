function formatNumberWithCommas(number) {
    const roundNumber = Math.round(number * 100) / 100
    // Convert the number to a string
    const numStr = roundNumber.toString();

    // Split the string into integer and decimal parts (if any)
    const parts = numStr.split('.');
    const intergers = parts[0].split('').reverse()
    let tempGroup = ''
    let commaCount = 0
    const numbersArray = []
    for (let i = 0; i <= intergers.length - 1; i++) {
      tempGroup = tempGroup + intergers[i]
      if (i === 2 && commaCount === 0) {
        numbersArray.push(tempGroup)
        tempGroup = ''
      } else if (i % 2 == 0 && i > 3) {
        numbersArray.push(tempGroup)
        tempGroup = ''
      }
    }
    // Join the groups with commas and return the formatted string
    const totalString = numbersArray.join(',');
    return totalString.split('').reverse().join('') + `${parts[1] ? '.'+ parts[1] : '' }`
  }
export default formatNumberWithCommas