const fieldsArray = [
  'closing_cr',
  'closing_dr',
  'opening_cr',
  'opening_dr',
  'transaction_cr',
  'transaction_dr',
]
const totalObjectFormat = {
  closing_cr: 0,
  closing_dr: 0,
  opening_cr: 0,
  opening_dr: 0,
  transaction_cr: 0,
  transaction_dr: 0,
}

const newValue = {
  id: 2,
  name: 'Liabilities',
  children: [
    {
      id: 20,
      name: 'Account Payables',
      children: [
        {
          id: 21,
          name: 'Suppliers',
          children: [],
          total: [
            {
              closing_cr: 2400,
              closing_dr: 0,
              opening_cr: 0,
              opening_dr: 0,
              transaction_cr: 2400,
              transaction_dr: 0,
            },
          ],
        },
      ],
      total: [
        {
          closing_cr: 2400,
          closing_dr: 0,
          opening_cr: 0,
          opening_dr: 0,
          transaction_cr: 2400,
          transaction_dr: 0,
        },
      ],
    },
    {
      id: 28,
      name: 'Duties & Taxes',
      children: [],
      total: [
        {
          closing_cr: 32480.7,
          closing_dr: 0,
          opening_cr: 0,
          opening_dr: 0,
          transaction_cr: 32480.7,
          transaction_dr: 0,
        },
      ],
    },
  ],
}

let computedTotal = []
const array = [1, 2]
array.forEach((testItem) => {
  newValue.children.forEach((child, childIndex) => {
    let count = 0
    if (child.total && child.total.length > 0) {
      child.total.forEach((totalObj, totalIndex) => {
        if (totalObj) {
          // console.log(computedTotal)
          if (!computedTotal[totalIndex])
            computedTotal[totalIndex] = totalObjectFormat
          fieldsArray.forEach((field) => {
            computedTotal[totalIndex][field] =
              computedTotal[totalIndex][field] + totalObj[field]
          })
        }
      })
    } else computedTotal = []
  })
  console.log(computedTotal)
})
