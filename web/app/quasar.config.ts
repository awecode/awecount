import { defineConfig } from '#q-app/wrappers'
import { sentryVitePlugin } from '@sentry/vite-plugin'
import { presetWind } from 'unocss'

export default defineConfig((/* ctx */) => {
  return {
    devServer: { open: true },

    css: ['app.scss'],

    boot: ['ofetch', 'num', 'sentry'],

    extras: [
      'mdi-v7',
      'fontawesome-v6',
      'roboto-font',
      'material-icons',
    ],

    build: {
      target: {
        browser: ['es2022', 'firefox115', 'chrome115', 'safari14'],
        node: 'node20',
      },

      vueRouterMode: 'history',
      vitePlugins: [
        [
          'unocss/vite',
          { presets: [presetWind()] },
        ],
        [
          'unplugin-auto-import/vite',
          {
            dirs: ['./src/composables'],
            dts: './.quasar/auto-imports.d.ts',
            imports: ['vue', 'vue-router', 'quasar', 'pinia'],
            include: [/\.[tj]sx?$/, /\.vue$/, /\.vue\?vue/, /\.md$/],
          },
        ],
        [
          'unplugin-vue-components/vite',
          { dts: './.quasar/components.d.ts' },
        ],
        [
          sentryVitePlugin({
            org: 'awecode',
            project: 'awecount',
          }),
        ],
      ],
    },

  }
})
