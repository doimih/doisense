export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  app: {
    baseURL: process.env.NUXT_PUBLIC_APP_BASE_URL || "/doisense/",
    head: {
      title: "Doisense",
      meta: [{ charset: "utf-8" }, { name: "viewport", content: "width=device-width, initial-scale=1" }],
    },
  },
  runtimeConfig: {
    public: {
      appBaseUrl: process.env.NUXT_PUBLIC_APP_BASE_URL || "/doisense/",
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api",
    },
  },
  modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss", "@nuxtjs/i18n"],
  i18n: {
    locales: [
      { code: "ro", iso: "ro-RO", name: "Română", file: "ro.json" },
      { code: "en", iso: "en-US", name: "English", file: "en.json" },
      { code: "de", iso: "de-DE", name: "Deutsch", file: "de.json" },
      { code: "it", iso: "it-IT", name: "Italiano", file: "it.json" },
      { code: "es", iso: "es-ES", name: "Español", file: "es.json" },
      { code: "pl", iso: "pl-PL", name: "Polski", file: "pl.json" },
    ],
    langDir: "locales",
    defaultLocale: "en",
    strategy: "prefix_except_default",
    detectBrowserLanguage: { useCookie: true, cookieKey: "i18n_redirect" },
  },
  typescript: { strict: true },
  devtools: { enabled: true },
});
