<template>
  <div class="profile-shell">
    <aside class="profile-sidebar">
      <div class="profile-logo">doisense</div>
      <nav class="profile-nav">
        <a class="profile-nav-item active" href="#profile-overview">Profil</a>
        <a class="profile-nav-item" href="#profile-habits">Obiceiurile mele</a>
        <a class="profile-nav-item" href="#profile-subscription">Abonament</a>
        <a class="profile-nav-item" href="#profile-security">Securitate</a>
        <a class="profile-nav-item" href="#profile-data">Date personale</a>
      </nav>
      <div class="profile-plan">{{ planTierLabel }}</div>
    </aside>

    <main class="profile-main" v-if="authStore.user">
      <header class="profile-header" id="profile-overview">
        <h1>{{ $t('nav.profile') }}</h1>
        <p>{{ text.manageNotificationsSupport }}</p>
      </header>

      <section class="profile-card profile-hero-card">
        <div class="profile-avatar">
          {{ (firstName || authStore.user.first_name || authStore.user.email || 'U').charAt(0).toUpperCase() }}
        </div>
        <div>
          <h2 class="profile-name">{{ firstName || authStore.user.first_name || 'User' }} {{ lastName || authStore.user.last_name || '' }}</h2>
          <p class="profile-email">{{ authStore.user.email }}</p>
        </div>
      </section>

      <HabitsDashboard />

      <section class="profile-card">
        <div class="profile-section-head">
          <h3>Detalii cont</h3>
          <button type="button" class="profile-btn profile-btn-primary" :disabled="saveLoading" @click="saveProfile">
            {{ saveLoading ? $t('common.loading') : text.saveProfile }}
          </button>
        </div>
        <div class="profile-grid">
          <div class="profile-field">
            <label>{{ text.firstName }}</label>
            <input v-model="firstName" type="text" />
          </div>
          <div class="profile-field">
            <label>{{ text.lastName }}</label>
            <input v-model="lastName" type="text" />
          </div>
          <div class="profile-field profile-field-full">
            <label>{{ text.phone }}</label>
            <input v-model="phoneContact" type="tel" placeholder="+40 712 345 678" />
            <div class="profile-tags">
              <button v-for="dialCode in dialCodeOptions" :key="dialCode.value" type="button" class="profile-tag" @click="setPhoneDialCode(dialCode.value)">
                {{ dialCode.label }}
              </button>
            </div>
          </div>
        </div>
        <p v-if="saveError" class="profile-error">{{ saveError }}</p>
        <p v-if="saveSuccess" class="profile-success">{{ saveSuccess }}</p>
      </section>

      <section class="profile-card" id="profile-subscription">
        <div class="profile-section-head">
          <h3>Abonament</h3>
        </div>

        <div v-if="authStore.user.membership_tier === 'trial' && trialDaysLeft !== null" class="profile-banner profile-banner-warn">
          <p class="profile-banner-title">{{ text.trialActive }}</p>
          <p>{{ trialDaysLeft > 0 ? text.trialDaysLeft.replace('{n}', String(trialDaysLeft)) : text.trialLastDay }}</p>
          <NuxtLink :to="localePath('/pricing')" class="profile-link">{{ text.trialUpgradeNow }} →</NuxtLink>
        </div>

        <div v-if="authStore.user.membership_tier === 'free'" class="profile-banner">
          <p class="profile-banner-title">{{ text.freeNotice }}</p>
          <NuxtLink :to="localePath('/pricing')" class="profile-link">{{ text.choosePlan }} →</NuxtLink>
        </div>

        <div class="profile-banner">
          <p class="profile-banner-title">{{ text.savedCard }}</p>
          <p v-if="cardLoading">{{ $t('common.loading') }}</p>
          <template v-else-if="savedCard?.has_saved_card && savedCard.card">
            <p>{{ savedCard.card.brand?.toUpperCase() }} •••• {{ savedCard.card.last4 }}</p>
            <p>{{ text.expires }}: {{ savedCard.card.exp_month }}/{{ savedCard.card.exp_year }}</p>
            <button type="button" class="profile-btn" :disabled="billingPortalLoading" @click="openBillingPortal">
              {{ billingPortalLoading ? $t('common.loading') : text.manageCard }}
            </button>
          </template>
          <p v-else>{{ text.noCard }}</p>
        </div>

        <div v-if="['trial', 'free'].includes(authStore.user.membership_tier)" class="profile-upgrade">
          <p>{{ text.upgradeTo }}</p>
          <div class="profile-tags">
            <button
              v-for="plan in upgradePlans"
              :key="plan.key"
              type="button"
              class="profile-tag"
              :disabled="checkoutLoading === plan.key"
              @click="createCheckout(plan.key)"
            >
              {{ checkoutLoading === plan.key ? $t('common.loading') : plan.label }}
            </button>
          </div>
        </div>
      </section>

      <section class="profile-card" id="profile-security">
        <div class="profile-section-head">
          <h3>{{ text.passwordChange }}</h3>
        </div>
        <div class="profile-grid">
          <div class="profile-field profile-field-full">
            <label>{{ text.currentPassword }}</label>
            <input v-model="currentPassword" type="password" />
          </div>
          <div class="profile-field">
            <label>{{ text.newPassword }}</label>
            <input v-model="newPassword" type="password" />
          </div>
          <div class="profile-field">
            <label>{{ text.confirmNewPassword }}</label>
            <input v-model="newPasswordConfirm" type="password" />
          </div>
        </div>
        <p v-if="passwordError" class="profile-error">{{ passwordError }}</p>
        <p v-if="passwordSuccess" class="profile-success">{{ passwordSuccess }}</p>
        <button type="button" class="profile-btn profile-btn-primary" :disabled="passwordLoading" @click="changePassword">
          {{ passwordLoading ? $t('common.loading') : text.changePassword }}
        </button>
      </section>

      <section class="profile-card" id="profile-data">
        <div class="profile-section-head">
          <h3>{{ dataRightsText.title }}</h3>
        </div>
        <p class="profile-copy">{{ dataRightsText.body }}</p>
        <p v-if="exportSuccess" class="profile-success">{{ exportSuccess }}</p>
        <p v-if="exportError" class="profile-error">{{ exportError }}</p>
        <button type="button" class="profile-btn" :disabled="exportLoading" @click="exportPersonalData">
          {{ exportLoading ? dataRightsText.exportLoading : dataRightsText.exportAction }}
        </button>
      </section>

      <section class="profile-card profile-card-danger">
        <div class="profile-section-head">
          <h3>{{ text.deleteTitle }}</h3>
        </div>
        <p class="profile-copy">{{ text.deleteBody }}</p>
        <p class="profile-warning">{{ text.deleteWarning }}</p>
        <p v-if="deleteError" class="profile-error">{{ deleteError }}</p>
        <button type="button" class="profile-btn profile-btn-danger" :disabled="deleteLoading" @click="deleteAccount">
          {{ deleteLoading ? $t('common.loading') : text.deleteAction }}
        </button>
      </section>

      <section class="profile-card">
        <div class="profile-section-head">
          <h3>Acces rapid</h3>
        </div>
        <p class="profile-copy">{{ text.featureTourPrompt }}</p>
        <div class="profile-tags">
          <button type="button" class="profile-btn" @click="restartOnboarding">{{ text.restartOnboarding }}</button>
          <NuxtLink :to="localePath('/notifications')" class="profile-btn">{{ text.notificationsCta }}</NuxtLink>
          <NuxtLink :to="localePath('/tickets')" class="profile-btn">{{ text.supportTicketsCta }}</NuxtLink>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.profile-shell {
  --bg: #fafbfa;
  --surface: #fafbfa;
  --border: #d4e4e0;
  --text: #2c3e35;
  --muted: #8a9b94;
  --accent: #7bb8a0;
  --accent-soft: #e8f1ed;
  --danger: #c05848;
  --danger-soft: #fdf0ee;
  display: grid;
  grid-template-columns: 240px minmax(0, 860px);
  gap: 28px;
  max-width: 1160px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  color: var(--text);
  background: var(--bg);
}

.profile-sidebar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  align-self: start;
  position: sticky;
  top: 86px;
}

.profile-logo {
  padding: 0 22px 18px;
  border-bottom: 1px solid var(--border);
  font-size: 20px;
  letter-spacing: 0.12em;
  font-weight: 400;
  color: var(--text);
}

.profile-nav {
  padding: 14px 0;
  display: flex;
  flex-direction: column;
}

.profile-nav-item {
  padding: 10px 22px;
  color: var(--muted);
  text-decoration: none;
  font-size: 13px;
}

.profile-nav-item.active,
.profile-nav-item:hover {
  background: var(--accent-soft);
  color: var(--accent);
}

.profile-plan {
  margin: auto 22px 0;
  background: var(--accent-soft);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 2px;
  text-align: center;
  font-size: 10px;
  padding: 6px 10px;
  font-weight: 400;
  letter-spacing: 0.25em;
  text-transform: uppercase;
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.profile-header h1 {
  font-size: 36px;
  font-weight: 400;
  letter-spacing: 0.04em;
}

.profile-header p {
  margin-top: 4px;
  color: var(--muted);
  font-size: 13px;
}

.profile-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px;
}

.profile-card-danger {
  border-color: #ebc5c5;
  background: #fff6f6;
}

.profile-hero-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px 32px;
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a8d5ba, #7bb8a0);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 24px;
  font-weight: 400;
}

.profile-name {
  font-size: 26px;
  font-weight: 400;
  letter-spacing: 0.05em;
}

.profile-email {
  font-size: 13px;
  color: var(--muted);
}

.profile-section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.profile-section-head h3 {
  font-size: 10px;
  font-weight: 400;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--muted);
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.profile-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.profile-field-full {
  grid-column: 1 / -1;
}

.profile-field label {
  font-size: 10px;
  font-weight: 400;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--muted);
}

.profile-field input {
  border: none;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text);
  background: transparent;
}

.profile-field input:focus {
  border-bottom-color: var(--accent);
  outline: none;
  box-shadow: none;
}

.profile-banner {
  border: 1px solid var(--border);
  background: #f0f4f1;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  font-size: 14px;
}

.profile-banner-warn {
  border-color: #eadcb7;
  background: #f6f2e8;
}

.profile-banner-title {
  font-weight: 700;
  margin-bottom: 4px;
}

.profile-upgrade > p {
  font-weight: 700;
  margin-bottom: 8px;
}

.profile-link {
  color: var(--accent);
  display: inline-block;
  margin-top: 6px;
  text-decoration: none;
  font-weight: 700;
}

.profile-link:hover {
  text-decoration: underline;
}

.profile-tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.profile-tag,
.profile-btn {
  border: 1px solid var(--border);
  background: transparent;
  border-radius: 3px;
  color: var(--muted);
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 400;
  cursor: pointer;
  text-decoration: none;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.profile-btn-primary {
  background: var(--text);
  color: #fafbfa;
  border-color: var(--text);
}

.profile-btn-danger {
  background: var(--danger-soft, #fdf0ee);
  border-color: #f0c8c0;
  color: var(--danger);
}

.profile-copy {
  font-size: 14px;
  color: var(--muted);
  line-height: 1.5;
}

.profile-warning {
  margin-top: 10px;
  color: var(--danger);
  font-size: 11px;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.profile-error {
  color: #ba4a4a;
  font-size: 13px;
  margin-top: 10px;
}

.profile-success {
  color: #1f8b63;
  font-size: 13px;
  margin-top: 10px;
}

@media (max-width: 980px) {
  .profile-shell {
    grid-template-columns: 1fr;
    padding-top: 10px;
  }

  .profile-sidebar {
    display: none;
  }

  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup lang="ts">
import HabitsDashboard from '~/components/profile/HabitsDashboard.vue'

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
  ro: [{ key: 'basic', label: 'BASIC – €12/lună' }, { key: 'premium', label: 'PREMIUM – €25/lună' }, { key: 'vip', label: 'VIP – €49/lună' }],
  en: [{ key: 'basic', label: 'BASIC – €12/mo' }, { key: 'premium', label: 'PREMIUM – €25/mo' }, { key: 'vip', label: 'VIP – €49/mo' }],
  de: [{ key: 'basic', label: 'BASIC – €12/Mo.' }, { key: 'premium', label: 'PREMIUM – €25/Mo.' }, { key: 'vip', label: 'VIP – €49/Mo.' }],
  fr: [{ key: 'basic', label: 'BASIC – €12/mois' }, { key: 'premium', label: 'PREMIUM – €25/mois' }, { key: 'vip', label: 'VIP – €49/mois' }],
  it: [{ key: 'basic', label: 'BASIC – €12/mese' }, { key: 'premium', label: 'PREMIUM – €25/mese' }, { key: 'vip', label: 'VIP – €49/mese' }],
  es: [{ key: 'basic', label: 'BASIC – €12/mes' }, { key: 'premium', label: 'PREMIUM – €25/mes' }, { key: 'vip', label: 'VIP – €49/mes' }],
  pl: [{ key: 'basic', label: 'BASIC – €12/mies.' }, { key: 'premium', label: 'PREMIUM – €25/mies.' }, { key: 'vip', label: 'VIP – €49/mies.' }],
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
  featureTourPrompt: string
  restartOnboarding: string
  manageNotificationsSupport: string
  notificationsCta: string
  supportTicketsCta: string
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
    featureTourPrompt: 'Vrei un tur rapid pentru redescoperirea functiilor?',
    restartOnboarding: 'Reporneste onboarding',
    manageNotificationsSupport: 'Gestioneaza notificarile si cere ajutor direct din cont.',
    notificationsCta: 'Notificari',
    supportTicketsCta: 'Support tickets',
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
    featureTourPrompt: 'Need a quick feature rediscovery tour?',
    restartOnboarding: 'Restart onboarding',
    manageNotificationsSupport: 'Manage notifications and request support directly from your account.',
    notificationsCta: 'Notifications',
    supportTicketsCta: 'Support tickets',
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
    featureTourPrompt: 'Brauchst du eine kurze Tour zur Wiederentdeckung der Funktionen?',
    restartOnboarding: 'Onboarding neu starten',
    manageNotificationsSupport: 'Verwalte Benachrichtigungen und fordere direkt im Konto Hilfe an.',
    notificationsCta: 'Benachrichtigungen',
    supportTicketsCta: 'Support-Tickets',
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
    featureTourPrompt: 'Besoin d\'une visite rapide des fonctionnalites ?',
    restartOnboarding: 'Redemarrer l\'onboarding',
    manageNotificationsSupport: 'Gerez les notifications et demandez de l\'aide directement depuis votre compte.',
    notificationsCta: 'Notifications',
    supportTicketsCta: 'Tickets support',
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
    featureTourPrompt: 'Vuoi un tour rapido per riscoprire le funzionalita?',
    restartOnboarding: 'Riavvia onboarding',
    manageNotificationsSupport: 'Gestisci notifiche e richiedi supporto direttamente dal tuo account.',
    notificationsCta: 'Notifiche',
    supportTicketsCta: 'Ticket di supporto',
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
    featureTourPrompt: 'Necesitas un recorrido rapido para redescubrir funciones?',
    restartOnboarding: 'Reiniciar onboarding',
    manageNotificationsSupport: 'Gestiona notificaciones y solicita ayuda directamente desde tu cuenta.',
    notificationsCta: 'Notificaciones',
    supportTicketsCta: 'Tickets de soporte',
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
    featureTourPrompt: 'Potrzebujesz szybkiego przypomnienia funkcji?',
    restartOnboarding: 'Uruchom onboarding ponownie',
    manageNotificationsSupport: 'Zarzadzaj powiadomieniami i popros o pomoc bezposrednio z konta.',
    notificationsCta: 'Powiadomienia',
    supportTicketsCta: 'Zgloszenia wsparcia',
    deleteTitle: 'Usun konto', deleteBody: 'Ta akcja usuwa dane osobowe konta, kasuje dziennik i check-iny oraz zachowuje rozmowy tylko w formie zanonimizowanej.',
    deleteWarning: 'Tej akcji nie da sie cofnac.', deleteAction: 'Usun konto', deleteConfirm: 'Czy na pewno chcesz usunac konto?',
    deleteSuccess: 'Konto usuniete.', deleteError: 'Nie udalo sie usunac konta.',
    saveSuccess: 'Profil zaktualizowany.', saveError: 'Nie udalo sie zapisac profilu.', passwordSuccess: 'Haslo zostalo zmienione.', passwordError: 'Nie udalo sie zmienic hasla.',
    seoTitle: 'Profil uzytkownika - Doisense', seoDescription: 'Panel konta dla zalogowanych uzytkownikow Doisense.',
  },
}

const text = computed(() => profileCopy[localeCode.value] || profileCopy.en)

const dataRightsText = computed(() => {
  return {
    ro: {
      title: 'Datele tale personale',
      body: 'Poti exporta imediat datele personale asociate contului tau in format JSON.',
      exportAction: 'Exporta datele personale',
      exportLoading: 'Se exporta...',
      exportSuccess: 'Exportul a fost generat.',
      exportError: 'Nu am putut genera exportul de date.',
    },
    en: {
      title: 'Your personal data',
      body: 'You can export the personal data linked to your account as a JSON file at any time.',
      exportAction: 'Export personal data',
      exportLoading: 'Exporting...',
      exportSuccess: 'Your export is ready.',
      exportError: 'We could not generate your data export.',
    },
    de: {
      title: 'Deine personenbezogenen Daten',
      body: 'Du kannst die mit deinem Konto verknuepften personenbezogenen Daten jederzeit als JSON exportieren.',
      exportAction: 'Personendaten exportieren',
      exportLoading: 'Export laeuft...',
      exportSuccess: 'Der Export ist bereit.',
      exportError: 'Der Datenexport konnte nicht erstellt werden.',
    },
    fr: {
      title: 'Vos donnees personnelles',
      body: 'Vous pouvez exporter a tout moment les donnees personnelles liees a votre compte au format JSON.',
      exportAction: 'Exporter les donnees personnelles',
      exportLoading: 'Export en cours...',
      exportSuccess: 'Votre export est pret.',
      exportError: 'Impossible de generer l\'export des donnees.',
    },
    it: {
      title: 'I tuoi dati personali',
      body: 'Puoi esportare in qualsiasi momento i dati personali del tuo account in formato JSON.',
      exportAction: 'Esporta dati personali',
      exportLoading: 'Esportazione in corso...',
      exportSuccess: 'Il tuo export e pronto.',
      exportError: 'Non siamo riusciti a generare l\'export dei dati.',
    },
    es: {
      title: 'Tus datos personales',
      body: 'Puedes exportar en cualquier momento los datos personales de tu cuenta en formato JSON.',
      exportAction: 'Exportar datos personales',
      exportLoading: 'Exportando...',
      exportSuccess: 'Tu exportacion esta lista.',
      exportError: 'No pudimos generar la exportacion de datos.',
    },
    pl: {
      title: 'Twoje dane osobowe',
      body: 'W dowolnym momencie mozesz wyeksportowac dane osobowe konta w formacie JSON.',
      exportAction: 'Eksportuj dane osobowe',
      exportLoading: 'Trwa eksport...',
      exportSuccess: 'Eksport jest gotowy.',
      exportError: 'Nie mozna wygenerowac eksportu danych.',
    },
  }[localeCode.value] || {
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

async function restartOnboarding() {
  await fetchApi('/me/re-onboarding', { method: 'POST' })
  if (authStore.user) {
    authStore.setUser({ ...authStore.user, onboarding_completed: false })
  }
  await navigateTo(localePath('/onboarding'))
}
</script>
