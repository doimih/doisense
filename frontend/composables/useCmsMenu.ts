export interface CmsMenuLink {
  slug: string
  title: string
  path: string
}

export function useCmsMenu() {
  const headerLinks = useState<CmsMenuLink[]>('cms-header-links', () => [])
  const footerLinks = useState<CmsMenuLink[]>('cms-footer-links', () => [])

  async function load(language: string) {
    try {
      const config = useRuntimeConfig()
      const base = config.public.apiBase as string
      const res = await $fetch<{ header: CmsMenuLink[]; footer: CmsMenuLink[] }>(
        `${base}/cms/menu-links`,
        {
          query: { language },
        },
      )
      headerLinks.value = res.header || []
      footerLinks.value = res.footer || []
    } catch {
      headerLinks.value = []
      footerLinks.value = []
    }
  }

  return { headerLinks, footerLinks, load }
}
