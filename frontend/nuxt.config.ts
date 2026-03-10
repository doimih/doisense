import { defineNuxtConfig } from "nuxt/config";

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
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || "https://projects.doimih.net",
      appBaseUrl: process.env.NUXT_PUBLIC_APP_BASE_URL || "/doisense/",
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api",
      googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID || "",
      appleClientId: process.env.NUXT_PUBLIC_APPLE_CLIENT_ID || "",
      appleRedirectUri: process.env.NUXT_PUBLIC_APPLE_REDIRECT_URI || "",
    },
  },
  modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss", "@nuxtjs/i18n", "@nuxt/content"],
  i18n: {
    restructureDir: "",
    lazy: true,
    locales: [
      { code: "ro", language: "ro-RO", name: "Română", file: "ro.json" },
      { code: "en", language: "en-US", name: "English", file: "en.json" },
      { code: "de", language: "de-DE", name: "Deutsch", file: "de.json" },
      { code: "fr", language: "fr-FR", name: "Français", file: "fr.json" },
      { code: "it", language: "it-IT", name: "Italiano", file: "it.json" },
      { code: "es", language: "es-ES", name: "Español", file: "es.json" },
      { code: "pl", language: "pl-PL", name: "Polski", file: "pl.json" },
    ],
    langDir: "locales",
    defaultLocale: "en",
    strategy: "prefix_except_default",
    detectBrowserLanguage: { useCookie: true, cookieKey: "i18n_redirect" },
  },
  typescript: { strict: true },
  devtools: { enabled: true },
});