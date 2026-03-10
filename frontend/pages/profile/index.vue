<template>
  <div class="max-w-xl mx-auto space-y-4">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">{{ $t('nav.profile') }}</h1>

    <div v-if="authStore.user" class="space-y-4 rounded-xl border border-stone-200 bg-white p-4">
      <div class="flex items-center justify-between">
        <p><span class="font-medium">{{ $t('auth.email') }}:</span> {{ authStore.user.email }}</p>
        <span class="inline-flex items-center gap-2 rounded-full border border-stone-200 px-3 py-1 text-xs font-medium text-stone-700">
          <span class="h-2.5 w-2.5 rounded-full bg-emerald-500" />
          {{ authStore.user.membership_tier === 'premium' ? text.membershipPremium : text.membershipStandard }}
        </span>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.firstName }}</label>
          <input v-model="firstName" type="text" class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.lastName }}</label>
          <input v-model="lastName" type="text" class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.phone }}</label>
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

      <div class="rounded-lg border border-stone-200 bg-stone-50 p-3 text-sm text-stone-700">
        <p class="font-medium text-stone-800">{{ text.savedCard }}</p>
        <p v-if="cardLoading" class="mt-1">{{ $t('common.loading') }}</p>
        <template v-else-if="savedCard?.has_saved_card && savedCard.card">
          <p class="mt-1">{{ savedCard.card.brand?.toUpperCase() }} •••• {{ savedCard.card.last4 }}</p>
          <p>{{ text.expires }}: {{ savedCard.card.exp_month }}/{{ savedCard.card.exp_year }}</p>
          <button
            type="button"
            :disabled="billingPortalLoading"
            class="mt-3 inline-flex px-3 py-1.5 rounded-md border border-stone-300 hover:bg-white disabled:opacity-50"
            @click="openBillingPortal"
          >
            {{ billingPortalLoading ? $t('common.loading') : text.manageCard }}
          </button>
        </template>
        <p v-else class="mt-1">{{ text.noCard }}</p>
      </div>

      <p v-if="saveError" class="text-sm text-red-600">{{ saveError }}</p>
      <p v-if="saveSuccess" class="text-sm text-emerald-700">{{ saveSuccess }}</p>

      <button
        type="button"
        :disabled="saveLoading"
        class="px-4 py-2 bg-stone-800 text-white rounded-lg hover:bg-stone-900 disabled:opacity-50"
        @click="saveProfile"
      >
        {{ saveLoading ? $t('common.loading') : text.saveProfile }}
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
        <h2 class="text-base font-semibold text-stone-800">{{ text.passwordChange }}</h2>

        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.currentPassword }}</label>
          <input
            v-model="currentPassword"
            type="password"
            class="w-full rounded-lg border border-stone-300 px-3 py-2"
          />
        </div>

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.newPassword }}</label>
            <input
              v-model="newPassword"
              type="password"
              class="w-full rounded-lg border border-stone-300 px-3 py-2"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.confirmNewPassword }}</label>
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
          {{ passwordLoading ? $t('common.loading') : text.changePassword }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const { fetchApi } = useApi()
const { locale } = useI18n()
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

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const profileCopy: Record<string, {
  membershipPremium: string
  membershipStandard: string
  firstName: string
  lastName: string
  phone: string
  savedCard: string
  expires: string
  manageCard: string
  noCard: string
  saveProfile: string
  passwordChange: string
  currentPassword: string
  newPassword: string
  confirmNewPassword: string
  changePassword: string
  saveSuccess: string
  saveError: string
  passwordSuccess: string
  passwordError: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    membershipPremium: 'Membru Premium', membershipStandard: 'Membru Standard', firstName: 'Prenume', lastName: 'Nume', phone: 'Telefon contact',
    savedCard: 'Card salvat', expires: 'Expira', manageCard: 'Gestioneaza cardul', noCard: 'Nu exista card salvat inca.', saveProfile: 'Salveaza profilul',
    passwordChange: 'Schimbare parola', currentPassword: 'Parola curenta', newPassword: 'Parola noua', confirmNewPassword: 'Confirmare parola noua', changePassword: 'Schimba parola',
    saveSuccess: 'Profilul a fost actualizat.', saveError: 'Nu am putut salva profilul.', passwordSuccess: 'Parola a fost schimbata cu succes.', passwordError: 'Nu am putut schimba parola.',
    seoTitle: 'Profil utilizator - Doisense', seoDescription: 'Panou de cont pentru utilizatori autentificati Doisense.',
  },
  en: {
    membershipPremium: 'Premium member', membershipStandard: 'Standard member', firstName: 'First name', lastName: 'Last name', phone: 'Contact phone',
    savedCard: 'Saved card', expires: 'Expires', manageCard: 'Manage card', noCard: 'No saved card yet.', saveProfile: 'Save profile',
    passwordChange: 'Change password', currentPassword: 'Current password', newPassword: 'New password', confirmNewPassword: 'Confirm new password', changePassword: 'Change password',
    saveSuccess: 'Profile updated.', saveError: 'Could not save profile.', passwordSuccess: 'Password changed successfully.', passwordError: 'Could not change password.',
    seoTitle: 'User profile - Doisense', seoDescription: 'Account dashboard for authenticated Doisense users.',
  },
  de: {
    membershipPremium: 'Premium-Mitglied', membershipStandard: 'Standard-Mitglied', firstName: 'Vorname', lastName: 'Nachname', phone: 'Kontakttelefon',
    savedCard: 'Gespeicherte Karte', expires: 'Ablauf', manageCard: 'Karte verwalten', noCard: 'Noch keine Karte gespeichert.', saveProfile: 'Profil speichern',
    passwordChange: 'Passwort ändern', currentPassword: 'Aktuelles Passwort', newPassword: 'Neues Passwort', confirmNewPassword: 'Neues Passwort bestätigen', changePassword: 'Passwort ändern',
    saveSuccess: 'Profil wurde aktualisiert.', saveError: 'Profil konnte nicht gespeichert werden.', passwordSuccess: 'Passwort erfolgreich geändert.', passwordError: 'Passwort konnte nicht geändert werden.',
    seoTitle: 'Benutzerprofil - Doisense', seoDescription: 'Kontodashboard für angemeldete Doisense-Nutzer.',
  },
  fr: {
    membershipPremium: 'Membre Premium', membershipStandard: 'Membre Standard', firstName: 'Prenom', lastName: 'Nom', phone: 'Telephone de contact',
    savedCard: 'Carte enregistree', expires: 'Expire', manageCard: 'Gerer la carte', noCard: 'Aucune carte enregistree pour le moment.', saveProfile: 'Enregistrer le profil',
    passwordChange: 'Changer le mot de passe', currentPassword: 'Mot de passe actuel', newPassword: 'Nouveau mot de passe', confirmNewPassword: 'Confirmer le nouveau mot de passe', changePassword: 'Changer le mot de passe',
    saveSuccess: 'Profil mis a jour.', saveError: 'Impossible d\'enregistrer le profil.', passwordSuccess: 'Mot de passe modifie avec succes.', passwordError: 'Impossible de modifier le mot de passe.',
    seoTitle: 'Profil utilisateur - Doisense', seoDescription: 'Tableau de bord du compte pour les utilisateurs connectes de Doisense.',
  },
  it: {
    membershipPremium: 'Membro Premium', membershipStandard: 'Membro Standard', firstName: 'Nome', lastName: 'Cognome', phone: 'Telefono di contatto',
    savedCard: 'Carta salvata', expires: 'Scadenza', manageCard: 'Gestisci carta', noCard: 'Nessuna carta salvata.', saveProfile: 'Salva profilo',
    passwordChange: 'Cambia password', currentPassword: 'Password attuale', newPassword: 'Nuova password', confirmNewPassword: 'Conferma nuova password', changePassword: 'Cambia password',
    saveSuccess: 'Profilo aggiornato.', saveError: 'Impossibile salvare il profilo.', passwordSuccess: 'Password cambiata con successo.', passwordError: 'Impossibile cambiare la password.',
    seoTitle: 'Profilo utente - Doisense', seoDescription: 'Pannello account per utenti autenticati Doisense.',
  },
  es: {
    membershipPremium: 'Miembro Premium', membershipStandard: 'Miembro Standard', firstName: 'Nombre', lastName: 'Apellido', phone: 'Telefono de contacto',
    savedCard: 'Tarjeta guardada', expires: 'Caduca', manageCard: 'Gestionar tarjeta', noCard: 'Aun no hay tarjeta guardada.', saveProfile: 'Guardar perfil',
    passwordChange: 'Cambiar contraseña', currentPassword: 'Contraseña actual', newPassword: 'Nueva contraseña', confirmNewPassword: 'Confirmar nueva contraseña', changePassword: 'Cambiar contraseña',
    saveSuccess: 'Perfil actualizado.', saveError: 'No se pudo guardar el perfil.', passwordSuccess: 'Contraseña cambiada correctamente.', passwordError: 'No se pudo cambiar la contraseña.',
    seoTitle: 'Perfil de usuario - Doisense', seoDescription: 'Panel de cuenta para usuarios autenticados de Doisense.',
  },
  pl: {
    membershipPremium: 'Czlonek Premium', membershipStandard: 'Czlonek Standard', firstName: 'Imie', lastName: 'Nazwisko', phone: 'Telefon kontaktowy',
    savedCard: 'Zapisana karta', expires: 'Wazna do', manageCard: 'Zarzadzaj karta', noCard: 'Brak zapisanej karty.', saveProfile: 'Zapisz profil',
    passwordChange: 'Zmiana hasla', currentPassword: 'Aktualne haslo', newPassword: 'Nowe haslo', confirmNewPassword: 'Potwierdz nowe haslo', changePassword: 'Zmien haslo',
    saveSuccess: 'Profil zaktualizowany.', saveError: 'Nie udalo sie zapisac profilu.', passwordSuccess: 'Haslo zostalo zmienione.', passwordError: 'Nie udalo sie zmienic hasla.',
    seoTitle: 'Profil uzytkownika - Doisense', seoDescription: 'Panel konta dla zalogowanych uzytkownikow Doisense.',
  },
}

const text = computed(() => profileCopy[localeCode.value] || profileCopy.en)

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
  title: computed(() => text.value.seoTitle),
  description: computed(() => text.value.seoDescription),
  noindex: true,
})

watch(
  () => authStore.user,
  (user) => {
    firstName.value = user?.first_name || ''
    lastName.value = user?.last_name || ''
    phoneContact.value = user?.phone_contact || ''
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
    }>('/me', {
      method: 'PATCH',
      body: {
        first_name: firstName.value,
        last_name: lastName.value,
        phone_contact: phoneContact.value,
      },
    })

    if (authStore.user) {
      authStore.setUser({
        ...authStore.user,
        first_name: updated.first_name,
        last_name: updated.last_name,
        phone_contact: updated.phone_contact,
      })
    }
    saveSuccess.value = text.value.saveSuccess
  } catch {
    saveError.value = text.value.saveError
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
    passwordSuccess.value = text.value.passwordSuccess
  } catch (error: any) {
    passwordError.value = error?.data?.detail || text.value.passwordError
  } finally {
    passwordLoading.value = false
  }
}
</script>
