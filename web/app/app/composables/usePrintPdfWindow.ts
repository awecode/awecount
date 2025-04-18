export default function useGenerateChequePdf(printData: string) {
  const iframe = document.createElement('iframe')
  iframe.style = 'display:none; margin: 20px'
  document.body.appendChild(iframe)
  const iframeWindow = iframe.contentWindow
  if (iframeWindow !== null) {
    iframeWindow.document.open()
    iframeWindow.document.write(printData)
    iframeWindow.document.close()
    iframeWindow.focus()
    nextTick(() => {
      iframeWindow.print()
    })
  }
}
