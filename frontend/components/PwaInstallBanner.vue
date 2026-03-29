<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="translate-y-8 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-8 opacity-0"
  >
    <div
      v-if="showBanner"
      class="fixed inset-x-4 bottom-4 z-[120] mx-auto w-auto max-w-xl rounded-2xl border border-teal-900/20 bg-gradient-to-br from-teal-50 via-cyan-50 to-white p-4 shadow-2xl"
    >
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-sm font-semibold tracking-wide text-teal-900">
            {{ t('pwaInstall.title') }}
          </p>
          <p class="mt-1 text-xs text-stone-700">
            {{ t('pwaInstall.subtitle') }}
          </p>
        </div>
        <button
          type="button"
          class="rounded-md px-2 py-1 text-xs text-stone-600 hover:bg-white/80"
          @click="onDismiss(false)"
        >
          {{ t('pwaInstall.notNow') }}
        </button>
      </div>

      <div v-if="isIos" class="mt-3 rounded-xl bg-white/80 p-3">
        <ol class="space-y-1 text-xs text-stone-800">
          <li>1. {{ t('pwaInstall.iosStep1') }}</li>
          <li>2. {{ t('pwaInstall.iosStep2') }}</li>
          <li>3. {{ t('pwaInstall.iosStep3') }}</li>
        </ol>

        <div class="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            class="rounded-full bg-teal-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-800"
            @click="onManualInstalled"
          >
            {{ t('pwaInstall.iAdded') }}
          </button>
          <button
            type="button"
            class="rounded-full border border-stone-300 bg-white px-3 py-1.5 text-xs font-medium text-stone-700 hover:border-stone-400"
            @click="onDismiss(true)"
          >
            {{ t('pwaInstall.neverShow') }}
          </button>
        </div>
      </div>

      <div v-else-if="isAndroid" class="mt-3 rounded-xl bg-white/80 p-3">
        <template v-if="canNativeInstall">
          <p class="text-xs text-stone-800">
            {{ t('pwaInstall.androidPromptReady') }}
          </p>
          <div class="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              class="rounded-full bg-teal-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-800"
              @click="onInstall"
            >
              {{ t('pwaInstall.androidInstall') }}
            </button>
            <button
              type="button"
              class="rounded-full border border-stone-300 bg-white px-3 py-1.5 text-xs font-medium text-stone-700 hover:border-stone-400"
              @click="onDismiss(true)"
            >
              {{ t('pwaInstall.neverShow') }}
            </button>
          </div>
        </template>

        <template v-else>
          <ol class="space-y-1 text-xs text-stone-800">
            <li>1. {{ t('pwaInstall.androidStep1') }}</li>
            <li>2. {{ t('pwaInstall.androidStep2') }}</li>
          </ol>

          <div class="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              class="rounded-full bg-teal-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-800"
              @click="onManualInstalled"
            >
              {{ t('pwaInstall.iAdded') }}
            </button>
            <button
              type="button"
              class="rounded-full border border-stone-300 bg-white px-3 py-1.5 text-xs font-medium text-stone-700 hover:border-stone-400"
              @click="onDismiss(true)"
            >
              {{ t('pwaInstall.neverShow') }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { usePwaInstall } from '~/composables/usePwaInstall'

const { t } = useI18n()
const {
  init,
  showBanner,
  isIos,
  isAndroid,
  canNativeInstall,
  dismiss,
  triggerInstall,
  markManualInstall,
} = usePwaInstall()

onMounted(() => {
  void init()
})

async function onInstall() {
  await triggerInstall()
}

async function onManualInstalled() {
  await markManualInstall()
}

async function onDismiss(neverAgain: boolean) {
  await dismiss(neverAgain)
}
</script>
