export default {
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^~/(.*)$': '<rootDir>/$1',
    '^@vue/test-utils$': '<rootDir>/node_modules/@vue/test-utils/dist/vue-test-utils.cjs.js',
  },
  testMatch: ['**/tests/**/*.spec.[jt]s', '**/__tests__/**/*.spec.[jt]s'],
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleFileExtensions: ['vue', 'js', 'ts', 'tsx', 'json'],
  collectCoverageFrom: [
    'components/**/*.vue',
    'composables/**/*.ts',
    'stores/**/*.ts',
    'pages/**/*.vue',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/.nuxt/**',
    '!**/dist/**',
  ],
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 65,
      lines: 65,
      statements: 65,
    },
    './components/': {
      branches: 50,
      functions: 60,
      lines: 60,
      statements: 60,
    },
    './stores/': {
      branches: 70,
      functions: 80,
      lines: 75,
      statements: 75,
    },
  },
}
