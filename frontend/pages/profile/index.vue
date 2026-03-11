<template>
  <div class="max-w-xl mx-auto space-y-4 rounded-2xl border border-sky-100 bg-gradient-to-br from-[#f7fbff] via-[#f5f9fc] to-[#eef4f8] p-4 md:p-5">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-2xl font-bold text-slate-900">{{ $t('nav.profile') }}</h1>
    </div>

    <div v-if="authStore.user" class="space-y-4 rounded-xl border border-sky-200 bg-white/95 p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <p><span class="font-medium">{{ $t('auth.email') }}:</span> {{ authStore.user.email }}</p>
        <span
          :class="[
            'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium',
            authStore.user.membership_tier === 'trial'
              ? 'border-amber-300 bg-amber-50 text-amber-800'
              : ['basic','premium','vip'].includes(authStore.user.membership_tier)
                ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
                : 'border-stone-200 bg-stone-50 text-stone-600',
          ]"
        >
          <span
            :class="[
              'h-2.5 w-2.5 rounded-full',
              authStore.user.membership_tier === 'trial' ? 'bg-amber-400' : ['basic','premium','vip'].includes(authStore.user.membership_tier) ? 'bg-emerald-500' : 'bg-stone-400',
            ]"
          />
          {{ planTierLabel }}
        </span>
      </div>

      <!-- Trial countdown banner -->
      <div v-if="authStore.user.membership_tier === 'trial' && trialDaysLeft !== null" class="rounded-lg border border-amber-200 bg-amber-50/80 p-3 text-sm">
        <p class="font-medium text-amber-900">{{ text.trialActive }}</p>
        <p class="mt-0.5 text-amber-700">{{ trialDaysLeft > 0 ? text.trialDaysLeft.replace('{n}', String(trialDaysLeft)) : text.trialLastDay }}</p>
        <NuxtLink :to="localePath('/pricing')" class="mt-2 inline-block text-xs font-semibold text-sky-700 hover:underline">
          {{ text.trialUpgradeNow }} →
        </NuxtLink>
      </div>

      <!-- Free (expired trial / no subscription) upgrade prompt -->
      <div v-if="authStore.user.membership_tier === 'free'" class="rounded-lg border border-stone-200 bg-stone-50 p-3 text-sm">
        <p class="font-medium text-stone-900">{{ text.freeNotice }}</p>
        <NuxtLink :to="localePath('/pricing')" class="mt-2 inline-block text-xs font-semibold text-sky-700 hover:underline">
          {{ text.choosePlan }} →
        </NuxtLink>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">{{ text.firstName }}</label>
          <input v-model="firstName" type="text" class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-800 focus:border-sky-300 focus:outline-none focus:ring-2 focus:ring-sky-100" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">{{ text.lastName }}</label>
          <input v-model="lastName" type="text" class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-800 focus:border-sky-300 focus:outline-none focus:ring-2 focus:ring-sky-100" />
        </div>
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-slate-700">{{ text.phone }}</label>
        <input
          v-model="phoneContact"
          type="tel"
          placeholder="+40 712 345 678"
          class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-800 focus:border-sky-300 focus:outline-none focus:ring-2 focus:ring-sky-100"
        />
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="dialCode in dialCodeOptions"
            :key="dialCode.value"
            type="button"
            class="rounded-md border border-sky-200 bg-white px-2 py-1 text-xs text-slate-700 transition hover:bg-sky-50"
            @click="setPhoneDialCode(dialCode.value)"
          >
            {{ dialCode.label }}
          </button>
        </div>
      </div>

      <div class="rounded-lg border border-sky-200 bg-sky-50/70 p-3 text-sm text-slate-700">
        <p class="font-medium text-slate-900">{{ text.savedCard }}</p>
        <p v-if="cardLoading" class="mt-1">{{ $t('common.loading') }}</p>
        <template v-else-if="savedCard?.has_saved_card && savedCard.card">
          <p class="mt-1">{{ savedCard.card.brand?.toUpperCase() }} •••• {{ savedCard.card.last4 }}</p>
          <p>{{ text.expires }}: {{ savedCard.card.exp_month }}/{{ savedCard.card.exp_year }}</p>
          <button
            type="button"
            :disabled="billingPortalLoading"
            class="mt-3 inline-flex rounded-md border border-sky-200 bg-white px-3 py-1.5 text-slate-700 transition hover:bg-sky-50 disabled:opacity-50"
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
        class="rounded-lg bg-sky-300 px-4 py-2 font-medium text-stone-900 transition hover:bg-sky-200 disabled:opacity-50"
        @click="saveProfile"
      >
        {{ saveLoading ? $t('common.loading') : text.saveProfile }}
      </button>

      <!-- Upgrade section: show for trial or free users -->
      <div v-if="['trial', 'free'].includes(authStore.user.membership_tier)" class="space-y-2 rounded-lg border border-sky-200 bg-sky-50/60 p-4">
        <p class="text-sm font-semibold text-slate-900">{{ text.upgradeTo }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="plan in upgradePlans"
            :key="plan.key"
            type="button"
            :disabled="checkoutLoading === plan.key"
            class="rounded-full border border-sky-300 bg-white px-3 py-1.5 text-xs font-semibold text-sky-800 transition hover:bg-sky-100 disabled:opacity-50"
            @click="createCheckout(plan.key)"
          >
            {{ checkoutLoading === plan.key ? $t('common.loading') : plan.label }}
          </button>
        </div>
      </div>

      <div class="space-y-3 rounded-lg border border-sky-200 bg-sky-50/70 p-4">
        <h2 class="text-base font-semibold text-slate-900">{{ text.passwordChange }}</h2>

        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">{{ text.currentPassword }}</label>
          <input
            v-model="currentPassword"
            type="password"
            class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-800 focus:border-sky-300 focus:outline-none focus:ring-2 focus:ring-sky-100"
          />
        </div>

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">{{ text.newPassword }}</label>
            <input
              v-model="newPassword"
              type="password"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-800 focus:border-sky-300 focus:outline-none focus:ring-2 focus:ring-sky-100"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">{{ text.confirmNewPassword }}</label>
            <input
              v-model="newPasswordConfirm"
              type="password"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-800 focus:border-sky-300 focus:outline-none focus:ring-2 focus:ring-sky-100"
            />
          </div>
        </div>

        <p v-if="passwordError" class="text-sm text-red-600">{{ passwordError }}</p>
        <p v-if="passwordSuccess" class="text-sm text-emerald-700">{{ passwordSuccess }}</p>

        <button
          type="button"
          :disabled="passwordLoading"
          class="rounded-lg bg-sky-300 px-4 py-2 font-medium text-stone-900 transition hover:bg-sky-200 disabled:opacity-50"
          @click="changePassword"
        >
          {{ passwordLoading ? $t('common.loading') : text.changePassword }}
        </button>
      </div>

      <div class="space-y-3 rounded-lg border border-red-300 bg-red-50/80 p-4">
        <h2 class="text-base font-semibold text-slate-900">{{ dataRightsText.title }}</h2>
        <p class="text-sm text-slate-700">{{ dataRightsText.body }}</p>
        <p v-if="exportSuccess" class="text-sm text-emerald-700">{{ exportSuccess }}</p>
        <p v-if="exportError" class="text-sm text-red-700">{{ exportError }}</p>
        <button
          type="button"
          :disabled="exportLoading"
          class="rounded-lg border border-sky-300 bg-white px-4 py-2 font-medium text-slate-900 transition hover:bg-sky-50 disabled:opacity-60"
          @click="exportPersonalData"
        >
          {{ exportLoading ? dataRightsText.exportLoading : dataRightsText.exportAction }}
        </button>
      </div>

      <div class="space-y-3 rounded-lg border border-red-300 bg-red-50/80 p-4">
        <h2 class="text-base font-semibold text-red-800">{{ text.deleteTitle }}</h2>
        <p class="text-sm text-red-700">{{ text.deleteBody }}</p>
        <p class="text-xs font-semibold uppercase tracking-wide text-red-700">{{ text.deleteWarning }}</p>
        <p v-if="deleteError" class="text-sm text-red-700">{{ deleteError }}</p>

        <button
          type="button"
          :disabled="deleteLoading"
          class="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white transition hover:bg-red-700 disabled:opacity-60"
          @click="deleteAccount"
        >
          {{ deleteLoading ? $t('common.loading') : text.deleteAction }}
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
const localePath = useLocalePath()
const checkoutLoading = ref<string | null>(null)
const saveLoading = ref(false)
const cardLoading = ref(false)
const billingPortalLoading = ref(false)
const passwordLoading = ref(false)
const deleteLoading = ref(false)
const exportLoading = ref(false)
const saveError = ref('')
const saveSuccess = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')
const deleteError = ref('')
const exportError = ref('')
const exportSuccess = ref('')

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

const trialDaysLeft = computed(() => {
  const endsAt = authStore.user?.trial_ends_at
  if (!endsAt) return null
  const diff = new Date(endsAt).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / 86_400_000))
})

const PLAN_TIER_LABELS: Record<string, Record<string, string>> = {
  ro: { free: 'Plan Gratuit', trial: 'Trial activ', basic: 'BASIC', premium: 'PREMIUM', vip: 'VIP' },
  en: { free: 'Free plan', trial: 'Active trial', basic: 'BASIC', premium: 'PREMIUM', vip: 'VIP' },
  de: { free: 'Kostenlos', trial: 'Aktiver Test', basic: 'BASIC', premium: 'PREMIUM', vip: 'VIP' },
  fr: { free: 'Gratuit', trial: "Essai actif", basic: 'BASIC', premium: 'PREMIUM', vip: 'VIP' },
  it: { free: 'Gratuito', trial: 'Prova attiva', basic: 'BASIC', premium: 'PREMIUM', vip: 'VIP' },
  es: { free: 'Gratuito', trial: 'Prueba activa', basic: 'BASIC', premium: 'PREMIUM', vip: 'VIP' },
  pl: { free: 'Bezplatny', trial: 'Aktywny trial', basic: 'BASIC', premium: 'PREMIUM', vip: 'VIP' },
}

const planTierLabel = computed(() => {
  const tier = authStore.user?.membership_tier || 'free'
  return PLAN_TIER_LABELS[localeCode.value]?.[tier] ?? tier.toUpperCase()
})

const UPGRADE_PLAN_LABELS: Record<string, { key: string; label: string }[]> = {
  ro: [{ key: 'basic', label: 'BASIC – 59 lei/lună' }, { key: 'premium', label: 'PREMIUM – 129 lei/lună' }, { key: 'vip', label: 'VIP – 249 lei/lună' }],
  en: [{ key: 'basic', label: 'BASIC – 59 RON/mo' }, { key: 'premium', label: 'PREMIUM – 129 RON/mo' }, { key: 'vip', label: 'VIP – 249 RON/mo' }],
  de: [{ key: 'basic', label: 'BASIC – 59 RON/Mo.' }, { key: 'premium', label: 'PREMIUM – 129 RON/Mo.' }, { key: 'vip', label: 'VIP – 249 RON/Mo.' }],
  fr: [{ key: 'basic', label: 'BASIC – 59 RON/mois' }, { key: 'premium', label: 'PREMIUM – 129 RON/mois' }, { key: 'vip', label: 'VIP – 249 RON/mois' }],
  it: [{ key: 'basic', label: 'BASIC – 59 RON/mese' }, { key: 'premium', label: 'PREMIUM – 129 RON/mese' }, { key: 'vip', label: 'VIP – 249 RON/mese' }],
  es: [{ key: 'basic', label: 'BASIC – 59 RON/mes' }, { key: 'premium', label: 'PREMIUM – 129 RON/mes' }, { key: 'vip', label: 'VIP – 249 RON/mes' }],
  pl: [{ key: 'basic', label: 'BASIC – 59 RON/mies.' }, { key: 'premium', label: 'PREMIUM – 129 RON/mies.' }, { key: 'vip', label: 'VIP – 249 RON/mies.' }],
}

const upgradePlans = computed(() => UPGRADE_PLAN_LABELS[localeCode.value] || UPGRADE_PLAN_LABELS.en)

const profileCopy: Record<string, {
  membershipPremium: string
  membershipStandard: string
  trialActive: string
  trialDaysLeft: string
  trialLastDay: string
  trialUpgradeNow: string
  freeNotice: string
  choosePlan: string
  upgradeTo: string
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
  deleteTitle: string
  deleteBody: string
  deleteWarning: string
  deleteAction: string
  deleteConfirm: string
  deleteSuccess: string
  deleteError: string
  saveSuccess: string
  saveError: string
  passwordSuccess: string
  passwordError: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    membershipPremium: 'Membru Premium', membershipStandard: 'Membru Standard',
    trialActive: 'Trial activ', trialDaysLeft: 'Mai ai {n} zile de trial gratuit.', trialLastDay: 'Ultima zi de trial. Abonează-te azi!', trialUpgradeNow: 'Activează un abonament acum',
    freeNotice: 'Accesul tău gratuit a expirat.', choosePlan: 'Alege un plan pentru a continua',
    upgradeTo: 'Activează un abonament:',
    firstName: 'Prenume', lastName: 'Nume', phone: 'Telefon contact',
    savedCard: 'Card salvat', expires: 'Expira', manageCard: 'Gestioneaza cardul', noCard: 'Nu exista card salvat inca.', saveProfile: 'Salveaza profilul',
    passwordChange: 'Schimbare parola', currentPassword: 'Parola curenta', newPassword: 'Parola noua', confirmNewPassword: 'Confirmare parola noua', changePassword: 'Schimba parola',
    deleteTitle: 'Sterge contul', deleteBody: 'Actiunea elimina datele personale ale contului, sterge jurnalul si check-in-urile, iar conversatiile raman in platforma doar dupa anonimizare.',
    deleteWarning: 'Aceasta actiune este ireversibila.', deleteAction: 'Sterge contul', deleteConfirm: 'Esti sigur ca vrei sa stergi contul?',
    deleteSuccess: 'Contul a fost sters.', deleteError: 'Nu am putut sterge contul.',
    saveSuccess: 'Profilul a fost actualizat.', saveError: 'Nu am putut salva profilul.', passwordSuccess: 'Parola a fost schimbata cu succes.', passwordError: 'Nu am putut schimba parola.',
    seoTitle: 'Profil utilizator - Doisense', seoDescription: 'Panou de cont pentru utilizatori autentificati Doisense.',
  },
  en: {
    membershipPremium: 'Premium member', membershipStandard: 'Standard member',
    trialActive: 'Trial active', trialDaysLeft: '{n} day(s) left in your free trial.', trialLastDay: 'Last day of your trial. Subscribe now!', trialUpgradeNow: 'Activate a subscription now',
    freeNotice: 'Your free trial has expired.', choosePlan: 'Choose a plan to continue',
    upgradeTo: 'Activate a subscription:',
    firstName: 'First name', lastName: 'Last name', phone: 'Contact phone',
    savedCard: 'Saved card', expires: 'Expires', manageCard: 'Manage card', noCard: 'No saved card yet.', saveProfile: 'Save profile',
    passwordChange: 'Change password', currentPassword: 'Current password', newPassword: 'New password', confirmNewPassword: 'Confirm new password', changePassword: 'Change password',
    deleteTitle: 'Delete account', deleteBody: 'This action removes personal account data, deletes journal and wellbeing entries, and keeps conversations only in anonymized form.',
    deleteWarning: 'This action cannot be undone.', deleteAction: 'Delete account', deleteConfirm: 'Are you sure you want to delete your account?',
    deleteSuccess: 'Account deleted.', deleteError: 'Could not delete account.',
    saveSuccess: 'Profile updated.', saveError: 'Could not save profile.', passwordSuccess: 'Password changed successfully.', passwordError: 'Could not change password.',
    seoTitle: 'User profile - Doisense', seoDescription: 'Account dashboard for authenticated Doisense users.',
  },
  de: {
    membershipPremium: 'Premium-Mitglied', membershipStandard: 'Standard-Mitglied',
    trialActive: 'Test aktiv', trialDaysLeft: 'Noch {n} Tag(e) im kostenlosen Testzeitraum.', trialLastDay: 'Letzter Tag des Tests. Jetzt abonnieren!', trialUpgradeNow: 'Jetzt abonnieren',
    freeNotice: 'Dein kostenloser Testzeitraum ist abgelaufen.', choosePlan: 'Plan wählen und weitermachen',
    upgradeTo: 'Abonnement aktivieren:',
    firstName: 'Vorname', lastName: 'Nachname', phone: 'Kontakttelefon',
    savedCard: 'Gespeicherte Karte', expires: 'Ablauf', manageCard: 'Karte verwalten', noCard: 'Noch keine Karte gespeichert.', saveProfile: 'Profil speichern',
    passwordChange: 'Passwort ändern', currentPassword: 'Aktuelles Passwort', newPassword: 'Neues Passwort', confirmNewPassword: 'Neues Passwort bestätigen', changePassword: 'Passwort ändern',
    deleteTitle: 'Konto löschen', deleteBody: 'Diese Aktion entfernt personenbezogene Kontodaten, löscht Journal- und Check-in-Daten und behält Gespräche nur in anonymisierter Form.',
    deleteWarning: 'Diese Aktion ist nicht rückgängig zu machen.', deleteAction: 'Konto löschen', deleteConfirm: 'Möchtest du dein Konto wirklich löschen?',
    deleteSuccess: 'Konto gelöscht.', deleteError: 'Konto konnte nicht gelöscht werden.',
    saveSuccess: 'Profil wurde aktualisiert.', saveError: 'Profil konnte nicht gespeichert werden.', passwordSuccess: 'Passwort erfolgreich geändert.', passwordError: 'Passwort konnte nicht geändert werden.',
    seoTitle: 'Benutzerprofil - Doisense', seoDescription: 'Kontodashboard für angemeldete Doisense-Nutzer.',
  },
  fr: {
    membershipPremium: 'Membre Premium', membershipStandard: 'Membre Standard',
    trialActive: 'Essai actif', trialDaysLeft: '{n} jour(s) restant dans votre essai gratuit.', trialLastDay: 'Dernier jour d\'essai. Abonnez-vous maintenant !', trialUpgradeNow: 'Activer un abonnement maintenant',
    freeNotice: 'Votre essai gratuit a expiré.', choosePlan: 'Choisissez un plan pour continuer',
    upgradeTo: 'Activer un abonnement :',
    firstName: 'Prenom', lastName: 'Nom', phone: 'Telephone de contact',
    savedCard: 'Carte enregistree', expires: 'Expire', manageCard: 'Gerer la carte', noCard: 'Aucune carte enregistree pour le moment.', saveProfile: 'Enregistrer le profil',
    passwordChange: 'Changer le mot de passe', currentPassword: 'Mot de passe actuel', newPassword: 'Nouveau mot de passe', confirmNewPassword: 'Confirmer le nouveau mot de passe', changePassword: 'Changer le mot de passe',
    deleteTitle: 'Supprimer le compte', deleteBody: 'Cette action supprime les donnees personnelles du compte, efface le journal et les check-ins, et conserve les conversations uniquement sous forme anonymisee.',
    deleteWarning: 'Cette action est irreversible.', deleteAction: 'Supprimer le compte', deleteConfirm: 'Voulez-vous vraiment supprimer votre compte ?',
    deleteSuccess: 'Compte supprime.', deleteError: 'Impossible de supprimer le compte.',
    saveSuccess: 'Profil mis a jour.', saveError: 'Impossible d\'enregistrer le profil.', passwordSuccess: 'Mot de passe modifie avec succes.', passwordError: 'Impossible de modifier le mot de passe.',
    seoTitle: 'Profil utilisateur - Doisense', seoDescription: 'Tableau de bord du compte pour les utilisateurs connectes de Doisense.',
  },
  it: {
    membershipPremium: 'Membro Premium', membershipStandard: 'Membro Standard',
    trialActive: 'Prova attiva', trialDaysLeft: '{n} giorno/i rimasti nella prova gratuita.', trialLastDay: 'Ultimo giorno di prova. Abbonati ora!', trialUpgradeNow: 'Attiva un abbonamento ora',
    freeNotice: 'La tua prova gratuita è scaduta.', choosePlan: 'Scegli un piano per continuare',
    upgradeTo: 'Attiva un abbonamento:',
    firstName: 'Nome', lastName: 'Cognome', phone: 'Telefono di contatto',
    savedCard: 'Carta salvata', expires: 'Scadenza', manageCard: 'Gestisci carta', noCard: 'Nessuna carta salvata.', saveProfile: 'Salva profilo',
    passwordChange: 'Cambia password', currentPassword: 'Password attuale', newPassword: 'Nuova password', confirmNewPassword: 'Conferma nuova password', changePassword: 'Cambia password',
    deleteTitle: 'Elimina account', deleteBody: 'Questa azione rimuove i dati personali dell\'account, elimina diario e check-in e mantiene le conversazioni solo in forma anonimizzata.',
    deleteWarning: 'Questa azione e irreversibile.', deleteAction: 'Elimina account', deleteConfirm: 'Sei sicuro di voler eliminare il tuo account?',
    deleteSuccess: 'Account eliminato.', deleteError: 'Impossibile eliminare l\'account.',
    saveSuccess: 'Profilo aggiornato.', saveError: 'Impossibile salvare il profilo.', passwordSuccess: 'Password cambiata con successo.', passwordError: 'Impossibile cambiare la password.',
    seoTitle: 'Profilo utente - Doisense', seoDescription: 'Pannello account per utenti autenticati Doisense.',
  },
  es: {
    membershipPremium: 'Miembro Premium', membershipStandard: 'Miembro Standard',
    trialActive: 'Prueba activa', trialDaysLeft: '{n} día(s) restante(s) en tu prueba gratuita.', trialLastDay: 'Último día de prueba. ¡Suscríbete ahora!', trialUpgradeNow: 'Activar suscripción ahora',
    freeNotice: 'Tu prueba gratuita ha expirado.', choosePlan: 'Elige un plan para continuar',
    upgradeTo: 'Activar suscripción:',
    firstName: 'Nombre', lastName: 'Apellido', phone: 'Telefono de contacto',
    savedCard: 'Tarjeta guardada', expires: 'Caduca', manageCard: 'Gestionar tarjeta', noCard: 'Aun no hay tarjeta guardada.', saveProfile: 'Guardar perfil',
    passwordChange: 'Cambiar contraseña', currentPassword: 'Contraseña actual', newPassword: 'Nueva contraseña', confirmNewPassword: 'Confirmar nueva contraseña', changePassword: 'Cambiar contraseña',
    deleteTitle: 'Eliminar cuenta', deleteBody: 'Esta acción elimina los datos personales de la cuenta, borra diario y check-ins, y conserva las conversaciones solo de forma anonimizada.',
    deleteWarning: 'Esta accion no se puede deshacer.', deleteAction: 'Eliminar cuenta', deleteConfirm: '¿Seguro que quieres eliminar tu cuenta?',
    deleteSuccess: 'Cuenta eliminada.', deleteError: 'No se pudo eliminar la cuenta.',
    saveSuccess: 'Perfil actualizado.', saveError: 'No se pudo guardar el perfil.', passwordSuccess: 'Contraseña cambiada correctamente.', passwordError: 'No se pudo cambiar la contraseña.',
    seoTitle: 'Perfil de usuario - Doisense', seoDescription: 'Panel de cuenta para usuarios autenticados de Doisense.',
  },
  pl: {
    membershipPremium: 'Czlonek Premium', membershipStandard: 'Czlonek Standard',
    trialActive: 'Aktywny trial', trialDaysLeft: 'Pozostało {n} dzień/dni bezpłatnego trialu.', trialLastDay: 'Ostatni dzień trialu. Subskrybuj teraz!', trialUpgradeNow: 'Aktywuj subskrypcję teraz',
    freeNotice: 'Twój bezpłatny trial wygasł.', choosePlan: 'Wybierz plan, aby kontynuować',
    upgradeTo: 'Aktywuj subskrypcję:',
    firstName: 'Imie', lastName: 'Nazwisko', phone: 'Telefon kontaktowy',
    savedCard: 'Zapisana karta', expires: 'Wazna do', manageCard: 'Zarzadzaj karta', noCard: 'Brak zapisanej karty.', saveProfile: 'Zapisz profil',
    passwordChange: 'Zmiana hasla', currentPassword: 'Aktualne haslo', newPassword: 'Nowe haslo', confirmNewPassword: 'Potwierdz nowe haslo', changePassword: 'Zmien haslo',
    deleteTitle: 'Usun konto', deleteBody: 'Ta akcja usuwa dane osobowe konta, kasuje dziennik i check-iny oraz zachowuje rozmowy tylko w formie zanonimizowanej.',
    deleteWarning: 'Tej akcji nie da sie cofnac.', deleteAction: 'Usun konto', deleteConfirm: 'Czy na pewno chcesz usunac konto?',
    deleteSuccess: 'Konto usuniete.', deleteError: 'Nie udalo sie usunac konta.',
    saveSuccess: 'Profil zaktualizowany.', saveError: 'Nie udalo sie zapisac profilu.', passwordSuccess: 'Haslo zostalo zmienione.', passwordError: 'Nie udalo sie zmienic hasla.',
    seoTitle: 'Profil uzytkownika - Doisense', seoDescription: 'Panel konta dla zalogowanych uzytkownikow Doisense.',
  },
}

const text = computed(() => profileCopy[localeCode.value] || profileCopy.en)

const dataRightsText = computed(() => {
  if (localeCode.value === 'ro') {
    return {
      title: 'Datele tale personale',
      body: 'Poți exporta imediat datele personale asociate contului tău în format JSON.',
      exportAction: 'Exporta datele personale',
      exportLoading: 'Se exporta...',
      exportSuccess: 'Exportul a fost generat.',
      exportError: 'Nu am putut genera exportul de date.',
    }
  }

  return {
    title: 'Your personal data',
    body: 'You can export the personal data linked to your account as a JSON file at any time.',
    exportAction: 'Export personal data',
    exportLoading: 'Exporting...',
    exportSuccess: 'Your export is ready.',
    exportError: 'We could not generate your data export.',
  }
})

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

async function createCheckout(planKey = 'premium') {
  checkoutLoading.value = planKey
  try {
    const res = await fetchApi<{ url: string }>('/payments/create-checkout-session', {
      method: 'POST',
      body: { plan_tier: planKey },
    })
    if (res?.url) window.location.href = res.url
  } finally {
    checkoutLoading.value = null
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

async function deleteAccount() {
  if (!window.confirm(text.value.deleteConfirm)) return

  deleteLoading.value = true
  deleteError.value = ''
  try {
    await fetchApi('/me', { method: 'DELETE' })
    authStore.logout()
    await navigateTo(localePath('/'))
  } catch {
    deleteError.value = text.value.deleteError
  } finally {
    deleteLoading.value = false
  }
}

async function exportPersonalData() {
  exportLoading.value = true
  exportError.value = ''
  exportSuccess.value = ''

  try {
    const payload = await fetchApi<Record<string, unknown>>('/me/export', { method: 'GET' })
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'doisense-personal-data.json'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    exportSuccess.value = dataRightsText.value.exportSuccess
  } catch {
    exportError.value = dataRightsText.value.exportError
  } finally {
    exportLoading.value = false
  }
}
</script>
