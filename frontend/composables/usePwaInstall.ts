type PwaPlatform = 'ios' | 'android' | 'other'

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}

const DISMISS_UNTIL_KEY = 'doisense_pwa_dismiss_until'
const NEVER_SHOW_KEY = 'doisense_pwa_never_show'
const SESSION_PROMPT_TRACKED_KEY = 'doisense_pwa_prompt_tracked'
const SESSION_STANDALONE_TRACKED_KEY = 'doisense_pwa_standalone_tracked'
const DISMISS_TTL_MS = 7 * 24 * 60 * 60 * 1000

let initialized = false
let watchRegistered = false

const platform = ref<PwaPlatform>('other')
const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null)
const isStandalone = ref(false)
const dismissedUntil = ref(0)
const neverShow = ref(false)
const forceDebugBanner = ref(false)

function queryFlag(name: string): boolean {
  return new URLSearchParams(window.location.search).get(name) === '1'
}

function detectPlatform(): PwaPlatform {
  const userAgent = navigator.userAgent.toLowerCase()
  const isIosDevice = /iphone|ipad|ipod/.test(userAgent)
    || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)

  if (isIosDevice) return 'ios'
  if (/android/.test(userAgent)) return 'android'
  return 'other'
}

function detectStandaloneMode(): boolean {
  const nav = navigator as Navigator & { standalone?: boolean }
  return window.matchMedia('(display-mode: standalone)').matches || nav.standalone === true
}

function loadPreferences() {
  const rawDismissUntil = localStorage.getItem(DISMISS_UNTIL_KEY)
  const parsedDismissUntil = Number(rawDismissUntil || '0')
  dismissedUntil.value = Number.isFinite(parsedDismissUntil) ? parsedDismissUntil : 0
  neverShow.value = localStorage.getItem(NEVER_SHOW_KEY) === '1'
}

async function trackEvent(eventName: string, properties: Record<string, unknown>) {
  try {
    const { fetchApi } = useApi()
    await fetchApi('/analytics/track', {
      method: 'POST',
      body: {
        event_name: eventName,
        source: 'frontend',
        properties,
      },
    })
  } catch {
    // Analytics is best-effort only.
  }
}

function setupTrackingWatch(showBanner: ComputedRef<boolean>, canNativeInstall: ComputedRef<boolean>) {
  if (watchRegistered) {
    return
  }
  watchRegistered = true

  watch(showBanner, async (visible: boolean) => {
    if (!visible) {
      return
    }

    const alreadyTracked = sessionStorage.getItem(SESSION_PROMPT_TRACKED_KEY) === '1'
    if (alreadyTracked) {
      return
    }

    sessionStorage.setItem(SESSION_PROMPT_TRACKED_KEY, '1')
    await trackEvent('pwa_install_prompted', {
      platform: platform.value,
      trigger: forceDebugBanner.value
        ? 'debug_forced'
        : (canNativeInstall.value ? 'native_eligible' : 'manual_instructions'),
    })
  }, { immediate: true })
}

export function usePwaInstall() {
  const isIos = computed(() => platform.value === 'ios')
  const isAndroid = computed(() => platform.value === 'android')
  const canNativeInstall = computed(() => isAndroid.value && !!deferredPrompt.value)

  const showBanner = computed(() => {
    if (!import.meta.client) return false
    if (isStandalone.value) return false
    if (neverShow.value) return false
    if (dismissedUntil.value > Date.now()) return false
    if (forceDebugBanner.value) return true
    return isIos.value || isAndroid.value
  })

  async function init() {
    if (!import.meta.client || initialized) {
      return
    }
    initialized = true

    if (queryFlag('pwa_reset')) {
      localStorage.removeItem(DISMISS_UNTIL_KEY)
      localStorage.removeItem(NEVER_SHOW_KEY)
      sessionStorage.removeItem(SESSION_PROMPT_TRACKED_KEY)
      sessionStorage.removeItem(SESSION_STANDALONE_TRACKED_KEY)
    }

    forceDebugBanner.value = queryFlag('pwa_debug')

    platform.value = detectPlatform()
    isStandalone.value = detectStandaloneMode()
    loadPreferences()

    if (isStandalone.value && sessionStorage.getItem(SESSION_STANDALONE_TRACKED_KEY) !== '1') {
      sessionStorage.setItem(SESSION_STANDALONE_TRACKED_KEY, '1')
      await trackEvent('pwa_running_standalone', { platform: platform.value })
    }

    window.addEventListener('beforeinstallprompt', (event) => {
      event.preventDefault()
      deferredPrompt.value = event as BeforeInstallPromptEvent
    })

    window.addEventListener('appinstalled', () => {
      isStandalone.value = true
      neverShow.value = true
      localStorage.setItem(NEVER_SHOW_KEY, '1')
      deferredPrompt.value = null
      void trackEvent('pwa_install_accepted', {
        platform: platform.value,
        method: 'appinstalled_event',
      })
    })

    setupTrackingWatch(showBanner, canNativeInstall)
  }

  async function dismiss(neverAgain = false) {
    if (!import.meta.client) {
      return
    }

    if (neverAgain) {
      neverShow.value = true
      localStorage.setItem(NEVER_SHOW_KEY, '1')
    } else {
      const expiresAt = Date.now() + DISMISS_TTL_MS
      dismissedUntil.value = expiresAt
      localStorage.setItem(DISMISS_UNTIL_KEY, String(expiresAt))
    }

    await trackEvent('pwa_install_dismissed', {
      platform: platform.value,
      never_again: neverAgain,
    })
  }

  async function triggerInstall() {
    if (!deferredPrompt.value) {
      await markManualInstall()
      return
    }

    const promptEvent = deferredPrompt.value
    deferredPrompt.value = null

    await promptEvent.prompt()
    const choice = await promptEvent.userChoice

    if (choice.outcome === 'accepted') {
      neverShow.value = true
      localStorage.setItem(NEVER_SHOW_KEY, '1')
      await trackEvent('pwa_install_accepted', {
        platform: platform.value,
        method: 'native_prompt',
      })
      return
    }

    const expiresAt = Date.now() + DISMISS_TTL_MS
    dismissedUntil.value = expiresAt
    localStorage.setItem(DISMISS_UNTIL_KEY, String(expiresAt))
    await trackEvent('pwa_install_dismissed', {
      platform: platform.value,
      never_again: false,
    })
  }

  async function markManualInstall() {
    if (!import.meta.client) {
      return
    }

    neverShow.value = true
    localStorage.setItem(NEVER_SHOW_KEY, '1')
    await trackEvent('pwa_install_accepted', {
      platform: platform.value,
      method: 'manual_confirmed',
    })
  }

  return {
    init,
    showBanner,
    isIos,
    isAndroid,
    canNativeInstall,
    dismiss,
    triggerInstall,
    markManualInstall,
  }
}
