import { boot } from 'quasar/wrappers';
import * as Sentry from '@sentry/vue';
// import { BrowserTracing } from '@sentry/tracing';

export default boot(({ app, router }) => {
  Sentry.init({
    app,
    dsn: 'https://51ed8b7e9bb19758cd85c6b792f9c9c8@o374601.ingest.sentry.io/4506143333154816',
    integrations: [
      // new BrowserTracing({
      //   routingInstrumentation: Sentry.vueRouterInstrumentation(router),
      //   tracingOrigins: ['localhost', 'my-site-url.com', regex],
      // }),
    ],

    trackComponents: true,
    tracesSampleRate: 1.0,
  });
  console.log('snetry-------------------------------------------------------------------------------------------------------', Sentry)
});
