// @ts-check
import antfu from '@antfu/eslint-config'

export default antfu({
  lessOpinionated: true,
  stylistic: {
    overrides: {
      'curly': ['error', 'multi-line', 'consistent'],
      'style/brace-style': ['error', '1tbs', { allowSingleLine: false }],
    },
  },
  javascript: {
    overrides: {
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },
  vue: {
    overrides: {
      // enforce <script setup lang="ts">
      'vue/block-lang': ['error', { script: { lang: 'ts' } }],
      'vue/component-api-style': ['error', ['script-setup', 'composition']],

      // enforce ts for props and emits
      'vue/define-props-declaration': ['error', 'type-based'],
      'vue/define-emits-declaration': ['error', 'type-literal'],

      // enforce line breaks
      'vue/max-attributes-per-line': ['error', { singleline: 10, multiline: 1 }],
      'vue/first-attribute-linebreak': ['error', { singleline: 'beside', multiline: 'below' }],

      // misc
      'vue/component-options-name-casing': ['error', 'kebab-case'],
      'vue/html-self-closing': ['error', { html: { normal: 'never', void: 'always' } }],
    },
  },
})
