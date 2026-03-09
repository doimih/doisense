type GdprConsent = {
  necessary: true
  analytics: boolean
  marketing: boolean
  personalization: boolean
  updatedAt: string
}

const CONSENT_STORAGE_KEY = 'doisense_gdpr_consent_v1'

function defaultConsent(): GdprConsent {
  return {
    necessary: true,
    analytics: false,
    marketing: false,
    personalization: false,
    updatedAt: '',
  }
}

export function useGdprConsent() {
  const modalOpen = useState<boolean>('gdpr-consent-modal-open', () => false)
  const hydrated = useState<boolean>('gdpr-consent-hydrated', () => false)
  const consent = useState<GdprConsent>('gdpr-consent-value', defaultConsent)

  function loadFromStorage() {
    if (!import.meta.client || hydrated.value) return

    try {
      const raw = localStorage.getItem(CONSENT_STORAGE_KEY)
      if (!raw) {
        modalOpen.value = true
      } else {
        const parsed = JSON.parse(raw) as Partial<GdprConsent>
        consent.value = {
          necessary: true,
          analytics: Boolean(parsed.analytics),
          marketing: Boolean(parsed.marketing),
          personalization: Boolean(parsed.personalization),
          updatedAt: typeof parsed.updatedAt === 'string' ? parsed.updatedAt : '',
        }
      }
    } catch {
      modalOpen.value = true
    } finally {
      hydrated.value = true
    }
  }

  function persist(next: Omit<GdprConsent, 'necessary' | 'updatedAt'>) {
    const value: GdprConsent = {
      necessary: true,
      analytics: next.analytics,
      marketing: next.marketing,
      personalization: next.personalization,
      updatedAt: new Date().toISOString(),
    }
    consent.value = value

    if (import.meta.client) {
      localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(value))
    }
    modalOpen.value = false
  }

  function acceptAll() {
    persist({ analytics: true, marketing: true, personalization: true })
  }

  function rejectOptional() {
    persist({ analytics: false, marketing: false, personalization: false })
  }

  function saveCustom(custom: { analytics: boolean; marketing: boolean; personalization: boolean }) {
    persist(custom)
  }

  function openModal() {
    modalOpen.value = true
  }

  function closeModal() {
    modalOpen.value = false
  }

  return {
    modalOpen,
    consent,
    loadFromStorage,
    openModal,
    closeModal,
    acceptAll,
    rejectOptional,
    saveCustom,
  }
}
