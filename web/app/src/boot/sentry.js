import { boot } from 'quasar/wrappers';
import * as Sentry from '@sentry/vue';
// import { BrowserTracing } from '@sentry/tracing';

export default boot(({ app }) => {
  Sentry.init({
    app,
    dsn: 'https://51ed8b7e9bb19758cd85c6b792f9c9c8@o374601.ingest.sentry.io/4506143333154816',
    enabled: process.env.NODE_ENV !== 'development',
    integrations: [],
    trackComponents: true,
  });
});
