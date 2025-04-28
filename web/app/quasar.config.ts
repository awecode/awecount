import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

import { defineConfig } from '#q-app/wrappers'
import { sentryVitePlugin } from '@sentry/vite-plugin'

import dotenv from 'dotenv'
import { presetWind } from 'unocss'

export default defineConfig((/* ctx */) => {
  dotenv.config({ path: path.resolve(fileURLToPath(import.meta.url), '..', '..', '..', '.env') })

  return {
    devServer: { open: true },

    css: ['app.scss'],

    boot: ['ofetch', 'num', 'sentry'],

    extras: ['mdi-v7', 'fontawesome-v6', 'roboto-font', 'material-icons'],

    framework: {
      config: {
        notify: { position: 'top-right', progress: true },
      },
      plugins: ['Notify', 'Dialog', 'Meta'],
    },

    build: {
      target: {
        browser: ['es2022', 'firefox115', 'chrome115', 'safari14'],
        node: 'node20',
      },

      vueRouterMode: 'history',
      vitePlugins: [
        ['unocss/vite', { presets: [presetWind()] }],
        [
          'unplugin-auto-import/vite',
          {
            dirs: ['./src/composables'],
            dts: './.quasar/auto-imports.d.ts',
            imports: ['vue', 'vue-router', 'quasar', 'pinia'],
            include: [/\.[tj]sx?$/, /\.vue$/, /\.vue\?vue/, /\.md$/],
          },
        ],
        ['unplugin-vue-components/vite', { dts: './.quasar/components.d.ts' }],
        [
          sentryVitePlugin({
            org: 'awecode',
            project: 'awecount',
          }),
        ],
      ],
      extendViteConf: (viteConf) => {
        viteConf.define ||= {}
        viteConf.define['import.meta.env.API_BASE_URL'] = JSON.stringify(process.env.API_URL)
        viteConf.define['import.meta.env.ALLOW_SIGNUP'] = process.env.ALLOW_SIGNUP === 'True'
      },
    },
  }
})
