<template>
  <div class="max-w-xl mx-auto space-y-4">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">{{ $t('nav.profile') }}</h1>

    <div v-if="authStore.user" class="space-y-4 rounded-xl border border-stone-200 bg-white p-4">
      <div class="flex items-center justify-between">
        <p><span class="font-medium">{{ $t('auth.email') }}:</span> {{ authStore.user.email }}</p>
        <span class="inline-flex items-center gap-2 rounded-full border border-stone-200 px-3 py-1 text-xs font-medium text-stone-700">
          <span class="h-2.5 w-2.5 rounded-full bg-emerald-500" />
          {{ authStore.user.membership_tier === 'premium' ? 'Membru Premium' : 'Membru Normal' }}
        </span>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">Prenume</label>
          <input v-model="firstName" type="text" class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">Nume</label>
          <input v-model="lastName" type="text" class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-stone-700">Telefon contact</label>
        <input
          v-model="phoneContact"
          type="tel"
          placeholder="+40 712 345 678"
          class="w-full rounded-lg border border-stone-300 px-3 py-2"
        />
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="dialCode in dialCodeOptions"
            :key="dialCode.value"
            type="button"
            class="rounded-md border border-stone-300 px-2 py-1 text-xs text-stone-700 hover:bg-stone-50"
            @click="setPhoneDialCode(dialCode.value)"
          >
            {{ dialCode.label }}
          </button>
        </div>
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-stone-700">Zona fiscala</label>
        <input v-model="taxRegion" type="text" class="w-full rounded-lg border border-stone-300 px-3 py-2" />
      </div>

      <div class="rounded-lg border border-stone-200 bg-stone-50 p-3 text-sm text-stone-700">
        <p class="font-medium text-stone-800">Card salvat</p>
        <p v-if="cardLoading" class="mt-1">{{ $t('common.loading') }}</p>
        <template v-else-if="savedCard?.has_saved_card && savedCard.card">
          <p class="mt-1">{{ savedCard.card.brand?.toUpperCase() }} •••• {{ savedCard.card.last4 }}</p>
          <p>Expira: {{ savedCard.card.exp_month }}/{{ savedCard.card.exp_year }}</p>
          <button
            type="button"
            :disabled="billingPortalLoading"
            class="mt-3 inline-flex px-3 py-1.5 rounded-md border border-stone-300 hover:bg-white disabled:opacity-50"
            @click="openBillingPortal"
          >
            {{ billingPortalLoading ? $t('common.loading') : 'Gestioneaza cardul' }}
          </button>
        </template>
        <p v-else class="mt-1">Nu exista card salvat inca.</p>
      </div>

      <p v-if="saveError" class="text-sm text-red-600">{{ saveError }}</p>
      <p v-if="saveSuccess" class="text-sm text-emerald-700">{{ saveSuccess }}</p>

      <button
        type="button"
        :disabled="saveLoading"
        class="px-4 py-2 bg-stone-800 text-white rounded-lg hover:bg-stone-900 disabled:opacity-50"
        @click="saveProfile"
      >
        {{ saveLoading ? $t('common.loading') : 'Salveaza profilul' }}
      </button>

      <p><span class="font-medium">{{ $t('profile.premium') }}:</span> {{ authStore.user.is_premium ? $t('common.yes') : $t('common.no') }}</p>
      <button
        v-if="!authStore.user.is_premium"
        :disabled="checkoutLoading"
        class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
        @click="createCheckout"
      >
        {{ checkoutLoading ? $t('common.loading') : $t('profile.upgrade') }}
      </button>

      <div class="space-y-3 rounded-lg border border-stone-200 bg-stone-50 p-4">
        <h2 class="text-base font-semibold text-stone-800">Schimbare parola</h2>

        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">Parola curenta</label>
          <input
            v-model="currentPassword"
            type="password"
            class="w-full rounded-lg border border-stone-300 px-3 py-2"
          />
        </div>

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm font-medium text-stone-700">Parola noua</label>
            <input
              v-model="newPassword"
              type="password"
              class="w-full rounded-lg border border-stone-300 px-3 py-2"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-stone-700">Confirmare parola noua</label>
            <input
              v-model="newPasswordConfirm"
              type="password"
              class="w-full rounded-lg border border-stone-300 px-3 py-2"
            />
          </div>
        </div>

        <p v-if="passwordError" class="text-sm text-red-600">{{ passwordError }}</p>
        <p v-if="passwordSuccess" class="text-sm text-emerald-700">{{ passwordSuccess }}</p>

        <button
          type="button"
          :disabled="passwordLoading"
          class="px-4 py-2 bg-stone-800 text-white rounded-lg hover:bg-stone-900 disabled:opacity-50"
          @click="changePassword"
        >
          {{ passwordLoading ? $t('common.loading') : 'Schimba parola' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const { fetchApi } = useApi()
const checkoutLoading = ref(false)
const saveLoading = ref(false)
const cardLoading = ref(false)
const billingPortalLoading = ref(false)
const passwordLoading = ref(false)
const saveError = ref('')
const saveSuccess = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

const dialCodeOptions = [
  { value: '+40', label: 'RO +40' },
  { value: '+44', label: 'UK +44' },
  { value: '+49', label: 'DE +49' },
  { value: '+39', label: 'IT +39' },
  { value: '+34', label: 'ES +34' },
  { value: '+48', label: 'PL +48' },
  { value: '+33', label: 'FR +33' },
  { value: '+1', label: 'US/CA +1' },
]

const firstName = ref(authStore.user?.first_name || '')
const lastName = ref(authStore.user?.last_name || '')
const phoneContact = ref(authStore.user?.phone_contact || '')
const taxRegion = ref(authStore.user?.tax_region || '')

const currentPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')

type SavedCardResponse = {
  has_saved_card: boolean
  card: null | {
    brand: string | null
    last4: string | null
    exp_month: number | null
    exp_year: number | null
    country: string | null
  }
}

const savedCard = ref<SavedCardResponse | null>(null)

function getDefaultDialCode() {
  const language = (authStore.user?.language || 'ro').slice(0, 2).toLowerCase()
  if (language === 'de') return '+49'
  if (language === 'it') return '+39'
  if (language === 'es') return '+34'
  if (language === 'pl') return '+48'
  return '+40'
}

function ensurePhonePrefix() {
  if (phoneContact.value.trim()) return
  phoneContact.value = `${getDefaultDialCode()} `
}

function setPhoneDialCode(code: string) {
  const raw = phoneContact.value.trim()
  if (!raw) {
    phoneContact.value = `${code} `
    return
  }

  if (raw.startsWith('+')) {
    const updated = raw.replace(/^\+\d{1,4}/, code).trim()
    phoneContact.value = updated === code ? `${code} ` : updated
    return
  }

  phoneContact.value = `${code} ${raw}`
}

usePublicSeo({
  title: 'Profil utilizator - Doisense',
  description: 'Panou de cont pentru utilizatori autentificati Doisense.',
  noindex: true,
})

watch(
  () => authStore.user,
  (user) => {
    firstName.value = user?.first_name || ''
    lastName.value = user?.last_name || ''
    phoneContact.value = user?.phone_contact || ''
    taxRegion.value = user?.tax_region || ''
    ensurePhonePrefix()
  },
  { immediate: true },
)

onMounted(async () => {
  await loadSavedCard()
})

async function loadSavedCard() {
  cardLoading.value = true
  try {
    savedCard.value = await fetchApi<SavedCardResponse>('/payments/saved-card')
  } catch {
    savedCard.value = { has_saved_card: false, card: null }
  } finally {
    cardLoading.value = false
  }
}

async function saveProfile() {
  saveLoading.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    const updated = await fetchApi<{
      first_name: string
      last_name: string
      phone_contact: string
      tax_region: string
    }>('/me', {
      method: 'PATCH',
      body: {
        first_name: firstName.value,
        last_name: lastName.value,
        phone_contact: phoneContact.value,
        tax_region: taxRegion.value,
      },
    })

    if (authStore.user) {
      authStore.setUser({
        ...authStore.user,
        first_name: updated.first_name,
        last_name: updated.last_name,
        phone_contact: updated.phone_contact,
        tax_region: updated.tax_region,
      })
    }
    saveSuccess.value = 'Profilul a fost actualizat.'
  } catch {
    saveError.value = 'Nu am putut salva profilul.'
  } finally {
    saveLoading.value = false
  }
}

async function createCheckout() {
  checkoutLoading.value = true
  try {
    const res = await fetchApi<{ url: string }>('/payments/create-checkout-session', { method: 'POST' })
    if (res?.url) window.location.href = res.url
  } finally {
    checkoutLoading.value = false
  }
}

async function openBillingPortal() {
  billingPortalLoading.value = true
  try {
    const res = await fetchApi<{ url: string }>('/payments/create-billing-portal-session', {
      method: 'POST',
    })
    if (res?.url) {
      window.location.href = res.url
    }
  } catch {
    // Ignore here; user still has profile data in place.
  } finally {
    billingPortalLoading.value = false
  }
}

async function changePassword() {
  passwordLoading.value = true
  passwordError.value = ''
  passwordSuccess.value = ''
  try {
    await fetchApi<{ detail: string }>('/me/change-password', {
      method: 'POST',
      body: {
        current_password: currentPassword.value,
        new_password: newPassword.value,
        new_password_confirm: newPasswordConfirm.value,
      },
    })
    currentPassword.value = ''
    newPassword.value = ''
    newPasswordConfirm.value = ''
    passwordSuccess.value = 'Parola a fost schimbata cu succes.'
  } catch (error: any) {
    passwordError.value = error?.data?.detail || 'Nu am putut schimba parola.'
  } finally {
    passwordLoading.value = false
  }
}
</script>
