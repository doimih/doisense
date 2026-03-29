<template>
  <section class="onb-wrap">
    <div class="onb-shell">
      <p class="logo-mark">doi <span>sense</span></p>
      <p class="step-counter">{{ currentStep + 1 }} / {{ text.steps.length }}</p>

      <div class="step active">
        <div class="progress-wrap">
          <span class="progress-label">{{ text.progressLabel(currentStep + 1, text.steps.length) }}</span>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${((currentStep + 1) / text.steps.length) * 100}%` }" />
          </div>
          <div class="progress-dots">
            <div
              v-for="(_, index) in text.steps"
              :key="`pdot-${index}`"
              :class="[
                'pdot',
                index < currentStep ? 'done' : '',
                index === currentStep ? 'current' : '',
              ]"
            />
          </div>
        </div>

        <div class="card">
          <div class="card-hero">
            <div class="step-chip">
              <span class="step-chip-dot" />
              {{ activeStep.shortTitle }}
            </div>
            <h1 class="hero-title">{{ activeStep.title }}</h1>
            <p v-if="activeStep.text" class="hero-desc">{{ activeStep.text }}</p>
            <p v-if="activeStep.subtext" class="hero-desc hero-desc-soft">{{ activeStep.subtext }}</p>
            <p class="hero-note">{{ tierHint }}</p>
          </div>

          <div class="card-body">
            <template v-if="currentStep === 0">
              <div class="welcome-visual">
                <div class="breathing-orb">
                  <div class="orb-inner">∞</div>
                </div>
              </div>
            </template>

            <template v-else-if="activeStep.bullets?.length">
              <div class="feature-grid">
                <article
                  v-for="(bullet, index) in activeStep.bullets"
                  :key="bullet"
                  :class="['feature-item', index === activeStep.bullets.length - 1 && activeStep.bullets.length % 2 !== 0 ? 'feature-item-full' : '']"
                >
                  <div class="feature-icon">{{ featureIcons[index] || '•' }}</div>
                  <div class="feature-text">
                    <p class="feature-name">{{ bullet }}</p>
                    <p class="feature-desc">{{ featureDescriptions[index] || '' }}</p>
                  </div>
                </article>
              </div>
            </template>

            <template v-if="currentStep === 2">
              <div class="disclaimer-grid">
                <article class="disc-item disc-ok">
                  <div class="disc-icon">✓</div>
                  <p class="disc-title">{{ disclaimerText.offerTitle }}</p>
                  <p class="disc-sub">{{ activeStep.text }}</p>
                </article>
                <article class="disc-item disc-no">
                  <div class="disc-icon">!</div>
                  <p class="disc-title">{{ disclaimerText.limitTitle }}</p>
                  <p class="disc-sub">{{ activeStep.subtext }}</p>
                </article>
              </div>
            </template>

            <template v-if="currentStep === 3">
              <div class="privacy-box">
                <label class="privacy-check">
                  <input v-model="consentAccepted" type="checkbox" class="consent-checkbox" />
                  <span class="check-text">
                    {{ text.consentLabel.before }}
                    <NuxtLink :to="localePath('/legal/terms')">{{ text.consentLabel.terms }}</NuxtLink>
                    {{ text.consentLabel.middle }}
                    <NuxtLink :to="localePath('/legal/privacy')">{{ text.consentLabel.privacy }}</NuxtLink>
                    {{ text.consentLabel.and }}
                    <NuxtLink :to="localePath('/legal/ai-consent')">{{ text.consentLabel.ai }}</NuxtLink>
                    {{ text.consentLabel.after }}
                  </span>
                </label>

                <div class="doc-tags">
                  <NuxtLink :to="localePath('/legal/terms')" class="doc-tag">{{ text.linkLabels.terms }}</NuxtLink>
                  <NuxtLink :to="localePath('/legal/gdpr')" class="doc-tag">{{ text.linkLabels.gdpr }}</NuxtLink>
                  <NuxtLink :to="localePath('/legal/ai-consent')" class="doc-tag">{{ text.linkLabels.ai }}</NuxtLink>
                  <NuxtLink :to="localePath('/legal/cookies')" class="doc-tag">{{ text.linkLabels.cookies }}</NuxtLink>
                </div>
              </div>
            </template>

            <template v-if="currentStep === 4">
              <div class="emo-layout">
                <div class="emo-panel">
                  <p class="panel-label">{{ text.profile.moodTitle }}</p>
                  <div class="mood-grid">
                    <button
                      v-for="option in text.profile.moods"
                      :key="option.value"
                      type="button"
                      :class="['mood-item', selectedMood === option.value ? 'selected' : '']"
                      @click="selectedMood = option.value"
                    >
                      <span class="mood-emoji">{{ option.icon }}</span>
                      <span class="mood-label">{{ option.label }}</span>
                    </button>
                  </div>

                  <div class="energy-section">
                    <div class="energy-header">
                      <p class="energy-title">{{ text.profile.energyTitle }}</p>
                      <p class="energy-val">{{ energyLevel }}/5</p>
                    </div>
                    <input v-model="energyLevel" type="range" min="1" max="5" step="1" />
                    <div class="energy-labels">
                      <span>1</span>
                      <span>2</span>
                      <span>3</span>
                      <span>4</span>
                      <span>5</span>
                    </div>
                  </div>
                </div>

                <div class="emo-panel journal-panel">
                  <p class="panel-label">{{ text.profile.journalTitle }}</p>
                  <textarea v-model="journalEntry" rows="6" :placeholder="text.profile.journalPlaceholder" />
                  <p class="journal-note">{{ text.profile.note }}</p>
                </div>
              </div>
            </template>

            <p v-if="stepError" class="step-error">{{ stepError }}</p>
          </div>

          <div class="card-footer">
            <button v-if="currentStep > 0" type="button" class="btn btn-ghost" @click="goBack">{{ text.backAction }}</button>
            <span v-else />
            <button
              type="button"
              :disabled="isBusy || isCurrentStepBlocked"
              class="btn btn-accent"
              @click="goNext"
            >
              {{ currentStep === text.steps.length - 1 ? text.finishAction : activeStep.button }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.onb-wrap {
  --bg: #fafbfa;
  --surface: #fafbfa;
  --surface2: #e8f1ed;
  --border: rgba(168, 213, 186, 0.2);
  --border2: rgba(168, 213, 186, 0.1);
  --text: #2c3e35;
  --text2: #5a6b63;
  --text3: #8a9b94;
  --accent: #7bb8a0;
  --accent2: #a8d5ba;
  --accent-glow: rgba(168, 213, 186, 0.15);
  --gold: #d4e4e0;
  --danger: #c05848;
  min-height: 100vh;
  background:
    radial-gradient(ellipse 60% 50% at 20% 20%, rgba(168, 213, 186, 0.1) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 80% 80%, rgba(212, 228, 224, 0.08) 0%, transparent 60%),
    var(--bg);
  padding: 34px 22px;
}

.onb-shell {
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
}

.logo-mark {
  position: absolute;
  top: -2px;
  left: 6px;
  font-size: 20px;
  letter-spacing: 0.1em;
  color: var(--text3);
  font-weight: 700;
}

.logo-mark span {
  color: var(--accent);
}

.step-counter {
  position: fixed;
  right: 40px;
  bottom: 32px;
  color: var(--text3);
  font-size: 13px;
  letter-spacing: 0.1em;
  z-index: 10;
}

.step {
  padding-top: 44px;
}

.progress-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
}

.progress-label {
  font-size: 10px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--text3);
  font-weight: 600;
  white-space: nowrap;
}

.progress-track {
  flex: 1;
  height: 1px;
  border-radius: 2px;
  background: var(--border);
  overflow: visible;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #7bb8a0, #a8d5ba);
  transition: width 0.45s ease;
}

.progress-dots {
  display: flex;
  gap: 6px;
}

.pdot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--border);
}

.pdot.done {
  background: var(--accent2);
}

.pdot.current {
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent);
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.1), 0 1px 0 rgba(255, 255, 255, 0.8) inset;
}

.card-hero {
  padding: 42px 48px 34px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #e8f1ed 0%, #f0f4f1 60%, #fafbfa 100%);
  border-bottom: 1px solid var(--border);
}

.step-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  border: 1px solid rgba(168, 213, 186, 0.3);
  background: rgba(168, 213, 186, 0.15);
  color: #7bb8a0;
  padding: 5px 12px;
  font-size: 10px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  font-weight: 700;
}

.step-chip-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #7bb8a0;
}

.hero-title {
  margin-top: 20px;
  color: var(--text);
  font-size: clamp(30px, 3.8vw, 44px);
  line-height: 1.14;
  letter-spacing: 0.01em;
  font-weight: 700;
}

.hero-desc {
  margin-top: 14px;
  max-width: 640px;
  color: var(--text2);
  line-height: 1.72;
  font-size: 14px;
}

.hero-desc-soft {
  color: var(--text2);
}

.hero-note {
  margin-top: 14px;
  font-size: 11px;
  color: var(--text3);
}

.card-body {
  padding: 32px 48px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--border2);
  padding: 18px 48px 24px;
}

.btn {
  border-radius: 999px;
  padding: 11px 24px;
  font-size: 12px;
  letter-spacing: 0.08em;
  font-weight: 700;
  border: 1px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-accent {
  background: linear-gradient(135deg, var(--accent2), var(--accent));
  color: #fff;
}

.btn-accent:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px -12px rgba(123, 184, 160, 0.7);
}

.btn-ghost {
  border-color: var(--border);
  background: transparent;
  color: var(--text3);
}

.btn-ghost:hover {
  border-color: rgba(15, 23, 42, 0.25);
}

.welcome-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 170px;
}

.breathing-orb {
  width: 92px;
  height: 92px;
  border-radius: 50%;
  border: 1px solid rgba(168, 213, 186, 0.18);
  background: radial-gradient(circle at 35% 35%, rgba(168, 213, 186, 0.2), rgba(123, 184, 160, 0.06) 50%, transparent);
  display: grid;
  place-items: center;
  animation: breathe 4s ease-in-out infinite;
}

.orb-inner {
  color: var(--accent);
  font-size: 30px;
  font-style: italic;
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.feature-item {
  border: 1px solid var(--border2);
  border-radius: 10px;
  background: var(--surface2);
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.feature-item-full {
  grid-column: 1 / -1;
}

.feature-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--accent-glow);
  display: grid;
  place-items: center;
}

.feature-name {
  font-size: 13px;
  color: var(--text);
}

.feature-desc {
  margin-top: 4px;
  font-size: 11px;
  color: var(--text3);
  line-height: 1.55;
}

.disclaimer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.disc-item {
  border-radius: 10px;
  border: 1px solid var(--border2);
  background: var(--surface2);
  padding: 20px;
}

.disc-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-weight: 700;
}

.disc-ok .disc-icon {
  background: rgba(106, 159, 126, 0.15);
  color: #6a9f7e;
}

.disc-no .disc-icon {
  background: rgba(192, 88, 72, 0.12);
  color: #c05848;
}

.disc-title {
  margin-top: 10px;
  font-size: 13px;
  color: var(--text);
  font-weight: 700;
}

.disc-sub {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text3);
  line-height: 1.6;
}

.privacy-box {
  border: 1px solid var(--border2);
  background: var(--surface2);
  border-radius: 8px;
  padding: 20px;
}

.privacy-check {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border2);
}

.consent-checkbox {
  margin-top: 2px;
  width: 18px;
  height: 18px;
  accent-color: var(--accent);
}

.check-text {
  font-size: 13px;
  color: var(--text2);
  line-height: 1.64;
}

.check-text a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid rgba(123, 184, 160, 0.35);
}

.doc-tags {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.doc-tag {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 11px;
  color: var(--text3);
  text-decoration: none;
}

.doc-tag:hover {
  border-color: var(--accent2);
  color: var(--accent);
}

.emo-layout {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 16px;
}

.emo-panel {
  border: 1px solid var(--border2);
  background: var(--surface2);
  border-radius: 10px;
  padding: 18px;
}

.panel-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: var(--text3);
  margin-bottom: 12px;
  font-weight: 700;
}

.mood-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.mood-item {
  border: 1px solid var(--border2);
  border-radius: 9px;
  background: #fff;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.mood-item.selected {
  border-color: var(--accent);
  background: rgba(123, 184, 160, 0.08);
}

.mood-emoji {
  font-size: 22px;
  line-height: 1;
}

.mood-label {
  text-align: center;
  font-size: 12px;
  color: var(--text2);
}

.energy-section {
  margin-top: 14px;
}

.energy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.energy-title {
  font-size: 12px;
  color: var(--text2);
}

.energy-val {
  font-size: 20px;
  color: var(--accent);
}

input[type="range"] {
  width: 100%;
  margin: 10px 0 8px;
  accent-color: var(--accent);
}

.energy-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text3);
}

textarea {
  width: 100%;
  border: none;
  border-bottom: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  font-size: 13px;
  line-height: 1.6;
  resize: none;
  outline: none;
  padding: 8px 0;
}

textarea:focus {
  border-bottom-color: var(--accent);
}

.journal-note {
  margin-top: 12px;
  color: var(--text3);
  font-size: 11px;
  line-height: 1.62;
}

.step-error {
  margin-top: 16px;
  border: 1px solid #f2c2bc;
  background: #fff3f1;
  color: #b94131;
  border-radius: 10px;
  padding: 11px 12px;
  font-size: 13px;
}

@keyframes breathe {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.08);
    opacity: 1;
  }
}

@media (max-width: 980px) {
  .onb-wrap {
    min-height: auto;
    padding: 18px 12px 24px;
    background:
      radial-gradient(ellipse 80% 52% at 12% 8%, rgba(26, 168, 187, 0.08) 0%, transparent 72%),
      radial-gradient(ellipse 70% 45% at 88% 92%, rgba(210, 169, 110, 0.07) 0%, transparent 68%),
      var(--bg);
  }

  .step-counter {
    position: static;
    text-align: right;
    margin-bottom: 8px;
  }

  .logo-mark {
    position: static;
    margin-bottom: 8px;
  }

  .step {
    padding-top: 4px;
  }

  .card-hero,
  .card-body,
  .card-footer {
    padding-left: 16px;
    padding-right: 16px;
  }

  .card-hero {
    padding-top: 26px;
    padding-bottom: 22px;
  }

  .card-body {
    padding-top: 20px;
    padding-bottom: 20px;
  }

  .card-footer {
    padding-top: 14px;
    padding-bottom: 18px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .hero-title {
    margin-top: 14px;
    font-size: clamp(25px, 7vw, 34px);
    line-height: 1.18;
  }

  .hero-desc {
    margin-top: 10px;
    font-size: 13px;
    line-height: 1.66;
  }

  .hero-note {
    margin-top: 11px;
    line-height: 1.45;
  }

  .welcome-visual {
    min-height: 130px;
  }

  .breathing-orb {
    width: 78px;
    height: 78px;
  }

  .progress-wrap {
    gap: 10px;
    margin-bottom: 14px;
  }

  .progress-label {
    font-size: 9px;
    letter-spacing: 0.14em;
  }

  .step-chip {
    padding: 5px 10px;
    font-size: 9px;
    letter-spacing: 0.14em;
  }

  .feature-grid,
  .disclaimer-grid,
  .emo-layout {
    grid-template-columns: 1fr;
  }

  .panel-label {
    letter-spacing: 0.12em;
  }
}

@media (max-width: 640px) {
  .logo-mark {
    font-size: 18px;
    margin-bottom: 6px;
  }

  .step-counter {
    margin-bottom: 6px;
    font-size: 12px;
  }

  .progress-track,
  .progress-dots {
    display: none;
  }

  .progress-wrap {
    justify-content: center;
    margin-bottom: 12px;
  }

  .card {
    border-radius: 12px;
  }

  .card-footer {
    display: grid;
    grid-template-columns: 1fr;
  }

  .card-footer .btn {
    width: 100%;
    justify-self: stretch;
  }

  .mood-grid {
    gap: 8px;
  }

  .mood-item {
    padding: 13px 8px;
  }

  .mood-label {
    font-size: 11px;
  }

  textarea {
    min-height: 120px;
    font-size: 12px;
  }

  .doc-tags {
    gap: 6px;
  }

  .doc-tag {
    width: 100%;
    text-align: center;
  }
}
</style>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const localePath = useLocalePath()
const router = useRouter()
const authStore = useAuthStore()
const { fetchApi } = useApi()
const { locale } = useI18n()
const { chatPath } = useOnboarding()

type MoodValue = 'low' | 'ok' | 'good' | 'great'

interface OnboardingCopy {
  steps: Array<{
    shortTitle: string
    title: string
    text?: string
    subtext?: string
    bullets?: string[]
    button: string
  }>
  progressLabel: (current: number, total: number) => string
  consentLabel: {
    before: string
    terms: string
    middle: string
    privacy: string
    and: string
    ai: string
    after: string
  }
  linkLabels: Record<'terms' | 'gdpr' | 'ai' | 'cookies', string>
  profile: {
    moodTitle: string
    moods: Array<{ value: MoodValue; label: string; icon: string }>
    energyTitle: string
    journalTitle: string
    journalPlaceholder: string
    note: string
  }
  chatAccessSteps: Array<{ step: string; title: string; body: string }>
  backAction: string
  finishAction: string
  consentRequired: string
  saveError: string
  seoTitle: string
  seoDescription: string
}

const copy: Record<string, OnboardingCopy> = {
  ro: {
    steps: [
      {
        shortTitle: 'Bun venit',
        title: 'Bine ai venit în spațiul tău de claritate și echilibru',
        text: 'Aici vei lucra cu un AI creat pentru a te ajuta să înțelegi mai bine ce simți, să-ți clarifici obiectivele și să evoluezi în ritmul tău.',
        button: 'Începe',
      },
      {
        shortTitle: 'Platforma',
        title: 'Cum te poate ajuta platforma',
        bullets: [
          'îți analizează stările emoționale',
          'îți pune întrebări inteligente',
          'îți creează planuri zilnice și rapoarte',
          'te ajută să-ți clarifici obiectivele',
          'îți oferă suport emoțional general',
        ],
        button: 'Continuă',
      },
      {
        shortTitle: 'Disclaimer',
        title: 'Ce este important să știi',
        text: 'Platforma oferă suport emoțional general și instrumente de auto-reflecție. Nu oferă sfaturi medicale, psihologice sau terapeutice.',
        subtext: 'Dacă te confrunți cu o situație gravă, este important să cauți ajutor specializat.',
        button: 'Am înțeles',
      },
      {
        shortTitle: 'Confidențialitate',
        title: 'Protejăm confidențialitatea ta',
        text: 'Nu colectăm nume, adresă sau date personale sensibile. Folosim doar un ID anonim. Datele tale sunt criptate și pot fi șterse oricând.',
        button: 'Accept și continui',
      },
      {
        shortTitle: 'Profil emoțional',
        title: 'Setarea profilului emoțional',
        text: 'Înainte de prima conversație, setează rapid starea ta actuală. Asta ne ajută să pornim mai relevant și mai calm.',
        subtext: 'Poți adăuga și câteva rânduri despre ce te preocupă chiar acum.',
        button: 'Continuă către AI',
      },
    ],
    progressLabel: (current, total) => `Pasul ${current} din ${total}`,
    consentLabel: {
      before: 'Sunt de acord cu ',
      terms: 'Termenii și Condițiile',
      middle: ', ',
      privacy: 'Politica de Confidențialitate',
      and: ' și ',
      ai: 'Acordul AI',
      after: '.',
    },
    linkLabels: {
      terms: 'Termeni și Condiții',
      gdpr: 'Politica GDPR',
      ai: 'Acord AI',
      cookies: 'Politica Cookies',
    },
    profile: {
      moodTitle: 'Cum te simți acum?',
      moods: [
        { value: 'low', label: 'Apăsat(ă)', icon: '🌧️' },
        { value: 'ok', label: 'Echilibrat(ă)', icon: '🌿' },
        { value: 'good', label: 'Bine', icon: '🌤️' },
        { value: 'great', label: 'Foarte bine', icon: '☀️' },
      ],
      energyTitle: 'Nivelul de energie',
      journalTitle: 'Jurnal inițial',
      journalPlaceholder: 'Scrie câteva rânduri despre ce simți, ce te apasă sau ce ai vrea să clarifici.',
      note: 'Vom salva starea ta actuală pentru a personaliza experiența din chat. Nota de jurnal este opțională, dar utilă pentru primul context.',
    },
    chatAccessSteps: [
      { step: 'Pasul 1', title: 'Intri în chat-ul AI', body: 'După acest ecran vei fi redirecționat direct în zona de chat a platformei.' },
      { step: 'Pasul 2', title: 'Alegi direcția conversației', body: 'Poți porni cu suport emoțional, clarificare, obiective sau o întrebare punctuală.' },
      { step: 'Pasul 3', title: 'Scrii primul mesaj', body: 'Spune ce simți acum, ce te preocupă sau ce vrei să înțelegi mai bine despre tine.' },
      { step: 'Pasul 4', title: 'Primești răspuns ghidat', body: 'AI-ul îți oferă întrebări, clarificări și recomandări generale, fără diagnostic sau tratament.' },
    ],
    backAction: 'Înapoi',
    finishAction: 'Deschide chat-ul AI',
    consentRequired: 'Trebuie să accepți termenii înainte să continui.',
    saveError: 'Nu am putut salva profilul inițial. Încearcă din nou.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Flux ghidat de onboarding pentru utilizatorii noi înainte de prima conversație cu AI-ul.',
  },
  en: {
    steps: [
      {
        shortTitle: 'Welcome',
        title: 'Welcome to your space for clarity and balance',
        text: 'Here you will work with an AI designed to help you understand what you feel, clarify your goals, and grow at your own pace.',
        button: 'Start',
      },
      {
        shortTitle: 'Platform',
        title: 'How the platform can help you',
        bullets: [
          'analyzes your emotional states',
          'asks intelligent questions',
          'creates daily plans and reports',
          'helps you clarify your goals',
          'offers general emotional support',
        ],
        button: 'Continue',
      },
      {
        shortTitle: 'Disclaimer',
        title: 'What is important to know',
        text: 'The platform provides general emotional support and self-reflection tools. It does not provide medical, psychological, or therapeutic advice.',
        subtext: 'If you are facing a serious situation, it is important to seek specialized help.',
        button: 'I understand',
      },
      {
        shortTitle: 'Privacy',
        title: 'We protect your privacy',
        text: 'We do not collect names, addresses, or sensitive personal data. We use only an anonymous ID. Your data is encrypted and can be deleted at any time.',
        button: 'Accept and continue',
      },
      {
        shortTitle: 'Emotional profile',
        title: 'Set up your emotional profile',
        text: 'Before your first conversation, quickly set your current state. This helps us start in a more relevant and calmer way.',
        subtext: 'You can also add a few lines about what is on your mind right now.',
        button: 'Continue to AI',
      },
    ],
    progressLabel: (current, total) => `Step ${current} of ${total}`,
    consentLabel: {
      before: 'I agree with the ',
      terms: 'Terms and Conditions',
      middle: ', ',
      privacy: 'Privacy Policy',
      and: ', and the ',
      ai: 'AI Agreement',
      after: '.',
    },
    linkLabels: {
      terms: 'Terms and Conditions',
      gdpr: 'GDPR Policy',
      ai: 'AI Agreement',
      cookies: 'Cookies Policy',
    },
    profile: {
      moodTitle: 'How do you feel right now?',
      moods: [
        { value: 'low', label: 'Low', icon: '🌧️' },
        { value: 'ok', label: 'Steady', icon: '🌿' },
        { value: 'good', label: 'Good', icon: '🌤️' },
        { value: 'great', label: 'Great', icon: '☀️' },
      ],
      energyTitle: 'Energy level',
      journalTitle: 'Initial journal note',
      journalPlaceholder: 'Write a few lines about what you feel, what feels heavy, or what you want to clarify.',
      note: 'We will save your current state to personalize the chat experience. The journal note is optional, but helpful for initial context.',
    },
    chatAccessSteps: [
      { step: 'Step 1', title: 'Open AI chat', body: 'After this screen you will be redirected straight into the chat area.' },
      { step: 'Step 2', title: 'Choose your direction', body: 'You can start with emotional support, clarity, goals, or a direct question.' },
      { step: 'Step 3', title: 'Write your first message', body: 'Say what you feel now, what is on your mind, or what you want to understand better.' },
      { step: 'Step 4', title: 'Receive guided support', body: 'The AI responds with questions, clarifications, and general recommendations without diagnosis or treatment.' },
    ],
    backAction: 'Back',
    finishAction: 'Open AI chat',
    consentRequired: 'You need to accept the terms before continuing.',
    saveError: 'We could not save your initial profile. Please try again.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Guided onboarding flow for new users before their first AI conversation.',
  },
  de: {
    steps: [
      {
        shortTitle: 'Willkommen',
        title: 'Willkommen in deinem Raum fur Klarheit und Balance',
        text: 'Hier arbeitest du mit einer KI, die dir hilft, Gefuhle besser zu verstehen, Ziele zu klaren und in deinem Tempo zu wachsen.',
        button: 'Start',
      },
      {
        shortTitle: 'Plattform',
        title: 'Wie die Plattform dir helfen kann',
        bullets: [
          'analysiert deine emotionalen Zustande',
          'stellt intelligente Fragen',
          'erstellt Tagesplane und Berichte',
          'hilft dir, Ziele zu klaren',
          'bietet allgemeine emotionale Unterstutzung',
        ],
        button: 'Weiter',
      },
      {
        shortTitle: 'Hinweis',
        title: 'Wichtige Hinweise',
        text: 'Die Plattform bietet allgemeine emotionale Unterstutzung und Reflexionswerkzeuge. Sie bietet keine medizinische, psychologische oder therapeutische Beratung.',
        subtext: 'Bei ernsten Situationen solltest du professionelle Hilfe suchen.',
        button: 'Ich verstehe',
      },
      {
        shortTitle: 'Datenschutz',
        title: 'Wir schutzen deine Privatsphare',
        text: 'Wir erfassen keine Namen, Adressen oder sensible personliche Daten. Wir verwenden nur eine anonyme ID. Deine Daten sind verschlusselt und jederzeit loschbar.',
        button: 'Akzeptieren und weiter',
      },
      {
        shortTitle: 'Emotionales Profil',
        title: 'Richte dein emotionales Profil ein',
        text: 'Vor dem ersten Gesprach kannst du deinen aktuellen Zustand schnell festlegen. So starten wir relevanter und ruhiger.',
        subtext: 'Du kannst auch ein paar Zeilen zu deinen aktuellen Gedanken schreiben.',
        button: 'Weiter zur KI',
      },
    ],
    progressLabel: (current, total) => `Schritt ${current} von ${total}`,
    consentLabel: {
      before: 'Ich stimme den ',
      terms: 'Nutzungsbedingungen',
      middle: ', der ',
      privacy: 'Datenschutzerklarung',
      and: ' und der ',
      ai: 'KI-Vereinbarung',
      after: ' zu.',
    },
    linkLabels: {
      terms: 'Nutzungsbedingungen',
      gdpr: 'DSGVO-Richtlinie',
      ai: 'KI-Vereinbarung',
      cookies: 'Cookie-Richtlinie',
    },
    profile: {
      moodTitle: 'Wie fuhlst du dich gerade?',
      moods: [
        { value: 'low', label: 'Niedrig', icon: '🌧️' },
        { value: 'ok', label: 'Stabil', icon: '🌿' },
        { value: 'good', label: 'Gut', icon: '🌤️' },
        { value: 'great', label: 'Sehr gut', icon: '☀️' },
      ],
      energyTitle: 'Energielevel',
      journalTitle: 'Erste Journaleintragung',
      journalPlaceholder: 'Schreibe ein paar Zeilen daruber, wie du dich fuhlst, was schwer wirkt oder was du klaren mochtest.',
      note: 'Wir speichern deinen aktuellen Zustand, um die Chat-Erfahrung zu personalisieren. Die Notiz ist optional, aber hilfreich fur den Einstieg.',
    },
    chatAccessSteps: [
      { step: 'Schritt 1', title: 'KI-Chat offnen', body: 'Nach diesem Bildschirm wirst du direkt in den Chat-Bereich weitergeleitet.' },
      { step: 'Schritt 2', title: 'Richtung wahlen', body: 'Du kannst mit emotionaler Unterstutzung, Klarheit, Zielen oder einer direkten Frage starten.' },
      { step: 'Schritt 3', title: 'Erste Nachricht schreiben', body: 'Schreibe, wie du dich fuhlst, was dich beschaftigt oder was du besser verstehen willst.' },
      { step: 'Schritt 4', title: 'Gefuhrte Unterstutzung erhalten', body: 'Die KI antwortet mit Fragen, Klarstellungen und allgemeinen Empfehlungen ohne Diagnose oder Behandlung.' },
    ],
    backAction: 'Zuruck',
    finishAction: 'KI-Chat offnen',
    consentRequired: 'Du musst die Bedingungen akzeptieren, um fortzufahren.',
    saveError: 'Das Speichern des Startprofils ist fehlgeschlagen. Bitte versuche es erneut.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Gefuhrter Onboarding-Flow fur neue Nutzer vor dem ersten KI-Gesprach.',
  },
  fr: {
    steps: [
      {
        shortTitle: 'Bienvenue',
        title: 'Bienvenue dans ton espace de clarte et d equilibre',
        text: 'Ici, tu travailles avec une IA concue pour t aider a mieux comprendre tes emotions, clarifier tes objectifs et evoluer a ton rythme.',
        button: 'Commencer',
      },
      {
        shortTitle: 'Plateforme',
        title: 'Comment la plateforme peut t aider',
        bullets: [
          'analyse tes etats emotionnels',
          'pose des questions intelligentes',
          'cree des plans quotidiens et des rapports',
          't aide a clarifier tes objectifs',
          'offre un soutien emotionnel general',
        ],
        button: 'Continuer',
      },
      {
        shortTitle: 'Avertissement',
        title: 'Ce qu il faut savoir',
        text: 'La plateforme offre un soutien emotionnel general et des outils de reflexion. Elle ne fournit pas de conseils medicaux, psychologiques ou therapeutiques.',
        subtext: 'En cas de situation serieuse, il est important de demander une aide specialisee.',
        button: 'Je comprends',
      },
      {
        shortTitle: 'Confidentialite',
        title: 'Nous protegens ta vie privee',
        text: 'Nous ne collectons pas de noms, adresses ou donnees personnelles sensibles. Nous utilisons seulement un identifiant anonyme. Tes donnees sont chiffrees et supprimables a tout moment.',
        button: 'Accepter et continuer',
      },
      {
        shortTitle: 'Profil emotionnel',
        title: 'Configure ton profil emotionnel',
        text: 'Avant la premiere conversation, indique rapidement ton etat actuel. Cela permet un demarrage plus pertinent et plus calme.',
        subtext: 'Tu peux aussi ajouter quelques lignes sur ce qui te preoccupe maintenant.',
        button: 'Continuer vers l IA',
      },
    ],
    progressLabel: (current, total) => `Etape ${current} sur ${total}`,
    consentLabel: {
      before: 'J accepte les ',
      terms: 'Conditions generales',
      middle: ', la ',
      privacy: 'Politique de confidentialite',
      and: ' et l ',
      ai: 'Accord IA',
      after: '.',
    },
    linkLabels: {
      terms: 'Conditions generales',
      gdpr: 'Politique RGPD',
      ai: 'Accord IA',
      cookies: 'Politique Cookies',
    },
    profile: {
      moodTitle: 'Comment te sens-tu maintenant ?',
      moods: [
        { value: 'low', label: 'Bas', icon: '🌧️' },
        { value: 'ok', label: 'Stable', icon: '🌿' },
        { value: 'good', label: 'Bien', icon: '🌤️' },
        { value: 'great', label: 'Tres bien', icon: '☀️' },
      ],
      energyTitle: 'Niveau d energie',
      journalTitle: 'Note initiale',
      journalPlaceholder: 'Ecris quelques lignes sur ce que tu ressens, ce qui pese ou ce que tu veux clarifier.',
      note: 'Nous enregistrons ton etat actuel pour personnaliser le chat. La note est optionnelle, mais utile pour le premier contexte.',
    },
    chatAccessSteps: [
      { step: 'Etape 1', title: 'Ouvrir le chat IA', body: 'Apres cet ecran, tu seras redirige directement vers l espace de chat.' },
      { step: 'Etape 2', title: 'Choisir ta direction', body: 'Tu peux commencer par un soutien emotionnel, de la clarte, des objectifs ou une question directe.' },
      { step: 'Etape 3', title: 'Ecrire ton premier message', body: 'Dis ce que tu ressens maintenant, ce qui te preoccupe ou ce que tu veux mieux comprendre.' },
      { step: 'Etape 4', title: 'Recevoir un soutien guide', body: 'L IA repond avec des questions, clarifications et recommandations generales, sans diagnostic ni traitement.' },
    ],
    backAction: 'Retour',
    finishAction: 'Ouvrir le chat IA',
    consentRequired: 'Tu dois accepter les conditions pour continuer.',
    saveError: 'Nous n avons pas pu enregistrer ton profil initial. Reessaie.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Parcours d onboarding guide pour les nouveaux utilisateurs avant leur premiere conversation IA.',
  },
  it: {
    steps: [
      {
        shortTitle: 'Benvenuto',
        title: 'Benvenuto nel tuo spazio di chiarezza ed equilibrio',
        text: 'Qui lavorerai con un IA progettata per aiutarti a capire meglio cio che provi, chiarire i tuoi obiettivi e crescere al tuo ritmo.',
        button: 'Inizia',
      },
      {
        shortTitle: 'Piattaforma',
        title: 'Come puo aiutarti la piattaforma',
        bullets: [
          'analizza i tuoi stati emotivi',
          'pone domande intelligenti',
          'crea piani giornalieri e report',
          'ti aiuta a chiarire gli obiettivi',
          'offre supporto emotivo generale',
        ],
        button: 'Continua',
      },
      {
        shortTitle: 'Avvertenza',
        title: 'Cosa e importante sapere',
        text: 'La piattaforma offre supporto emotivo generale e strumenti di auto-riflessione. Non fornisce consigli medici, psicologici o terapeutici.',
        subtext: 'Se affronti una situazione seria, e importante cercare aiuto specializzato.',
        button: 'Ho capito',
      },
      {
        shortTitle: 'Privacy',
        title: 'Proteggiamo la tua privacy',
        text: 'Non raccogliamo nomi, indirizzi o dati personali sensibili. Usiamo solo un ID anonimo. I tuoi dati sono cifrati e possono essere eliminati in qualsiasi momento.',
        button: 'Accetta e continua',
      },
      {
        shortTitle: 'Profilo emotivo',
        title: 'Configura il tuo profilo emotivo',
        text: 'Prima della prima conversazione, imposta rapidamente il tuo stato attuale. Questo ci aiuta a iniziare in modo piu rilevante e calmo.',
        subtext: 'Puoi aggiungere anche qualche riga su cio che ti preoccupa ora.',
        button: 'Continua verso IA',
      },
    ],
    progressLabel: (current, total) => `Passo ${current} di ${total}`,
    consentLabel: {
      before: 'Accetto i ',
      terms: 'Termini e Condizioni',
      middle: ', la ',
      privacy: 'Privacy Policy',
      and: ' e l ',
      ai: 'Accordo IA',
      after: '.',
    },
    linkLabels: {
      terms: 'Termini e Condizioni',
      gdpr: 'Politica GDPR',
      ai: 'Accordo IA',
      cookies: 'Politica Cookies',
    },
    profile: {
      moodTitle: 'Come ti senti adesso?',
      moods: [
        { value: 'low', label: 'Basso', icon: '🌧️' },
        { value: 'ok', label: 'Stabile', icon: '🌿' },
        { value: 'good', label: 'Bene', icon: '🌤️' },
        { value: 'great', label: 'Molto bene', icon: '☀️' },
      ],
      energyTitle: 'Livello di energia',
      journalTitle: 'Nota iniziale',
      journalPlaceholder: 'Scrivi alcune righe su come ti senti, cosa pesa o cosa vuoi chiarire.',
      note: 'Salveremo il tuo stato attuale per personalizzare l esperienza chat. La nota e facoltativa, ma utile come primo contesto.',
    },
    chatAccessSteps: [
      { step: 'Passo 1', title: 'Apri chat IA', body: 'Dopo questa schermata verrai reindirizzato direttamente nell area chat.' },
      { step: 'Passo 2', title: 'Scegli la direzione', body: 'Puoi iniziare con supporto emotivo, chiarezza, obiettivi o una domanda diretta.' },
      { step: 'Passo 3', title: 'Scrivi il primo messaggio', body: 'Di cosa provi ora, cosa hai in mente o cosa vuoi capire meglio.' },
      { step: 'Passo 4', title: 'Ricevi supporto guidato', body: 'L IA risponde con domande, chiarimenti e raccomandazioni generali senza diagnosi o trattamenti.' },
    ],
    backAction: 'Indietro',
    finishAction: 'Apri chat IA',
    consentRequired: 'Devi accettare i termini per continuare.',
    saveError: 'Non siamo riusciti a salvare il profilo iniziale. Riprova.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Flusso guidato di onboarding per nuovi utenti prima della prima conversazione IA.',
  },
  es: {
    steps: [
      {
        shortTitle: 'Bienvenido',
        title: 'Bienvenido a tu espacio de claridad y equilibrio',
        text: 'Aqui trabajaras con una IA disenada para ayudarte a entender mejor lo que sientes, aclarar tus objetivos y crecer a tu ritmo.',
        button: 'Empezar',
      },
      {
        shortTitle: 'Plataforma',
        title: 'Como puede ayudarte la plataforma',
        bullets: [
          'analiza tus estados emocionales',
          'hace preguntas inteligentes',
          'crea planes diarios e informes',
          'te ayuda a aclarar objetivos',
          'ofrece apoyo emocional general',
        ],
        button: 'Continuar',
      },
      {
        shortTitle: 'Aviso',
        title: 'Lo importante que debes saber',
        text: 'La plataforma ofrece apoyo emocional general y herramientas de autorreflexion. No ofrece asesoramiento medico, psicologico ni terapeutico.',
        subtext: 'Si enfrentas una situacion grave, es importante buscar ayuda especializada.',
        button: 'Entiendo',
      },
      {
        shortTitle: 'Privacidad',
        title: 'Protegemos tu privacidad',
        text: 'No recopilamos nombres, direcciones ni datos personales sensibles. Usamos solo un ID anonimo. Tus datos estan cifrados y pueden eliminarse en cualquier momento.',
        button: 'Aceptar y continuar',
      },
      {
        shortTitle: 'Perfil emocional',
        title: 'Configura tu perfil emocional',
        text: 'Antes de la primera conversacion, define rapidamente tu estado actual. Esto nos ayuda a empezar de forma mas relevante y tranquila.',
        subtext: 'Tambien puedes escribir unas lineas sobre lo que te preocupa ahora.',
        button: 'Continuar hacia IA',
      },
    ],
    progressLabel: (current, total) => `Paso ${current} de ${total}`,
    consentLabel: {
      before: 'Acepto los ',
      terms: 'Terminos y Condiciones',
      middle: ', la ',
      privacy: 'Politica de Privacidad',
      and: ' y el ',
      ai: 'Acuerdo de IA',
      after: '.',
    },
    linkLabels: {
      terms: 'Terminos y Condiciones',
      gdpr: 'Politica GDPR',
      ai: 'Acuerdo de IA',
      cookies: 'Politica de Cookies',
    },
    profile: {
      moodTitle: 'Como te sientes ahora?',
      moods: [
        { value: 'low', label: 'Bajo', icon: '🌧️' },
        { value: 'ok', label: 'Estable', icon: '🌿' },
        { value: 'good', label: 'Bien', icon: '🌤️' },
        { value: 'great', label: 'Muy bien', icon: '☀️' },
      ],
      energyTitle: 'Nivel de energia',
      journalTitle: 'Nota inicial',
      journalPlaceholder: 'Escribe unas lineas sobre como te sientes, que pesa o que quieres aclarar.',
      note: 'Guardaremos tu estado actual para personalizar el chat. La nota es opcional, pero util para el primer contexto.',
    },
    chatAccessSteps: [
      { step: 'Paso 1', title: 'Abrir chat IA', body: 'Despues de esta pantalla seras redirigido directamente al area de chat.' },
      { step: 'Paso 2', title: 'Elegir direccion', body: 'Puedes empezar con apoyo emocional, claridad, objetivos o una pregunta directa.' },
      { step: 'Paso 3', title: 'Escribir primer mensaje', body: 'Di como te sientes ahora, que te preocupa o que quieres entender mejor.' },
      { step: 'Paso 4', title: 'Recibir apoyo guiado', body: 'La IA responde con preguntas, aclaraciones y recomendaciones generales sin diagnostico ni tratamiento.' },
    ],
    backAction: 'Atras',
    finishAction: 'Abrir chat IA',
    consentRequired: 'Debes aceptar los terminos para continuar.',
    saveError: 'No pudimos guardar el perfil inicial. Intentalo de nuevo.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Flujo guiado de onboarding para nuevos usuarios antes de su primera conversacion con IA.',
  },
  pl: {
    steps: [
      {
        shortTitle: 'Witamy',
        title: 'Witamy w Twojej przestrzeni jasnosci i rownowagi',
        text: 'Tutaj bedziesz pracowac z AI zaprojektowanym, aby pomoci Ci lepiej rozumiec emocje, wyjasnic cele i rozwijac sie we wlasnym tempie.',
        button: 'Start',
      },
      {
        shortTitle: 'Platforma',
        title: 'Jak platforma moze Ci pomoc',
        bullets: [
          'analizuje Twoje stany emocjonalne',
          'zadaje inteligentne pytania',
          'tworzy codzienne plany i raporty',
          'pomaga wyjasnic cele',
          'oferuje ogolne wsparcie emocjonalne',
        ],
        button: 'Kontynuuj',
      },
      {
        shortTitle: 'Informacja',
        title: 'Co warto wiedziec',
        text: 'Platforma oferuje ogolne wsparcie emocjonalne i narzedzia autorefleksji. Nie zapewnia porad medycznych, psychologicznych ani terapeutycznych.',
        subtext: 'W powaznej sytuacji nalezy skorzystac z pomocy specjalisty.',
        button: 'Rozumiem',
      },
      {
        shortTitle: 'Prywatnosc',
        title: 'Chronimy Twoja prywatnosc',
        text: 'Nie zbieramy imion, adresow ani wrazliwych danych osobowych. Uzywamy tylko anonimowego ID. Twoje dane sa szyfrowane i moga byc usuniete w kazdym momencie.',
        button: 'Akceptuj i kontynuuj',
      },
      {
        shortTitle: 'Profil emocjonalny',
        title: 'Ustaw swoj profil emocjonalny',
        text: 'Przed pierwsza rozmowa szybko ustaw swoj aktualny stan. To pomaga nam zaczac bardziej trafnie i spokojnie.',
        subtext: 'Mozez tez dodac kilka zdan o tym, co teraz najbardziej zajmuje Twoje mysli.',
        button: 'Przejdz do AI',
      },
    ],
    progressLabel: (current, total) => `Krok ${current} z ${total}`,
    consentLabel: {
      before: 'Akceptuje ',
      terms: 'Warunki korzystania',
      middle: ', ',
      privacy: 'Polityke Prywatnosci',
      and: ' oraz ',
      ai: 'Umowe AI',
      after: '.',
    },
    linkLabels: {
      terms: 'Warunki korzystania',
      gdpr: 'Polityka GDPR',
      ai: 'Umowa AI',
      cookies: 'Polityka Cookies',
    },
    profile: {
      moodTitle: 'Jak sie teraz czujesz?',
      moods: [
        { value: 'low', label: 'Nisko', icon: '🌧️' },
        { value: 'ok', label: 'Stabilnie', icon: '🌿' },
        { value: 'good', label: 'Dobrze', icon: '🌤️' },
        { value: 'great', label: 'Bardzo dobrze', icon: '☀️' },
      ],
      energyTitle: 'Poziom energii',
      journalTitle: 'Notatka poczatkowa',
      journalPlaceholder: 'Napisz kilka zdan o tym, co czujesz, co jest trudne lub co chcesz wyjasnic.',
      note: 'Zapiszemy Twoj aktualny stan, aby spersonalizowac rozmowe. Notatka jest opcjonalna, ale pomocna na poczatek.',
    },
    chatAccessSteps: [
      { step: 'Krok 1', title: 'Otworz chat AI', body: 'Po tym ekranie zostaniesz przekierowany bezposrednio do obszaru czatu.' },
      { step: 'Krok 2', title: 'Wybierz kierunek', body: 'Mozesz zaczac od wsparcia emocjonalnego, jasnosci, celow lub bezposredniego pytania.' },
      { step: 'Krok 3', title: 'Napisz pierwsza wiadomosc', body: 'Napisz, jak sie teraz czujesz, co Cie martwi lub co chcesz lepiej zrozumiec.' },
      { step: 'Krok 4', title: 'Otrzymaj prowadzone wsparcie', body: 'AI odpowiada pytaniami, wyjasnieniami i ogolnymi rekomendacjami bez diagnozy i leczenia.' },
    ],
    backAction: 'Wstecz',
    finishAction: 'Otworz chat AI',
    consentRequired: 'Musisz zaakceptowac warunki, aby kontynuowac.',
    saveError: 'Nie udalo sie zapisac profilu poczatkowego. Sprobuj ponownie.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Prowadzony onboarding dla nowych uzytkownikow przed pierwsza rozmowa z AI.',
  },
}

const SUPPORTED_ONBOARDING_LOCALES = ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'] as const

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return SUPPORTED_ONBOARDING_LOCALES.includes(code as (typeof SUPPORTED_ONBOARDING_LOCALES)[number]) ? code : 'en'
})

const text = computed(() => copy[localeCode.value] || copy.en)
const currentStep = ref(0)
const consentAccepted = ref(false)
const selectedMood = ref<MoodValue>('ok')
const energyLevel = ref(3)
const journalEntry = ref('')
const stepError = ref('')
const profileSaved = ref(false)
const isBusy = ref(false)

const activeStep = computed(() => text.value.steps[currentStep.value])
const isCurrentStepBlocked = computed(() => currentStep.value === 3 && !consentAccepted.value)
const tierVariant = computed(() => authStore.user?.membership_tier || 'free')
const tierHint = computed(() => {
  const labels = {
    ro: {
      premium: 'Ai acces extins: mai mult context în AI și recomandări avansate.',
      standard: 'Începi cu fluxul standard, iar funcțiile premium pot fi activate ulterior.',
      base: 'Parcurgi fluxul de bază; poți face upgrade oricând din profil.',
    },
    de: {
      premium: 'Du hast erweiterten Zugriff: mehr KI-Kontext und fortgeschrittene Empfehlungen.',
      standard: 'Du startest mit dem Standard-Flow und kannst Premium-Funktionen spater aktivieren.',
      base: 'Du nutzt den Basis-Flow und kannst jederzeit im Profil upgraden.',
    },
    fr: {
      premium: 'Tu as un acces etendu: plus de contexte IA et des recommandations avancees.',
      standard: 'Tu commences avec le flux standard et peux activer les fonctions premium plus tard.',
      base: 'Tu es sur le flux de base; tu peux passer en premium a tout moment depuis le profil.',
    },
    it: {
      premium: 'Hai accesso esteso: contesto IA piu ricco e raccomandazioni avanzate.',
      standard: 'Inizi con il flusso standard e puoi attivare le funzioni premium in seguito.',
      base: 'Sei nel flusso base; puoi fare upgrade in qualsiasi momento dal profilo.',
    },
    es: {
      premium: 'Tienes acceso ampliado: mas contexto de IA y recomendaciones avanzadas.',
      standard: 'Comienzas con el flujo estandar y puedes activar funciones premium despues.',
      base: 'Estas en el flujo base; puedes mejorar tu plan cuando quieras desde el perfil.',
    },
    pl: {
      premium: 'Masz rozszerzony dostep: bogatszy kontekst AI i zaawansowane rekomendacje.',
      standard: 'Zaczynasz od standardowego przeplywu i mozesz pozniej wlaczyc funkcje premium.',
      base: 'Korzystasz z podstawowego przeplywu; upgrade mozesz zrobic w dowolnym momencie w profilu.',
    },
    en: {
      premium: 'You have expanded access: richer AI context and advanced recommendations.',
      standard: 'You start with the standard flow and can unlock premium features later.',
      base: 'You are on the base flow; you can upgrade anytime from profile.',
    },
  } as const
  const localeLabels = labels[localeCode.value as keyof typeof labels] || labels.en

  if (['premium', 'vip'].includes(tierVariant.value)) {
    return localeLabels.premium
  }
  if (['basic', 'trial'].includes(tierVariant.value)) {
    return localeLabels.standard
  }
  return localeLabels.base
})

const featureIcons = ['🧠', '💬', '📋', '🎯', '🤝']
const featureDescriptions = computed(() => {
  const labels = {
    ro: [
      'Identifică tipare și te ajută să înțelegi ce simți.',
      'Conversații adaptate la contextul tău personal.',
      'Rapoarte și structuri adaptate ritmului tău.',
      'Transformă dorințele generale în direcții clare.',
      'Un spațiu calm pentru reflecție fără judecată.',
    ],
    de: [
      'Erkennt Muster und hilft dir, deinen emotionalen Zustand zu verstehen.',
      'Konversationen, angepasst an deinen aktuellen Kontext.',
      'Tagesstruktur und Berichtshinweise passend zu deinem Rhythmus.',
      'Macht aus allgemeinen Absichten klare nachste Schritte.',
      'Ein ruhiger Raum fur Reflexion ohne Bewertung.',
    ],
    fr: [
      'Identifie les modeles et t aide a comprendre ton etat emotionnel.',
      'Conversations adaptees a ton contexte personnel.',
      'Structure quotidienne et reperes de progression selon ton rythme.',
      'Transforme des intentions generales en directions claires.',
      'Un espace calme de reflexion sans jugement.',
    ],
    it: [
      'Identifica i pattern e ti aiuta a capire il tuo stato emotivo.',
      'Conversazioni adattate al tuo contesto personale.',
      'Struttura quotidiana e indicazioni in linea con il tuo ritmo.',
      'Trasforma intenzioni generali in prossimi passi chiari.',
      'Uno spazio calmo per riflettere senza giudizio.',
    ],
    es: [
      'Identifica patrones y te ayuda a entender tu estado emocional.',
      'Conversaciones adaptadas a tu contexto personal actual.',
      'Estructura diaria y orientacion segun tu ritmo.',
      'Convierte intenciones generales en siguientes pasos claros.',
      'Un espacio sereno para reflexionar sin juicio.',
    ],
    pl: [
      'Wykrywa wzorce i pomaga zrozumiec Twoj stan emocjonalny.',
      'Rozmowy dopasowane do Twojego aktualnego kontekstu.',
      'Codzienna struktura i wskazowki zgodne z Twoim rytmem.',
      'Zmienia ogolne intencje w konkretne kolejne kroki.',
      'Spokojna przestrzen do refleksji bez oceniania.',
    ],
    en: [
      'Identifies patterns and helps you understand your emotional state.',
      'Conversations adapted to your current personal context.',
      'Daily structure and report guidance matched to your rhythm.',
      'Turns broad intentions into clear next directions.',
      'A calm space for reflection without judgment.',
    ],
  } as const
  return labels[localeCode.value as keyof typeof labels] || labels.en
})

const disclaimerText = computed(() => {
  const labels = {
    ro: {
      offerTitle: 'Ce oferă platforma',
      limitTitle: 'Ce nu oferă platforma',
    },
    de: {
      offerTitle: 'Was die Plattform bietet',
      limitTitle: 'Was die Plattform nicht bietet',
    },
    fr: {
      offerTitle: 'Ce que la plateforme offre',
      limitTitle: 'Ce que la plateforme n offre pas',
    },
    it: {
      offerTitle: 'Cosa offre la piattaforma',
      limitTitle: 'Cosa la piattaforma non offre',
    },
    es: {
      offerTitle: 'Lo que ofrece la plataforma',
      limitTitle: 'Lo que la plataforma no ofrece',
    },
    pl: {
      offerTitle: 'Co oferuje platforma',
      limitTitle: 'Czego platforma nie oferuje',
    },
    en: {
      offerTitle: 'What the platform offers',
      limitTitle: 'What the platform does not offer',
    },
  } as const
  return labels[localeCode.value as keyof typeof labels] || labels.en
})

const onboardingStepKeys = ['welcome', 'platform', 'disclaimer', 'privacy', 'profile']

usePublicSeo({
  title: computed(() => text.value.seoTitle),
  description: computed(() => text.value.seoDescription),
  noindex: true,
})

onMounted(async () => {
  authStore.hydrate()
  if (authStore.user?.onboarding_completed !== false) {
    await router.replace(chatPath.value)
    return
  }
  await trackOnboarding('onboarding_started', { tier_variant: tierVariant.value })
})

function goBack() {
  stepError.value = ''
  currentStep.value = Math.max(0, currentStep.value - 1)
}

async function saveInitialProfile() {
  if (profileSaved.value) {
    return
  }

  const tasks: Promise<unknown>[] = [
    fetchApi('/wellbeing/checkins', {
      method: 'POST',
      body: { mood: selectedMood.value, energy_level: energyLevel.value },
    }),
  ]

  if (journalEntry.value.trim()) {
    const questions = await fetchApi<Array<{ id: number }>>(`/journal/questions?language=${localeCode.value}`)
    if (questions[0]?.id) {
      tasks.push(
        fetchApi('/journal/entries', {
          method: 'POST',
          body: {
            question: questions[0].id,
            content: journalEntry.value.trim(),
            emotions: [selectedMood.value],
          },
        }),
      )
    }
  }

  await Promise.all(tasks)
  await trackOnboarding('onboarding_profile_saved', {
    has_journal: Boolean(journalEntry.value.trim()),
    tier_variant: tierVariant.value,
  })
  profileSaved.value = true
}

async function trackOnboarding(eventName: string, properties: Record<string, unknown>) {
  try {
    await fetchApi('/analytics/track', {
      method: 'POST',
      body: {
        event_name: eventName,
        source: 'frontend',
        properties,
      },
    })
  } catch {
    // Best-effort analytics tracking only.
  }
}

async function completeOnboarding() {
  const user = await fetchApi<typeof authStore.user>('/me', {
    method: 'PATCH',
    body: { onboarding_completed: true },
  })
  if (user) {
    authStore.setUser(user)
  }
}

async function goNext() {
  stepError.value = ''

  if (currentStep.value === 3 && !consentAccepted.value) {
    stepError.value = text.value.consentRequired
    return
  }

  isBusy.value = true
  try {
    if (currentStep.value === 4) {
      await saveInitialProfile()
    }

    if (currentStep.value === text.value.steps.length - 1) {
      await trackOnboarding('onboarding_step_completed', {
        step_key: onboardingStepKeys[currentStep.value] || `step_${currentStep.value + 1}`,
        step_index: currentStep.value + 1,
        tier_variant: tierVariant.value,
      })
      await completeOnboarding()
      await trackOnboarding('onboarding_completed', { tier_variant: tierVariant.value })
      await router.push(chatPath.value)
      return
    }

    await trackOnboarding('onboarding_step_completed', {
      step_key: onboardingStepKeys[currentStep.value] || `step_${currentStep.value + 1}`,
      step_index: currentStep.value + 1,
      tier_variant: tierVariant.value,
    })

    currentStep.value += 1
  } catch {
    stepError.value = text.value.saveError
  } finally {
    isBusy.value = false
  }
}
</script>