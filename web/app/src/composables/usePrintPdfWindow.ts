export default function useGenerateChequePdf(printData: string) {
  const iframe = document.createElement('iframe')
  iframe.style = 'display:none; margin: 20px'
  document.body.appendChild(iframe)
  const iframeWindow = iframe.contentWindow
  iframeWindow.document.open()
  iframeWindow.document.write(printData)
  iframeWindow.document.close()
  iframeWindow.focus()
  setTimeout(() => iframeWindow.print(), 100)
}
