import { boot } from 'quasar/wrappers';
import * as Sentry from '@sentry/vue';
import { BrowserTracing } from '@sentry/tracing';

export default boot(({ app, router }) => {
  Sentry.init({
    app,
    dsn: '<my sentry dns>',
    integrations: [
      new BrowserTracing({
        routingInstrumentation: Sentry.vueRouterInstrumentation(router),
        tracingOrigins: ['localhost', 'my-site-url.com', regex],
      }),
    ],

    trackComponents: true,
    tracesSampleRate: 1.0,
  });
});
