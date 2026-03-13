<template>
  <section class="mx-auto max-w-5xl space-y-6 rounded-2xl border border-sky-100 bg-gradient-to-br from-[#f7fbff] via-[#f5f9fc] to-[#eef4f8] p-4 md:p-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">{{ text.title }}</h1>
        <p class="mt-1 text-sm text-slate-600">
          {{ text.subtitle }}
        </p>
      </div>
      <NuxtLink
        :to="localePath('/profile')"
        class="rounded-lg border border-sky-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-sky-50"
      >
        {{ text.backToProfile }}
      </NuxtLink>
    </div>

    <div v-if="!authStore.user?.is_superuser" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      {{ text.adminOnly }}
    </div>

    <template v-else>
      <div class="rounded-xl border border-sky-200 bg-white p-4 shadow-sm">
        <form class="space-y-3" @submit.prevent="uploadImage">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">{{ text.chooseImage }}</label>
            <input
              ref="fileInput"
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              class="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 file:mr-3 file:rounded-md file:border-0 file:bg-sky-100 file:px-3 file:py-1.5 file:font-medium file:text-slate-800"
              @change="onFileChange"
            >
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              type="submit"
              :disabled="uploading || !selectedFile"
              class="rounded-lg bg-sky-300 px-4 py-2 text-sm font-semibold text-stone-900 transition hover:bg-sky-200 disabled:opacity-50"
            >
              {{ uploading ? text.uploading : text.uploadImage }}
            </button>
            <button
              type="button"
              :disabled="loading"
              class="rounded-lg border border-sky-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-sky-50 disabled:opacity-50"
              @click="loadImages"
            >
              {{ text.refreshList }}
            </button>
          </div>
          <p v-if="uploadError" class="text-sm text-red-600">{{ uploadError }}</p>
          <p v-if="uploadSuccess" class="text-sm text-emerald-700">{{ uploadSuccess }}</p>
        </form>
      </div>

      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">{{ text.uploadedImages }}</h2>
          <p class="text-xs text-slate-500">{{ images.length }} {{ text.itemsLabel }}</p>
        </div>

        <div v-if="loading" class="rounded-xl border border-sky-200 bg-white p-4 text-sm text-slate-600">{{ text.loading }}</div>

        <div v-else-if="!images.length" class="rounded-xl border border-sky-200 bg-white p-4 text-sm text-slate-600">
          {{ text.noImages }}
        </div>

        <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="item in images"
            :key="item.url"
            class="overflow-hidden rounded-xl border border-sky-200 bg-white shadow-sm"
          >
            <img :src="item.url" :alt="item.name" class="h-40 w-full bg-slate-100 object-cover" loading="lazy" decoding="async">
            <div class="space-y-2 p-3">
              <p class="truncate text-sm font-medium text-slate-800" :title="item.name">{{ item.name }}</p>
              <p class="text-xs text-slate-500">{{ formatSize(item.size) }}</p>
              <button
                type="button"
                class="w-full rounded-md border border-sky-200 bg-sky-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-sky-100"
                @click="copyUrl(item.url)"
              >
                {{ text.copyUrl }}
              </button>
            </div>
          </article>
        </div>
      </div>
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

const text = computed(() => {
  return {
    ro: {
      title: 'Setari imagini',
      subtitle: 'Incarca imagini proiect si copiaza rapid linkurile pentru Hero sau continut CMS.',
      backToProfile: 'Inapoi la profil',
      adminOnly: 'Aceasta sectiune este disponibila doar pentru conturile admin.',
      chooseImage: 'Alege imagine',
      uploading: 'Se incarca...',
      uploadImage: 'Incarca imagine',
      refreshList: 'Reincarca lista',
      uploadedImages: 'Imagini incarcate',
      itemsLabel: 'element(e)',
      loading: 'Se incarca...',
      noImages: 'Nu exista imagini incarcate inca.',
      copyUrl: 'Copiaza URL',
      loadError: 'Nu am putut incarca lista de imagini.',
      uploadedSuccess: 'Incarcat:',
      uploadFailed: 'Incarcarea a esuat.',
      copied: 'URL copiat in clipboard.',
      copyFailed: 'Nu am putut copia URL-ul. Copiaza manual din browser.',
    },
    en: {
      title: 'Image Settings',
      subtitle: 'Upload project images and copy links quickly for Hero or CMS content.',
      backToProfile: 'Back to profile',
      adminOnly: 'This section is available only for admin accounts.',
      chooseImage: 'Choose image',
      uploading: 'Uploading...',
      uploadImage: 'Upload image',
      refreshList: 'Refresh list',
      uploadedImages: 'Uploaded images',
      itemsLabel: 'item(s)',
      loading: 'Loading...',
      noImages: 'No images uploaded yet.',
      copyUrl: 'Copy URL',
      loadError: 'Could not load images list.',
      uploadedSuccess: 'Uploaded:',
      uploadFailed: 'Upload failed.',
      copied: 'URL copied to clipboard.',
      copyFailed: 'Could not copy URL. Copy manually from browser.',
    },
    de: {
      title: 'Bildeinstellungen',
      subtitle: 'Projektbilder hochladen und Links schnell fuer Hero- oder CMS-Inhalte kopieren.',
      backToProfile: 'Zurueck zum Profil',
      adminOnly: 'Dieser Bereich ist nur fuer Admin-Konten verfuegbar.',
      chooseImage: 'Bild waehlen',
      uploading: 'Wird hochgeladen...',
      uploadImage: 'Bild hochladen',
      refreshList: 'Liste aktualisieren',
      uploadedImages: 'Hochgeladene Bilder',
      itemsLabel: 'Element(e)',
      loading: 'Wird geladen...',
      noImages: 'Noch keine Bilder hochgeladen.',
      copyUrl: 'URL kopieren',
      loadError: 'Bildliste konnte nicht geladen werden.',
      uploadedSuccess: 'Hochgeladen:',
      uploadFailed: 'Upload fehlgeschlagen.',
      copied: 'URL in die Zwischenablage kopiert.',
      copyFailed: 'URL konnte nicht kopiert werden. Bitte manuell kopieren.',
    },
    fr: {
      title: 'Parametres images',
      subtitle: 'Telechargez des images et copiez rapidement les liens pour le Hero ou le CMS.',
      backToProfile: 'Retour au profil',
      adminOnly: 'Cette section est reservee aux comptes administrateur.',
      chooseImage: 'Choisir une image',
      uploading: 'Telechargement...',
      uploadImage: 'Telecharger l\'image',
      refreshList: 'Actualiser la liste',
      uploadedImages: 'Images telechargees',
      itemsLabel: 'element(s)',
      loading: 'Chargement...',
      noImages: 'Aucune image telechargee pour le moment.',
      copyUrl: 'Copier l\'URL',
      loadError: 'Impossible de charger la liste des images.',
      uploadedSuccess: 'Telecharge:',
      uploadFailed: 'Echec du telechargement.',
      copied: 'URL copiee dans le presse-papiers.',
      copyFailed: 'Impossible de copier l\'URL. Copiez-la manuellement.',
    },
    it: {
      title: 'Impostazioni immagini',
      subtitle: 'Carica immagini di progetto e copia rapidamente i link per Hero o contenuti CMS.',
      backToProfile: 'Torna al profilo',
      adminOnly: 'Questa sezione e disponibile solo per account admin.',
      chooseImage: 'Scegli immagine',
      uploading: 'Caricamento...',
      uploadImage: 'Carica immagine',
      refreshList: 'Aggiorna lista',
      uploadedImages: 'Immagini caricate',
      itemsLabel: 'elemento/i',
      loading: 'Caricamento...',
      noImages: 'Nessuna immagine caricata.',
      copyUrl: 'Copia URL',
      loadError: 'Impossibile caricare la lista immagini.',
      uploadedSuccess: 'Caricato:',
      uploadFailed: 'Caricamento fallito.',
      copied: 'URL copiato negli appunti.',
      copyFailed: 'Impossibile copiare URL. Copia manualmente dal browser.',
    },
    es: {
      title: 'Ajustes de imagenes',
      subtitle: 'Sube imagenes del proyecto y copia enlaces rapidamente para Hero o contenido CMS.',
      backToProfile: 'Volver al perfil',
      adminOnly: 'Esta seccion esta disponible solo para cuentas admin.',
      chooseImage: 'Elegir imagen',
      uploading: 'Subiendo...',
      uploadImage: 'Subir imagen',
      refreshList: 'Actualizar lista',
      uploadedImages: 'Imagenes subidas',
      itemsLabel: 'elemento(s)',
      loading: 'Cargando...',
      noImages: 'Aun no hay imagenes subidas.',
      copyUrl: 'Copiar URL',
      loadError: 'No se pudo cargar la lista de imagenes.',
      uploadedSuccess: 'Subido:',
      uploadFailed: 'La subida fallo.',
      copied: 'URL copiada al portapapeles.',
      copyFailed: 'No se pudo copiar la URL. Copia manualmente desde el navegador.',
    },
    pl: {
      title: 'Ustawienia obrazow',
      subtitle: 'Przeslij obrazy projektu i szybko kopiuj linki do sekcji Hero lub CMS.',
      backToProfile: 'Powrot do profilu',
      adminOnly: 'Ta sekcja jest dostepna tylko dla kont administratora.',
      chooseImage: 'Wybierz obraz',
      uploading: 'Przesylanie...',
      uploadImage: 'Przeslij obraz',
      refreshList: 'Odswiez liste',
      uploadedImages: 'Przeslane obrazy',
      itemsLabel: 'element(y)',
      loading: 'Ladowanie...',
      noImages: 'Brak przeslanych obrazow.',
      copyUrl: 'Kopiuj URL',
      loadError: 'Nie mozna zaladowac listy obrazow.',
      uploadedSuccess: 'Przeslano:',
      uploadFailed: 'Przesylanie nie powiodlo sie.',
      copied: 'URL skopiowany do schowka.',
      copyFailed: 'Nie mozna skopiowac URL. Skopiuj recznie z przegladarki.',
    },
  }[localeCode.value] || {
    title: 'Image Settings',
    subtitle: 'Upload project images and copy links quickly for Hero or CMS content.',
    backToProfile: 'Back to profile',
    adminOnly: 'This section is available only for admin accounts.',
    chooseImage: 'Choose image',
    uploading: 'Uploading...',
    uploadImage: 'Upload image',
    refreshList: 'Refresh list',
    uploadedImages: 'Uploaded images',
    itemsLabel: 'item(s)',
    loading: 'Loading...',
    noImages: 'No images uploaded yet.',
    copyUrl: 'Copy URL',
    loadError: 'Could not load images list.',
    uploadedSuccess: 'Uploaded:',
    uploadFailed: 'Upload failed.',
    copied: 'URL copied to clipboard.',
    copyFailed: 'Could not copy URL. Copy manually from browser.',
  }
})

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const loading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')

type ImageItem = {
  name: string
  url: string
  size: number
  updated_at: string
}

const images = ref<ImageItem[]>([])

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
  uploadError.value = ''
  uploadSuccess.value = ''
}

async function loadImages() {
  if (!authStore.user?.is_superuser) return
  loading.value = true
  try {
    const res = await fetchApi<{ items: ImageItem[] }>('/settings/images', { method: 'GET' })
    images.value = res.items || []
  } catch {
    uploadError.value = text.value.loadError
  } finally {
    loading.value = false
  }
}

async function uploadImage() {
  if (!selectedFile.value) return

  uploadError.value = ''
  uploadSuccess.value = ''
  uploading.value = true

  try {
    const data = new FormData()
    data.append('image', selectedFile.value)

    const uploaded = await fetchApi<{ name: string; url: string }>('/settings/images', {
      method: 'POST',
      body: data,
    })

    uploadSuccess.value = `${text.value.uploadedSuccess} ${uploaded.name}`
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    await loadImages()
  } catch (error: any) {
    uploadError.value = error?.data?.detail || text.value.uploadFailed
  } finally {
    uploading.value = false
  }
}

async function copyUrl(url: string) {
  try {
    await navigator.clipboard.writeText(url)
    uploadSuccess.value = text.value.copied
    uploadError.value = ''
  } catch {
    uploadError.value = text.value.copyFailed
  }
}

function formatSize(size: number): string {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

onMounted(async () => {
  await loadImages()
})
</script>
