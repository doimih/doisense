<template>
  <ClientOnly>
    <ChatWindow />
    <template #fallback>
      <div class="rounded-[28px] border border-slate-200 bg-white p-6 text-sm text-slate-500">
        Se incarca chat-ul...
      </div>
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'onboarding'], layout: 'chat' })

const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const seoCopy: Record<string, { title: string; description: string }> = {
  ro: { title: 'Chat - Doisense', description: 'Chat AI contextual pentru utilizatori autentificati.' },
  en: { title: 'Chat - Doisense', description: 'Context-aware AI chat for authenticated users.' },
  de: { title: 'Chat - Doisense', description: 'Kontextbezogener KI-Chat fur angemeldete Nutzer.' },
  fr: { title: 'Chat - Doisense', description: 'Chat IA contextuel pour les utilisateurs connectes.' },
  it: { title: 'Chat - Doisense', description: 'Chat AI contestuale per utenti autenticati.' },
  es: { title: 'Chat - Doisense', description: 'Chat AI contextual para usuarios autenticados.' },
  pl: { title: 'Chat - Doisense', description: 'Kontekstowy chat AI dla zalogowanych uzytkownikow.' },
}

const seoText = computed(() => seoCopy[localeCode.value] || seoCopy.en)

usePublicSeo({
  title: computed(() => seoText.value.title),
  description: computed(() => seoText.value.description),
  noindex: true,
})
</script>
