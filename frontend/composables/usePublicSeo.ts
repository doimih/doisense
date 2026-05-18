type JsonLdNode = Record<string, unknown>

type UsePublicSeoInput = {
  title: string | Ref<string> | ComputedRef<string>
  description: string | Ref<string> | ComputedRef<string>
  type?:
    | 'article'
    | 'website'
    | 'book'
    | 'profile'
    | 'music.song'
    | 'music.album'
    | 'music.playlist'
    | 'music.radio_status'
    | 'video.movie'
    | 'video.episode'
    | 'video.tv_show'
    | 'video.other'
    | Ref<string>
    | ComputedRef<string>
  noindex?: boolean | Ref<boolean> | ComputedRef<boolean>
  structuredData?:
    | JsonLdNode
    | JsonLdNode[]
    | Ref<JsonLdNode | JsonLdNode[] | null | undefined>
    | ComputedRef<JsonLdNode | JsonLdNode[] | null | undefined>
}

type OgType =
  | 'article'
  | 'website'
  | 'book'
  | 'profile'
  | 'music.song'
  | 'music.album'
  | 'music.playlist'
  | 'music.radio_status'
  | 'video.movie'
  | 'video.episode'
  | 'video.tv_show'
  | 'video.other'

type LocaleCode = 'ro' | 'en' | 'de' | 'fr' | 'it' | 'es' | 'pl'

export function usePublicSeo(input: UsePublicSeoInput): void {
  const route = useRoute()
  const { locales } = useI18n()
  const switchLocalePath = useSwitchLocalePath()
  const { toAbsolutePublicUrl, siteUrl, appBase } = usePublicSiteContext()

  const canonicalUrl = computed(() => {
    const routePath = route.path.startsWith('/') ? route.path : `/${route.path}`
    return toAbsolutePublicUrl(routePath)
  })

  const ogImageUrl = computed(() => `${siteUrl.value}${appBase.value}/og-default.svg`)
  const localeEntries = computed<Array<{ code: LocaleCode; language: string }>>(() => {
    const configuredLocales = Array.isArray(locales.value) ? locales.value : []
    const normalizedLocales: Array<{ code: LocaleCode; language: string }> = []

    for (const localeEntry of configuredLocales) {
      if (typeof localeEntry === 'string') {
        normalizedLocales.push({ code: localeEntry as LocaleCode, language: localeEntry })
        continue
      }

      if (localeEntry.code) {
        normalizedLocales.push({
          code: localeEntry.code as LocaleCode,
          language: localeEntry.language || localeEntry.code,
        })
      }
    }

    return normalizedLocales
  })
  const defaultLocaleCode = 'en'
  const alternateLinks = computed(() => localeEntries.value.map((localeEntry) => {
    const localizedPath = switchLocalePath(localeEntry.code) || route.path
    return {
      rel: 'alternate',
      hreflang: localeEntry.language.toLowerCase(),
      href: toAbsolutePublicUrl(localizedPath),
    }
  }))
  const xDefaultLink = computed(() => ({
    rel: 'alternate',
    hreflang: 'x-default',
    href: toAbsolutePublicUrl(switchLocalePath(defaultLocaleCode) || route.path),
  }))
  const structuredDataScripts = computed(() => {
    const rawStructuredData = toValue(input.structuredData)
    if (!rawStructuredData) {
      return []
    }

    const nodes = Array.isArray(rawStructuredData) ? rawStructuredData : [rawStructuredData]
    return nodes
      .filter((node): node is JsonLdNode => Boolean(node && Object.keys(node).length > 0))
      .map((node, index) => ({
        key: `json-ld-${index}`,
        type: 'application/ld+json',
        children: JSON.stringify(node),
      }))
  })

  useSeoMeta({
    title: () => toValue(input.title),
    description: () => toValue(input.description),
    ogTitle: () => toValue(input.title),
    ogDescription: () => toValue(input.description),
    ogType: () => (toValue(input.type) as OgType) || 'website',
    ogUrl: () => canonicalUrl.value,
    ogImage: () => ogImageUrl.value,
    twitterCard: 'summary_large_image',
    twitterTitle: () => toValue(input.title),
    twitterDescription: () => toValue(input.description),
    twitterImage: () => ogImageUrl.value,
    robots: () => (toValue(input.noindex) ? 'noindex, nofollow' : 'index, follow'),
  })

  useHead({
    link: () => [
      { rel: 'canonical', href: canonicalUrl.value },
      ...alternateLinks.value,
      xDefaultLink.value,
    ],
    script: () => structuredDataScripts.value,
  })
}
