const $q = useQuasar()

export default function useHandleDeleteFifoInconsistency(
  url: string,
  response: Record<string, any>,
  body: Record<string, any> | null,
  method = 'POST'
) {
  $q.dialog({
    title: '<span class="text-orange">Fifo Inconsistency!</span>',
    message:
      `<span class="text-grey-8">Reason: ${response.data.detail}` +
      '<div class="text-body1 text-weight-medium text-grey-8 q-mt-md">Are you sure you want to Continue?</div>',
    cancel: true,
    html: true,
  }).onOk(() => {
    useApi(url + '?fifo_inconsistency=true', {
      method: method,
      body: body,
    }).then((data) => {
      // $q.notify({
      //   color: 'positive',
      //   message: 'Saved',
      //   icon: 'check_circle',
      // })
      // if (isModal) {
      //   context.emit('modalSignal', data)
      // } else {
      //   if (config.successRoute) {
      //     router.push(config.successRoute)
      //   } else {
      //     router.push(removeLastUrlSegment(route.path))
      //   }
      // }
      //   .catch((error) => {
      //     $q.notify({
      //       color: 'negative',
      //       message: 'Something went Wrong!',
      //       icon: 'report_problem',
      //     })
    })
  })
}
