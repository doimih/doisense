import {
  DEFAULT_PUBLIC_LOCALE,
  PRIVATE_ROUTE_ROOTS,
  PUBLIC_LOCALES,
  normalizeAppBasePath,
  normalizeSiteUrl,
  toAbsoluteUrl,
  toLocalePath,
  withBasePath,
} from '../utils/publicSeo'

export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  const siteUrl = normalizeSiteUrl(config.public.siteUrl as string | undefined)
  const basePath = normalizeAppBasePath(config.public.appBaseUrl as string | undefined)

  const disallowPaths = new Set<string>()
  for (const privateRoot of PRIVATE_ROUTE_ROOTS) {
    disallowPaths.add(withBasePath(basePath, privateRoot))
    for (const localeEntry of PUBLIC_LOCALES) {
      if (localeEntry.code === DEFAULT_PUBLIC_LOCALE) {
        continue
      }

      disallowPaths.add(withBasePath(basePath, toLocalePath(privateRoot, localeEntry.code)))
    }
  }

  setHeader(event, 'content-type', 'text/plain; charset=utf-8')

  return [
    'User-agent: *',
    'Allow: /',
    ...[...disallowPaths].sort().map((path) => `Disallow: ${path}`),
    `Sitemap: ${toAbsoluteUrl(siteUrl, basePath, '/sitemap.xml')}`,
    '',
  ].join('\n')
})