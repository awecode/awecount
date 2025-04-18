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
      // 'vue/block-lang': ['error', { script: { lang: 'ts' } }],
      'vue/component-api-style': ['error', ['script-setup', 'composition']],

      // enforce ts for props and emits
      'vue/define-props-declaration': ['error', 'type-based'],
      'vue/define-emits-declaration': ['error', 'type-literal'],

      // enforce line breaks
      'vue/max-attributes-per-line': ['error', { singleline: 3, multiline: 1 }],
      'vue/first-attribute-linebreak': ['error', { singleline: 'beside', multiline: 'below' }],

      // misc
      'vue/component-options-name-casing': ['error', 'kebab-case'],
      'vue/html-self-closing': ['error', { html: { normal: 'never', void: 'always' } }],

      // attributes
      'vue/attributes-order': [
        'error',
        {
          alphabetical: true,
          order: ['DEFINITION', 'LIST_RENDERING', 'CONDITIONALS', 'RENDER_MODIFIERS', 'GLOBAL', 'UNIQUE', 'SLOT', 'TWO_WAY_BINDING', 'OTHER_DIRECTIVES', 'ATTR_SHORTHAND_BOOL', 'ATTR_STATIC', 'ATTR_DYNAMIC', 'EVENTS', 'CONTENT'],
        },
      ],
    },
  },
})
