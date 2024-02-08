import { boot } from 'quasar/wrappers';
import * as Sentry from '@sentry/vue';
// import { BrowserTracing } from '@sentry/tracing';

// debugger

export default boot(({ app, router }) => {
  Sentry.init({
    app,
    // dsn: 'https://51ed8b7e9bb19758cd85c6b792f9c9c8@o374601.ingest.sentry.io/4506143333154816',
    dsn: 'https://a33dd63776e1f24aea26b1a39a0aebf3@o4506710210641920.ingest.sentry.io/4506710212345856',
    integrations: [
      // new BrowserTracing({
      //   routingInstrumentation: Sentry.vueRouterInstrumentation(router),
      //   tracingOrigins: ['localhost', 'my-site-url.com', regex],
      // }),
      // Sentry.browserTracingIntegration({ router })
    ],
    environment: 'development',
    trackComponents: true,
    tracesSampleRate: 1.0,
    tracePropagationTargets: ['localhost', /^https:\/\/sentry\.awecount\-quasar\.pages\.dev/,]
  });
});
