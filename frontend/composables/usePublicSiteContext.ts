export function usePublicSiteContext() {
  const runtime = useRuntimeConfig()

  const siteUrl = computed(() => {
    const raw = ((runtime.public.siteUrl as string) || 'https://www.doisense.eu').trim()
    return raw.replace(/\/+$/, '')
  })

  const appBase = computed(() => {
    const raw = (runtime.public.appBaseUrl as string) || '/'
    return raw === '/' ? '' : `/${raw.replace(/^\/+|\/+$/g, '')}`
  })

  function toAbsolutePublicUrl(path: string): string {
    const rawPath = path.startsWith('http://') || path.startsWith('https://')
      ? new URL(path).pathname
      : path
    const normalizedPath = rawPath.startsWith('/') ? rawPath : `/${rawPath}`
    const appRelativePath = appBase.value && normalizedPath.startsWith(`${appBase.value}/`)
      ? normalizedPath.slice(appBase.value.length)
      : normalizedPath === appBase.value
        ? '/'
        : normalizedPath

    return `${siteUrl.value}${appBase.value}${appRelativePath}`
  }

  return {
    siteUrl,
    appBase,
    toAbsolutePublicUrl,
  }
}
