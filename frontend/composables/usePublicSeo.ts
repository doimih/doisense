type UsePublicSeoInput = {
  title: string | Ref<string> | ComputedRef<string>
  description: string | Ref<string> | ComputedRef<string>
  type?: string | Ref<string> | ComputedRef<string>
  noindex?: boolean | Ref<boolean> | ComputedRef<boolean>
}

export function usePublicSeo(input: UsePublicSeoInput): void {
  const route = useRoute()
  const runtime = useRuntimeConfig()

  const siteUrlRaw = ((runtime.public.siteUrl as string) || "https://projects.doimih.net").trim()
  const siteUrl = siteUrlRaw.replace(/\/+$/, "")
  const appBaseRaw = (runtime.public.appBaseUrl as string) || "/"
  const appBase = appBaseRaw === "/" ? "" : `/${appBaseRaw.replace(/^\/+|\/+$/g, "")}`

  const canonicalUrl = computed(() => {
    const routePath = route.path.startsWith("/") ? route.path : `/${route.path}`
    return `${siteUrl}${appBase}${routePath}`
  })

  const ogImageUrl = computed(() => `${siteUrl}${appBase}/og-default.svg`)

  useSeoMeta({
    title: () => toValue(input.title),
    description: () => toValue(input.description),
    ogTitle: () => toValue(input.title),
    ogDescription: () => toValue(input.description),
    ogType: () => toValue(input.type) || "website",
    ogUrl: () => canonicalUrl.value,
    ogImage: () => ogImageUrl.value,
    twitterCard: "summary_large_image",
    twitterTitle: () => toValue(input.title),
    twitterDescription: () => toValue(input.description),
    twitterImage: () => ogImageUrl.value,
    robots: () => (toValue(input.noindex) ? "noindex, nofollow" : "index, follow"),
  })

  useHead({
    link: [{ rel: "canonical", href: canonicalUrl }],
  })
}
