export default (
  url: string,
  response: Record<string, any>,
  body: Record<string, any> | null,
  $q: Record<string, any>,
  method = 'POST'
) => {
  return new Promise((resolve, reject) => {
    $q.notify({
      color: 'negative',
      message: 'Fifo Inconsistency Error!',
      icon: 'report_problem',
    })
    $q.dialog({
      title: '<span class="text-orange">Fifo Inconsistency!</span>',
      message:
        `<span class="text-grey-8">Reason: ${response.data.detail}` +
        '<div class="text-body1 text-weight-medium text-grey-8 q-mt-md">Are you sure you want to Continue?</div>',
      html: true,
      cancel: true,
    })
      .onOk(() => {
        debugger
        useApi(url + '?fifo_inconsistency=true', {
          method: method,
          body: body?.body,
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
