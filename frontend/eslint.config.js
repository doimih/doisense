import tsParser from '@typescript-eslint/parser'

export default [
  {
    ignores: ['.nuxt/**', '.output/**', 'node_modules/**'],
  },
  {
    files: ['**/*.{js,mjs,cjs,ts}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
    },
    rules: {},
  },
]
