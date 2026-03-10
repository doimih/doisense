<template>
  <Teleport to="body">
    <div
      v-if="modalOpen"
      class="fixed inset-0 z-[120] flex items-end bg-stone-900/45 p-3 md:items-center md:justify-center"
      @click.self="closeModal"
    >
      <div class="w-full max-w-2xl rounded-2xl border border-stone-200 bg-white p-5 shadow-2xl md:p-6">
        <div class="mb-4">
          <h2 class="text-2xl font-bold text-stone-900">{{ text.title }}</h2>
          <p class="mt-2 text-sm text-stone-600">{{ text.subtitle }}</p>
        </div>

        <div class="space-y-3">
          <div class="rounded-xl border border-stone-200 bg-stone-50 p-3">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-stone-800">{{ text.necessaryTitle }}</p>
                <p class="text-xs text-stone-600">{{ text.necessaryDescription }}</p>
              </div>
              <span class="rounded-full bg-stone-800 px-3 py-1 text-xs font-semibold text-white">On</span>
            </div>
          </div>

          <div class="rounded-xl border border-stone-200 p-3">
            <label class="flex items-center justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-stone-800">{{ text.analyticsTitle }}</p>
                <p class="text-xs text-stone-600">{{ text.analyticsDescription }}</p>
              </div>
              <input v-model="draft.analytics" type="checkbox" class="h-4 w-4 accent-amber-600" />
            </label>
          </div>

          <div class="rounded-xl border border-stone-200 p-3">
            <label class="flex items-center justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-stone-800">{{ text.marketingTitle }}</p>
                <p class="text-xs text-stone-600">{{ text.marketingDescription }}</p>
              </div>
              <input v-model="draft.marketing" type="checkbox" class="h-4 w-4 accent-amber-600" />
            </label>
          </div>

          <div class="rounded-xl border border-stone-200 p-3">
            <label class="flex items-center justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-stone-800">{{ text.personalizationTitle }}</p>
                <p class="text-xs text-stone-600">{{ text.personalizationDescription }}</p>
              </div>
              <input v-model="draft.personalization" type="checkbox" class="h-4 w-4 accent-amber-600" />
            </label>
          </div>
        </div>

        <div class="mt-5 flex flex-wrap gap-2">
          <button type="button" class="rounded-lg bg-stone-900 px-4 py-2 text-sm font-semibold text-white" @click="acceptAll">
            {{ text.acceptAll }}
          </button>
          <button type="button" class="rounded-lg border border-stone-300 px-4 py-2 text-sm font-semibold text-stone-700" @click="rejectOptional">
            {{ text.rejectOptional }}
          </button>
          <button type="button" class="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white" @click="saveCustom(draft)">
            {{ text.savePreferences }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const consentCopy: Record<string, {
  title: string
  subtitle: string
  necessaryTitle: string
  necessaryDescription: string
  analyticsTitle: string
  analyticsDescription: string
  marketingTitle: string
  marketingDescription: string
  personalizationTitle: string
  personalizationDescription: string
  acceptAll: string
  rejectOptional: string
  savePreferences: string
}> = {
  ro: {
    title: 'Setări GDPR și cookie-uri',
    subtitle: 'Alege exact ce tipuri de date vrei să permiți. Poți schimba oricând opțiunile.',
    necessaryTitle: 'Strict necesare',
    necessaryDescription: 'Necesare pentru autentificare, securitate și funcționarea site-ului.',
    analyticsTitle: 'Analitice',
    analyticsDescription: 'Ne ajută să înțelegem cum folosești produsul și să îl îmbunătățim.',
    marketingTitle: 'Marketing',
    marketingDescription: 'Folosite pentru mesaje relevante și campanii personalizate.',
    personalizationTitle: 'Personalizare',
    personalizationDescription: 'Memorează preferințe și adaptează experiența în pagini.',
    acceptAll: 'Accept toate',
    rejectOptional: 'Refuz opționale',
    savePreferences: 'Salvează preferințele',
  },
  en: {
    title: 'GDPR and cookie settings',
    subtitle: 'Choose exactly what data categories you allow. You can update this anytime.',
    necessaryTitle: 'Strictly necessary',
    necessaryDescription: 'Required for authentication, security, and core site operation.',
    analyticsTitle: 'Analytics',
    analyticsDescription: 'Helps us understand usage and improve the product.',
    marketingTitle: 'Marketing',
    marketingDescription: 'Used for relevant messages and personalized campaigns.',
    personalizationTitle: 'Personalization',
    personalizationDescription: 'Remembers preferences and adapts the page experience.',
    acceptAll: 'Accept all',
    rejectOptional: 'Reject optional',
    savePreferences: 'Save preferences',
  },
  de: {
    title: 'DSGVO- und Cookie-Einstellungen',
    subtitle: 'Wähle genau aus, welche Datenkategorien erlaubt sind. Du kannst es jederzeit ändern.',
    necessaryTitle: 'Unbedingt erforderlich',
    necessaryDescription: 'Notwendig für Anmeldung, Sicherheit und den Kernbetrieb der Seite.',
    analyticsTitle: 'Analytik',
    analyticsDescription: 'Hilft uns, die Nutzung zu verstehen und das Produkt zu verbessern.',
    marketingTitle: 'Marketing',
    marketingDescription: 'Für relevante Nachrichten und personalisierte Kampagnen.',
    personalizationTitle: 'Personalisierung',
    personalizationDescription: 'Speichert Präferenzen und passt das Seitenerlebnis an.',
    acceptAll: 'Alles akzeptieren',
    rejectOptional: 'Optionale ablehnen',
    savePreferences: 'Präferenzen speichern',
  },
  it: {
    title: 'Impostazioni GDPR e cookie',
    subtitle: 'Scegli con precisione quali categorie di dati autorizzare. Puoi cambiare in qualsiasi momento.',
    necessaryTitle: 'Strettamente necessari',
    necessaryDescription: 'Necessari per autenticazione, sicurezza e funzionamento del sito.',
    analyticsTitle: 'Analitici',
    analyticsDescription: 'Ci aiutano a capire l\'uso del prodotto e migliorarlo.',
    marketingTitle: 'Marketing',
    marketingDescription: 'Usati per messaggi rilevanti e campagne personalizzate.',
    personalizationTitle: 'Personalizzazione',
    personalizationDescription: 'Memorizza preferenze e adatta l\'esperienza nelle pagine.',
    acceptAll: 'Accetta tutto',
    rejectOptional: 'Rifiuta opzionali',
    savePreferences: 'Salva preferenze',
  },
  es: {
    title: 'Configuración GDPR y cookies',
    subtitle: 'Elige exactamente qué categorías de datos permites. Puedes cambiarlo en cualquier momento.',
    necessaryTitle: 'Estrictamente necesarias',
    necessaryDescription: 'Necesarias para autenticación, seguridad y funcionamiento del sitio.',
    analyticsTitle: 'Analíticas',
    analyticsDescription: 'Nos ayudan a entender el uso del producto y mejorarlo.',
    marketingTitle: 'Marketing',
    marketingDescription: 'Usadas para mensajes relevantes y campañas personalizadas.',
    personalizationTitle: 'Personalización',
    personalizationDescription: 'Recuerda preferencias y adapta la experiencia en páginas.',
    acceptAll: 'Aceptar todo',
    rejectOptional: 'Rechazar opcionales',
    savePreferences: 'Guardar preferencias',
  },
  pl: {
    title: 'Ustawienia GDPR i cookies',
    subtitle: 'Wybierz dokładnie, na jakie kategorie danych się zgadzasz. Możesz to zmienić w każdej chwili.',
    necessaryTitle: 'Niezbędne',
    necessaryDescription: 'Wymagane do logowania, bezpieczeństwa i działania serwisu.',
    analyticsTitle: 'Analityczne',
    analyticsDescription: 'Pomagają zrozumieć użycie produktu i go ulepszać.',
    marketingTitle: 'Marketingowe',
    marketingDescription: 'Używane do trafnych komunikatów i kampanii personalizowanych.',
    personalizationTitle: 'Personalizacja',
    personalizationDescription: 'Zapamiętuje preferencje i dopasowuje doświadczenie w serwisie.',
    acceptAll: 'Akceptuj wszystko',
    rejectOptional: 'Odrzuć opcjonalne',
    savePreferences: 'Zapisz preferencje',
  },
}

const text = computed(() => consentCopy[localeCode.value] || consentCopy.en)
const { modalOpen, consent, loadFromStorage, closeModal, acceptAll, rejectOptional, saveCustom } = useGdprConsent()

const draft = ref({
  analytics: false,
  marketing: false,
  personalization: false,
})

watch(
  () => modalOpen.value,
  (open) => {
    if (!open) return
    draft.value = {
      analytics: consent.value.analytics,
      marketing: consent.value.marketing,
      personalization: consent.value.personalization,
    }
  },
  { immediate: true },
)

onMounted(() => {
  loadFromStorage()
})
</script>
