export type PublicLocale = {
  code: string
  language: string
}

export const PUBLIC_LOCALES: PublicLocale[] = [
  { code: 'en', language: 'en-US' },
  { code: 'ro', language: 'ro-RO' },
  { code: 'de', language: 'de-DE' },
  { code: 'fr', language: 'fr-FR' },
  { code: 'it', language: 'it-IT' },
  { code: 'es', language: 'es-ES' },
  { code: 'pl', language: 'pl-PL' },
]

export const DEFAULT_PUBLIC_LOCALE = 'en'

export const INDEXABLE_PUBLIC_PATHS = [
  '/',
  '/features',
  '/pricing',
  '/about',
  '/contact',
  '/faq',
  '/legal/privacy',
  '/legal/terms',
  '/legal/cookies',
  '/legal/gdpr',
  '/legal/ai-consent',
  '/legal/payments-subscriptions',
]

export const PRIVATE_ROUTE_ROOTS = [
  '/api',
  '/admin',
  '/auth',
  '/chat',
  '/journal',
  '/notifications',
  '/onboarding',
  '/payment-success',
  '/profile',
  '/programs',
  '/search',
  '/tickets',
  '/trial-expired',
]

export function normalizeSiteUrl(value?: string): string {
  return (value || 'https://www.doisense.eu').trim().replace(/\/+$/, '')
}

export function normalizeAppBasePath(value?: string): string {
  const normalized = (value || '/').trim()
  if (!normalized || normalized === '/') {
    return ''
  }

  return `/${normalized.replace(/^\/+|\/+$/g, '')}`
}

export function toLocalePath(path: string, localeCode: string): string {
  if (localeCode === DEFAULT_PUBLIC_LOCALE) {
    return path
  }

  return path === '/'
    ? `/${localeCode}`
    : `/${localeCode}${path}`
}

export function withBasePath(basePath: string, path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${basePath}${normalizedPath}` || '/'
}

export function toAbsoluteUrl(siteUrl: string, basePath: string, path: string): string {
  return `${siteUrl}${withBasePath(basePath, path)}`
}