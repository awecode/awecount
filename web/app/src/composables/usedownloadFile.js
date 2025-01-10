export default (blob, contentType, fileName) => {
  // https://blog.jayway.com/2017/07/13/open-pdf-downloaded-api-javascript/
  // It is necessary to create a new blob object with mime-type explicitly set
  // otherwise only Chrome works like it should
  let newBlob = new Blob([blob], { type: contentType })

  // IE doesn't allow using a blob object directly as link href
  // instead it is necessary to use msSaveOrOpenBlob
  if (window.navigator && window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(newBlob)
    return
  }

  // For other browsers:
  // Create a link pointing to the ObjectURL containing the blob.
  let link = document.createElement('a')
  link.href = window.URL.createObjectURL(newBlob)
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  // setTimeout(function() {
  //   // For Firefox it is necessary to delay revoking the ObjectURL
  //   document.body.removeChild(link);
  //   window.URL.revokeObjectURL(data);
  // }, 100);
}
