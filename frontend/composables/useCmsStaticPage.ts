import { computed, ref, watch } from 'vue'
import { useI18n } from '#imports'
import { useApi } from '~/composables/useApi'

interface CmsPublicPage {
  slug: string
  title: string
  content: string
}

export function useCmsStaticPage(baseSlug: string, prefix = '') {
  const { fetchApi } = useApi()
  const { locale } = useI18n()

  const cmsPage = ref<CmsPublicPage | null>(null)

  const localeCode = computed(() => (locale.value || 'ro').slice(0, 2).toLowerCase())

  const normalizedBaseSlug = computed(() => {
    const cleanPrefix = prefix.trim().replace(/^-+|-+$/g, '')
    const cleanBase = baseSlug.trim().replace(/^-+|-+$/g, '')
    return cleanPrefix ? `${cleanPrefix}-${cleanBase}` : cleanBase
  })

  async function load() {
    cmsPage.value = null

    try {
      const page = await fetchApi<CmsPublicPage>(
        `/cms/public/${normalizedBaseSlug.value}?language=${localeCode.value}`,
      )
      if (page?.content?.trim()) {
        cmsPage.value = page
      }
    } catch {
      // Keep null when CMS page is missing.
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

