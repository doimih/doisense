<template>
  <div class="-mt-6 pb-8">
    <section data-nav-theme="dark" class="relative left-1/2 right-1/2 -mx-[50vw] w-screen overflow-hidden bg-stone-900 text-white">
      <img
        src="/hero-zen.jpg"
        alt="Doisense wellbeing support"
        loading="eager"
        decoding="async"
        width="2200"
        height="1400"
        class="absolute inset-0 h-full w-full object-cover object-[50%_18%]"
      >
      <div class="absolute inset-0 bg-stone-950/62" />
      <div class="absolute inset-0 bg-gradient-to-r from-stone-950/94 via-stone-900/74 to-stone-900/48" />
      <div class="pointer-events-none absolute inset-0">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgba(125,211,252,0.35),transparent_42%),radial-gradient(circle_at_86%_82%,rgba(56,189,248,0.32),transparent_45%)]" />
      </div>

      <div class="relative mx-auto max-w-[1440px] px-4 py-10 sm:px-6 md:py-14 lg:px-8">
        <div class="relative overflow-hidden rounded-[2.4rem] border border-white/20 bg-black/28 p-5 shadow-[0_32px_90px_-35px_rgba(14,116,144,0.65)] backdrop-blur-[1px] md:p-8 lg:p-10">

          <div class="relative grid gap-8 lg:grid-cols-[1.18fr_0.82fr] lg:items-end">
            <div class="space-y-7">
              <p class="inline-flex items-center rounded-full border border-white/30 bg-white/10 px-4 py-2 text-xs font-semibold text-white/95 md:text-sm">
                {{ $t('home.heroBadge') }}
              </p>

              <h1 class="max-w-4xl text-4xl font-bold leading-[1.05] tracking-tight text-white md:text-6xl lg:text-7xl">
                {{ $t('home.heroTitle') }}
              </h1>

              <p class="max-w-2xl text-base leading-8 text-white/85 md:text-lg">
                {{ $t('home.heroSubtitle') }}
              </p>

              <div class="flex flex-wrap gap-3">
                <NuxtLink
                  v-if="!authStore.isLoggedIn"
                  :to="localePath('/auth/register')"
                  class="rounded-full bg-sky-300 px-6 py-3 text-sm font-semibold text-stone-900 transition hover:bg-sky-200"
                >
                  {{ $t('home.primaryCta') }}
                </NuxtLink>
                <NuxtLink
                  v-if="!authStore.isLoggedIn"
                  :to="localePath('/auth/login')"
                  class="rounded-full border border-white/35 bg-white/10 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/20"
                >
                  {{ $t('auth.login') }}
                </NuxtLink>
                <NuxtLink
                  v-if="authStore.isLoggedIn"
                  :to="localePath('/chat')"
                  class="rounded-full bg-sky-300 px-6 py-3 text-sm font-semibold text-stone-900 transition hover:bg-sky-200"
                >
                  {{ $t('nav.chat') }}
                </NuxtLink>
                <NuxtLink
                  :to="localePath('/features')"
                  class="rounded-full border border-white/35 bg-white/10 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/20"
                >
                  {{ $t('home.secondaryCta') }}
                </NuxtLink>
              </div>
            </div>

            <div class="space-y-4 lg:justify-self-end lg:max-w-md">
              <article class="rounded-2xl border border-white/20 bg-white/10 p-5 backdrop-blur">
                <h2 class="text-2xl font-semibold tracking-tight text-white md:text-3xl">{{ heroCard.title }}</h2>
                <p class="mt-2 text-base leading-7 text-white/85 md:text-lg">{{ heroCard.description }}</p>
              </article>

              <div class="flex flex-wrap gap-3">
                <p class="rounded-full border border-white/25 bg-white/10 px-5 py-2 text-sm font-semibold text-white/90 shadow-sm md:text-base">
                  {{ heroPillLeft }}
                </p>
                <p class="rounded-full border border-white/25 bg-white/10 px-5 py-2 text-sm font-semibold text-white/90 shadow-sm md:text-base">
                  {{ heroPillRight }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="mt-[120px] rounded-3xl border border-stone-200 bg-stone-100/70 px-5 py-8 md:px-8 md:py-10">
      <div class="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-start">
        <div class="space-y-6">
          <p class="inline-flex items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-700 md:text-sm">
            {{ $t('home.heroBadge') }}
          </p>
          <h2 class="max-w-4xl text-4xl font-bold leading-tight text-stone-900 md:text-6xl">
            {{ $t('home.sectionTwoTitle') }}
          </h2>
        </div>

        <div class="space-y-6 lg:pt-4">
          <p class="max-w-lg text-lg leading-8 text-stone-600">
            {{ $t('home.sectionTwoDesc') }}
          </p>
          <NuxtLink
            :to="sectionTwoCta.to"
            class="inline-flex items-center rounded-full bg-black px-6 py-3 text-sm font-semibold text-white transition hover:bg-stone-900"
          >
            {{ sectionTwoCta.label }}
          </NuxtLink>
        </div>
      </div>

      <div class="mt-8 flex flex-wrap gap-3">
        <NuxtLink
          v-for="link in quickLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="rounded-full border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 transition hover:bg-stone-50"
        >
          {{ link.title }}
        </NuxtLink>
      </div>
    </section>

    <section class="mt-[120px] rounded-3xl border border-stone-200 bg-stone-100/70 px-5 py-8 md:px-8 md:py-10">
      <div class="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
        <p class="inline-flex h-fit w-fit justify-self-start items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-700 md:text-sm">
          {{ $t('home.impactBadge') }}
        </p>
        <h2 class="max-w-4xl text-4xl font-bold leading-tight text-stone-900 md:text-6xl">
          {{ $t('home.impactTitle') }}
        </h2>
      </div>

      <div class="mt-8 grid gap-4 lg:grid-cols-4">
        <article
          v-for="(item, index) in impactCards"
          :key="item.label"
          :class="[
            'rounded-2xl border p-5 md:p-6',
            index === 1 ? 'border-sky-200 bg-sky-100/70' : 'border-stone-200 bg-white',
          ]"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-full border border-stone-200 bg-stone-50 text-[1.95rem] leading-none">
            ✹
          </div>
          <p class="mt-5 text-5xl font-bold tracking-tight text-stone-900">{{ item.value }}</p>
          <h3 class="mt-2 text-3xl font-semibold leading-tight text-stone-900">{{ item.label }}</h3>
          <p class="mt-4 text-xl leading-8 text-stone-600">{{ item.description }}</p>
        </article>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const authStore = useAuthStore()
const { locale, t } = useI18n()
const { cmsPage } = useCmsStaticPage('home')
type HomeCard = { title: string; description: string }

function stripHtml(value: string) {
  return value
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim()
}

function extractCardsFromCms(html: string): HomeCard[] {
  if (!html?.trim()) return []

  const cards: HomeCard[] = []

  // Recommended format in CMS: table rows => Title | Description
  const rowMatches = [...html.matchAll(/<tr[^>]*>([\s\S]*?)<\/tr>/gi)]
  for (const row of rowMatches) {
    const columns = [...row[1].matchAll(/<t[dh][^>]*>([\s\S]*?)<\/t[dh]>/gi)].map((col) => stripHtml(col[1]))
    if (columns.length >= 2 && columns[0] && columns[1]) {
      cards.push({ title: columns[0], description: columns[1] })
    }
  }

  if (cards.length) return cards

  // Fallback format: heading + first paragraph after heading.
  const headingMatches = [...html.matchAll(/<h[1-6][^>]*>([\s\S]*?)<\/h[1-6]>/gi)]
  for (let i = 0; i < headingMatches.length; i += 1) {
    const heading = stripHtml(headingMatches[i][1])
    const start = headingMatches[i].index ?? 0
    const end = i + 1 < headingMatches.length ? (headingMatches[i + 1].index ?? html.length) : html.length
    const chunk = html.slice(start, end)
    const paragraphMatch = chunk.match(/<p[^>]*>([\s\S]*?)<\/p>/i)
    const paragraph = paragraphMatch ? stripHtml(paragraphMatch[1]) : ""

    if (heading && paragraph) {
      cards.push({ title: heading, description: paragraph })
    }
  }

  return cards
}

const homeCards = computed(() => {
  const parsed = extractCardsFromCms(cmsPage.value?.content || "")
  return parsed.length ? parsed : [
    { title: t('home.card1Title'), description: t('home.card1Desc') },
    { title: t('home.card2Title'), description: t('home.card2Desc') },
    { title: t('home.card3Title'), description: t('home.card3Desc') },
  ]
})

const heroCard = computed(() => homeCards.value[0] || { title: t('home.card1Title'), description: t('home.card1Desc') })
const heroPillLeft = computed(() => `${homeCards.value.length}+ ${homeCards.value[0]?.title || t('home.card1Title')}`)
const heroPillRight = computed(() => t('nav.features'))
const sectionTwoCta = computed(() => ({
  to: localePath('/features'),
  label: t('nav.features'),
}))

const quickLinks = computed(() => [
  { to: '/features', title: t('nav.features') },
  { to: '/pricing', title: t('nav.pricing') },
  { to: '/about', title: t('nav.about') },
  { to: '/contact', title: t('nav.contact') },
])

const impactCards = computed(() => {
  const cards = homeCards.value
  return [
    {
      value: `${cards.length}+`,
      label: cards[0]?.title || t('home.card1Title'),
      description: cards[0]?.description || t('home.heroSubtitle'),
    },
    {
      value: `${quickLinks.value.length}+`,
      label: cards[1]?.title || t('home.card2Title'),
      description: cards[1]?.description || t('home.heroSubtitle'),
    },
    {
      value: '7+',
      label: cards[2]?.title || t('home.card3Title'),
      description: cards[2]?.description || t('home.heroSubtitle'),
    },
    {
      value: `${quickLinks.value.length * 15}+`,
      label: t('nav.features'),
      description: t('home.secondaryCta'),
    },
  ]
})

const seoTitle = computed(() => t('home.seoTitle'))
const seoDescription = computed(() => t('home.seoDesc'))

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
