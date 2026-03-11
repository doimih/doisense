// @ts-nocheck
import { computed, ref, watch } from 'vue'
import { useI18n } from '#imports'
import { useApi } from '~/composables/useApi'

export function useCmsStaticPage(baseSlug, prefix = '') {
  const { fetchApi } = useApi()
  const cmsPageCache = useState('cmsPageCache', () => new Map())
  const { locale } = useI18n()

  const cmsPage = ref(null)

  const localeCode = computed(() => (locale.value || 'en').slice(0, 2).toLowerCase())

  const normalizedBaseSlug = computed(() => {
    const cleanPrefix = prefix.trim().replace(/^-+|-+$/g, '')
    const cleanBase = baseSlug.trim().replace(/^-+|-+$/g, '')
    return cleanPrefix ? `${cleanPrefix}-${cleanBase}` : cleanBase
  })

  async function load() {
    const cacheKey = `${normalizedBaseSlug.value}:${localeCode.value}`
    if (cmsPageCache.value.has(cacheKey)) {
      cmsPage.value = cmsPageCache.value.get(cacheKey) || null
      return
    }

    try {
      const page = await fetchApi(
        `/cms/public/${normalizedBaseSlug.value}?language=${localeCode.value}`,
      )
      if (page?.content?.trim()) {
        cmsPage.value = page
        cmsPageCache.value.set(cacheKey, page)
      } else {
        cmsPageCache.value.set(cacheKey, null)
      }
    } catch {
      // Keep null when CMS page is missing.
      cmsPageCache.value.set(cacheKey, null)
    }
  }

  watch(
    () => locale.value,
    () => {
      load()
    },
    { immediate: true },
  )

  const hasCmsContent = computed(() => !!cmsPage.value?.content?.trim())

  return {
    cmsPage,
    hasCmsContent,
    load,
  }
}

