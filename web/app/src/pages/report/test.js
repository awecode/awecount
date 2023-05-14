const onDownloadXls12 = () => {
  // TODO: add download xls link
  // const wb = utils.table_to_book(tableRef.value)
  // const elt = tableRef.value
  const elt = document.getElementById('tableRef').children[0]
  const baseUrl = window.location.origin
  replaceHrefAttribute(elt, baseUrl)
  // adding styles
  const worksheet = utils.table_to_sheet(elt)
  const range = utils.decode_range(worksheet['!ref'])
  for (let row = range.s.r; row <= range.e.r; row++) {
    for (let col = range.s.c; col <= range.e.c; col++) {
      const cellAddress = utils.encode_cell({ r: row, c: col })
      if (worksheet[cellAddress]) {
        const td = elt.rows[row].cells[col]
        if (td instanceof HTMLElement) {
          const computedStyle = getComputedStyle(td)
          // debugger
          const style = {
            font: { bold: true },
            fill: { fgColor: { rgb: computedStyle.backgroundColor } },
            alignment: { horizontal: 'left' }, // Adjust as needed
          }
          worksheet[cellAddress].s = style
        }
      }
    }
    // adding styles
    // const wb = utils.table_to_book(elt, {
    //   sheet: 'sheet1',
    //   blankrows: false,
    // })
    const workbook = utils.book_new()
    utils.book_append_sheet(workbook, worksheet, 'Sheet1')
    writeFileXLSX(workbook, 'TrialBalance.xls', {
      cellStyles: true,
    })
  }
}
