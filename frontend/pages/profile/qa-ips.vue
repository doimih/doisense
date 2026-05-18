<template>
  <section class="mx-auto max-w-3xl space-y-6 rounded-2xl border border-sky-100 bg-gradient-to-br from-[#f7fbff] via-[#f5f9fc] to-[#eef4f8] p-4 md:p-6">
    <!-- Header -->
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">{{ t.title }}</h1>
        <p class="mt-1 text-sm text-slate-600">{{ t.subtitle }}</p>
      </div>
      <NuxtLink
        :to="localePath('/profile/settings')"
        class="rounded-lg border border-sky-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-sky-50"
      >
        {{ t.backToSettings }}
      </NuxtLink>
    </div>

    <!-- Admin guard -->
    <div v-if="!authStore.user?.is_superuser" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      {{ t.adminOnly }}
    </div>

    <template v-else>
      <!-- Info banner -->
      <div class="rounded-xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900">
        {{ t.info }}
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="rounded-xl border border-sky-200 bg-white p-6 text-center text-sm text-slate-500">
        {{ t.loading }}
      </div>

      <template v-else>
        <!-- Current IP list -->
        <div class="rounded-xl border border-sky-200 bg-white p-4 shadow-sm">
          <h2 class="mb-3 text-base font-semibold text-slate-800">{{ t.currentList }}</h2>

          <div v-if="!ips.length" class="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
            {{ t.emptyList }}
          </div>

          <ul v-else class="space-y-2">
            <li
              v-for="ip in ips"
              :key="ip"
              class="flex items-center justify-between rounded-lg border border-sky-100 bg-sky-50 px-3 py-2"
            >
              <span class="font-mono text-sm text-slate-800">{{ ip }}</span>
              <button
                type="button"
                class="ml-3 rounded-md border border-red-200 bg-white px-2.5 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50"
                :disabled="saving"
                @click="removeIp(ip)"
              >
                {{ t.remove }}
              </button>
            </li>
          </ul>
        </div>

        <!-- Add new IP -->
        <div class="rounded-xl border border-sky-200 bg-white p-4 shadow-sm">
          <h2 class="mb-3 text-base font-semibold text-slate-800">{{ t.addTitle }}</h2>
          <form class="flex flex-wrap gap-2" @submit.prevent="addIp">
            <input
              v-model="newIp"
              type="text"
              :placeholder="t.placeholder"
              class="flex-1 min-w-0 rounded-lg border border-slate-300 bg-white px-3 py-2 font-mono text-sm text-slate-800 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-200"
              :disabled="saving"
              autocomplete="off"
            >
            <button
              type="submit"
              :disabled="saving || !newIp.trim()"
              class="rounded-lg bg-sky-300 px-4 py-2 text-sm font-semibold text-stone-900 transition hover:bg-sky-200 disabled:opacity-50"
            >
              {{ t.add }}
            </button>
          </form>
          <p v-if="inputError" class="mt-2 text-xs text-red-600">{{ inputError }}</p>
        </div>

        <!-- Save button -->
        <div class="flex items-center gap-3">
          <button
            type="button"
            :disabled="saving"
            class="rounded-lg bg-sky-400 px-5 py-2.5 text-sm font-semibold text-white shadow transition hover:bg-sky-500 disabled:opacity-50"
            @click="saveList"
          >
            {{ saving ? t.saving : t.save }}
          </button>
          <p v-if="saveError" class="text-sm text-red-600">{{ saveError }}</p>
          <p v-if="saveSuccess" class="text-sm text-emerald-700">{{ saveSuccess }}</p>
        </div>
      </template>
    </template>
  </section>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { fetchApi } = useApi()
const authStore = useAuthStore()
const localePath = useLocalePath()
const { locale } = useI18n()

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const translations: Record<string, Record<string, string>> = {
  ro: {
    title: 'Acces QA — Whitelist IP',
    subtitle: 'Gestioneaza adresele IP care pot accesa API-ul platformei in modul QA.',
    backToSettings: 'Inapoi la setari',
    adminOnly: 'Aceasta sectiune este disponibila doar pentru conturile admin.',
    info: 'Daca lista este goala, orice IP poate accesa platforma. Adauga adrese IPv4/IPv6 sau retele CIDR (ex: 10.0.0.0/8). Doar IP-urile din aceasta lista vor putea apela API-ul.',
    loading: 'Se incarca...',
    currentList: 'IP-uri permise',
    emptyList: 'Nicio restrictie activa. Orice IP are acces la API.',
    remove: 'Sterge',
    addTitle: 'Adauga IP sau CIDR',
    placeholder: 'ex: 203.0.113.10 sau 10.0.0.0/8',
    add: 'Adauga',
    save: 'Salveaza lista',
    saving: 'Se salveaza...',
    invalidIp: 'Adresa IP sau CIDR invalida.',
    alreadyAdded: 'Aceasta adresa este deja in lista.',
    saveSuccess: 'Lista salvata cu succes.',
    saveError: 'Eroare la salvare. Incearca din nou.',
    serverError: 'Intrari invalide returnate de server:',
  },
  en: {
    title: 'QA Access — IP Whitelist',
    subtitle: 'Manage IP addresses allowed to access the platform API in QA mode.',
    backToSettings: 'Back to settings',
    adminOnly: 'This section is available only for admin accounts.',
    info: 'If the list is empty, any IP can access the platform. Add IPv4/IPv6 addresses or CIDR networks (e.g. 10.0.0.0/8). Only IPs on this list will be able to call the API.',
    loading: 'Loading...',
    currentList: 'Allowed IPs',
    emptyList: 'No restrictions active. Any IP can access the API.',
    remove: 'Remove',
    addTitle: 'Add IP or CIDR',
    placeholder: 'e.g. 203.0.113.10 or 10.0.0.0/8',
    add: 'Add',
    save: 'Save list',
    saving: 'Saving...',
    invalidIp: 'Invalid IP address or CIDR.',
    alreadyAdded: 'This address is already in the list.',
    saveSuccess: 'List saved successfully.',
    saveError: 'Error saving. Please try again.',
    serverError: 'Invalid entries returned by server:',
  },
  de: {
    title: 'QA-Zugang — IP-Whitelist',
    subtitle: 'Verwaltung der IP-Adressen, die im QA-Modus auf die Plattform-API zugreifen duerfen.',
    backToSettings: 'Zurueck zu Einstellungen',
    adminOnly: 'Dieser Bereich ist nur fuer Admin-Konten verfuegbar.',
    info: 'Wenn die Liste leer ist, kann jede IP auf die Plattform zugreifen. IPv4/IPv6-Adressen oder CIDR-Netzwerke hinzufuegen (z.B. 10.0.0.0/8).',
    loading: 'Wird geladen...',
    currentList: 'Erlaubte IPs',
    emptyList: 'Keine Einschraenkungen aktiv. Jede IP kann auf die API zugreifen.',
    remove: 'Entfernen',
    addTitle: 'IP oder CIDR hinzufuegen',
    placeholder: 'z.B. 203.0.113.10 oder 10.0.0.0/8',
    add: 'Hinzufuegen',
    save: 'Liste speichern',
    saving: 'Wird gespeichert...',
    invalidIp: 'Ungueltige IP-Adresse oder CIDR.',
    alreadyAdded: 'Diese Adresse ist bereits in der Liste.',
    saveSuccess: 'Liste erfolgreich gespeichert.',
    saveError: 'Fehler beim Speichern. Bitte erneut versuchen.',
    serverError: 'Vom Server zurueckgegebene ungueltige Eintraege:',
  },
}

const t = computed(() => translations[localeCode.value] ?? translations.en)

type QaIpsResponse = {
  ips?: string[]
}

// State
const ips = ref<string[]>([])
const newIp = ref('')
const inputError = ref('')
const loading = ref(false)
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref('')

// Rough client-side validation (server validates authoritatively)
function isValidIpOrCidr(value: string): boolean {
  const ipv4 = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/
  const ipv6 = /^[0-9a-fA-F:]+(\/.{1,3})?$/
  return ipv4.test(value) || ipv6.test(value)
}

async function loadList() {
  loading.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const data = await fetchApi<QaIpsResponse>('/api/settings/qa-ips')
    ips.value = data?.ips ?? []
  }
  catch {
    saveError.value = t.value.saveError
  }
  finally {
    loading.value = false
  }
}

function addIp() {
  const entry = newIp.value.trim()
  inputError.value = ''
  if (!entry) return

  if (!isValidIpOrCidr(entry)) {
    inputError.value = t.value.invalidIp
    return
  }
  if (ips.value.includes(entry)) {
    inputError.value = t.value.alreadyAdded
    return
  }
  ips.value = [...ips.value, entry]
  newIp.value = ''
}

function removeIp(ip: string) {
  ips.value = ips.value.filter(i => i !== ip)
}

async function saveList() {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const data = await fetchApi<QaIpsResponse>('/api/settings/qa-ips', {
      method: 'PUT',
      body: JSON.stringify({ ips: ips.value }),
    })
    ips.value = data?.ips ?? ips.value
    saveSuccess.value = t.value.saveSuccess
  }
  catch (err: any) {
    const detail = err?.data?.detail || err?.message || ''
    const invalid = err?.data?.invalid
    if (invalid?.length) {
      saveError.value = `${t.value.serverError} ${invalid.join(', ')}`
    }
    else {
      saveError.value = detail || t.value.saveError
    }
  }
  finally {
    saving.value = false
  }
}

onMounted(() => {
  if (authStore.user?.is_superuser) {
    loadList()
  }
})
</script>
