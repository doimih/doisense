// ESLint: run after npm install. For Nuxt, consider: npx nuxi prepare && use .nuxt/eslint.config.mjs
export default [
  {
    ignores: ['.output/**', 'node_modules/**'],
  },
  {
    files: ['**/*.{js,ts}'],
    languageOptions: {
      parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
    },
    rules: {},
  },
]
