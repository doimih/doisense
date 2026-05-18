import {
  INDEXABLE_PUBLIC_PATHS,
  PUBLIC_LOCALES,
  normalizeAppBasePath,
  normalizeSiteUrl,
  toAbsoluteUrl,
  toLocalePath,
} from '../utils/publicSeo'

function escapeXml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  const siteUrl = normalizeSiteUrl(config.public.siteUrl as string | undefined)
  const basePath = normalizeAppBasePath(config.public.appBaseUrl as string | undefined)
  const lastModified = new Date().toISOString()

  const urlEntries = PUBLIC_LOCALES.flatMap((localeEntry) =>
    INDEXABLE_PUBLIC_PATHS.map((path) => {
      const localizedPath = toLocalePath(path, localeEntry.code)
      const alternateLinks = PUBLIC_LOCALES.map((alternateLocale) => {
        const alternatePath = toLocalePath(path, alternateLocale.code)
        return `    <xhtml:link rel="alternate" hreflang="${escapeXml(alternateLocale.language.toLowerCase())}" href="${escapeXml(toAbsoluteUrl(siteUrl, basePath, alternatePath))}" />`
      }).join('\n')

      const xDefaultHref = escapeXml(toAbsoluteUrl(siteUrl, basePath, path))

      return [
        '  <url>',
        `    <loc>${escapeXml(toAbsoluteUrl(siteUrl, basePath, localizedPath))}</loc>`,
        alternateLinks,
        `    <xhtml:link rel="alternate" hreflang="x-default" href="${xDefaultHref}" />`,
        `    <lastmod>${lastModified}</lastmod>`,
        '  </url>',
      ].join('\n')
    }),
  ).join('\n')

  setHeader(event, 'content-type', 'application/xml; charset=utf-8')

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    urlEntries,
    '</urlset>',
    '',
  ].join('\n')
})