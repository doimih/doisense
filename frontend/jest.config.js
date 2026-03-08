export default {
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^~/(.*)$': '<rootDir>/$1',
  },
  testMatch: ['**/tests/**/*.spec.[jt]s', '**/__tests__/**/*.spec.[jt]s'],
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleFileExtensions: ['vue', 'js', 'ts', 'tsx', 'json'],
  collectCoverageFrom: [
    'components/**/*.vue',
    'stores/**/*.ts',
    'pages/**/*.vue',
  ],
  coverageThreshold: {
    global: {
      branches: 50,
      functions: 50,
      lines: 50,
      statements: 50,
    },
  },
}
