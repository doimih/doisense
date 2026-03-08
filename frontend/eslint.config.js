// ESLint: run after npm install. For Nuxt, consider: npx nuxi prepare && use .nuxt/eslint.config.mjs
export default [
  { files: ['**/*.{js,ts,vue}'], languageOptions: { parserOptions: { ecmaVersion: 'latest', sourceType: 'module' } }, rules: {} },
]
