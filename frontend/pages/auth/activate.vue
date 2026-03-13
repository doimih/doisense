<template>
  <div class="max-w-md mx-auto py-12">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">{{ text.title }}</h1>
    <p class="text-stone-600 mb-6">
      {{ text.subtitle }}
    </p>

    <p v-if="loading" class="text-stone-700">{{ $t('common.loading') }}...</p>
    <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
    <p v-if="success" class="text-emerald-700 text-sm">{{ success }}</p>

    <NuxtLink :to="localePath('/auth/login')" class="mt-6 inline-block text-amber-600 hover:underline">
      {{ text.goToLogin }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()
const route = useRoute()
const config = useRuntimeConfig()

const loading = ref(true)
const error = ref('')
const success = ref('')

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const copy: Record<string, {
  title: string
  subtitle: string
  goToLogin: string
  invalidLink: string
  activated: string
  activationFailed: string
}> = {
  ro: {
    title: 'Activare cont',
    subtitle: 'Confirmam contul tau folosind linkul din email.',
    goToLogin: 'Mergi la autentificare',
    invalidLink: 'Link de activare invalid.',
    activated: 'Cont activat cu succes.',
    activationFailed: 'Nu am putut activa contul.',
  },
  en: {
    title: 'Account activation',
    subtitle: 'We are confirming your account using the link from your email.',
    goToLogin: 'Go to sign in',
    invalidLink: 'Invalid activation link.',
    activated: 'Account activated successfully.',
    activationFailed: 'We could not activate your account.',
  },
  de: {
    title: 'Kontoaktivierung',
    subtitle: 'Wir bestaetigen dein Konto mit dem Link aus deiner E-Mail.',
    goToLogin: 'Zur Anmeldung',
    invalidLink: 'Ungueltiger Aktivierungslink.',
    activated: 'Konto erfolgreich aktiviert.',
    activationFailed: 'Konto konnte nicht aktiviert werden.',
  },
  fr: {
    title: 'Activation du compte',
    subtitle: 'Nous confirmons votre compte avec le lien recu par e-mail.',
    goToLogin: 'Aller a la connexion',
    invalidLink: 'Lien d\'activation invalide.',
    activated: 'Compte active avec succes.',
    activationFailed: 'Impossible d\'activer le compte.',
  },
  it: {
    title: 'Attivazione account',
    subtitle: 'Stiamo confermando il tuo account tramite il link ricevuto via email.',
    goToLogin: 'Vai al login',
    invalidLink: 'Link di attivazione non valido.',
    activated: 'Account attivato con successo.',
    activationFailed: 'Non siamo riusciti ad attivare l\'account.',
  },
  es: {
    title: 'Activacion de cuenta',
    subtitle: 'Estamos confirmando tu cuenta con el enlace de tu correo.',
    goToLogin: 'Ir a iniciar sesion',
    invalidLink: 'Enlace de activacion invalido.',
    activated: 'Cuenta activada correctamente.',
    activationFailed: 'No pudimos activar la cuenta.',
  },
  pl: {
    title: 'Aktywacja konta',
    subtitle: 'Potwierdzamy konto za pomoca linku z wiadomosci e-mail.',
    goToLogin: 'Przejdz do logowania',
    invalidLink: 'Nieprawidlowy link aktywacyjny.',
    activated: 'Konto zostalo aktywowane.',
    activationFailed: 'Nie udalo sie aktywowac konta.',
  },
}

const text = computed(() => copy[localeCode.value] || copy.en)

onMounted(async () => {
  const uid = (route.query.uid as string) || ''
  const token = (route.query.token as string) || ''

  if (!uid || !token) {
    error.value = text.value.invalidLink
    loading.value = false
    return
  }

  try {
    const base = config.public.apiBase as string
    const res = await $fetch<{ detail: string }>(`${base}/auth/activate`, {
      method: 'POST',
      body: { uid, token },
    })
    success.value = res.detail || text.value.activated
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || text.value.activationFailed
  } finally {
    loading.value = false
  }
})
</script>
