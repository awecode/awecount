export default (
  url: string,
  /* eslint-disable @typescript-eslint/no-explicit-any */
  response: Record<string, any>,
  body: Record<string, any> | null,
  $q: Record<string, any>,
  /* eslint-disable @typescript-eslint/no-explicit-any */
  method = 'POST',
) => {
  return new Promise((resolve, reject) => {
    $q.notify({
      color: 'orange',
      message: `${humanizeWord(response.data?.code)}!`,
      icon: 'report_problem',
    })
    $q.dialog({
      title: `<span class="text-orange">${humanizeWord(response.data?.code)}!</span>`,
      message: `<span class="text-grey-8">Reason: ${response.data.detail}` + '<div class="text-body1 text-weight-medium text-grey-8 q-mt-md">Are you sure you want to Continue?</div>',
      html: true,
      cancel: true,
    })
      .onOk(() => {
        useApi(`${url}?${response.data?.code}=true`, {
          method,
          body,
        }).then((data) => {
          resolve(data)
        })
      })
      .onCancel(() => {
        reject({
          status: 'cancel',
        })
      })
    // .onDismiss(() => {
    //   console.log('Called on OK or Cancel')
    // })
  })
}
