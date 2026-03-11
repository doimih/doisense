import { defineNuxtConfig } from "nuxt/config";

export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  app: {
    baseURL: process.env.NUXT_PUBLIC_APP_BASE_URL || "/doisense/",
    head: {
      title: "Doisense",
      meta: [{ charset: "utf-8" }, { name: "viewport", content: "width=device-width, initial-scale=1" }],
      link: [
        { rel: "apple-touch-icon", href: "/doisense/pwa-192x192.svg" },
      ],
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
  experimental: {
    payloadExtraction: true,
  },
  nitro: {
    compressPublicAssets: true,
    routeRules: {
      "/**": {
        headers: {
          "cache-control": "no-store",
        },
      },
      "/doisense/**": {
        headers: {
          "cache-control": "no-store",
        },
      },
      "/_nuxt/**": {
        headers: {
          "cache-control": "public, max-age=31536000, immutable",
        },
      },
      "/doisense/_nuxt/**": {
        headers: {
          "cache-control": "public, max-age=31536000, immutable",
        },
      },
    },
  },
  sourcemap: {
    client: process.env.NODE_ENV !== "production",
    server: process.env.NODE_ENV !== "production",
  },
  modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss", "@nuxtjs/i18n", "@nuxt/content", "@vite-pwa/nuxt"],
  pwa: {
    registerType: "autoUpdate",
    manifest: {
      id: "/doisense/",
      name: "Doisense",
      short_name: "Doisense",
      description: "Your wellbeing companion. Journal, chat with AI, and follow guided programs.",
      theme_color: "#0f766e",
      background_color: "#f3f5f8",
      display: "standalone",
      start_url: "/doisense/",
      scope: "/doisense/",
      lang: "en",
      icons: [
        {
          src: "/doisense/pwa-192x192.svg",
          sizes: "192x192",
          type: "image/svg+xml",
          purpose: "any maskable",
        },
        {
          src: "/doisense/pwa-512x512.svg",
          sizes: "512x512",
          type: "image/svg+xml",
          purpose: "any maskable",
        },
      ],
    },
    workbox: {
      navigateFallback: "/doisense/offline",
      navigateFallbackDenylist: [
        /^\/doisense\/(?:[a-z]{2}\/)?admin(?:\/|$)/,
      ],
      globPatterns: ["**/*.{js,css,html,ico,png,svg,json,txt,woff2}"],
    },
    client: {
      installPrompt: true,
      periodicSyncForUpdates: 3600,
    },
    devOptions: {
      enabled: false,
      suppressWarnings: true,
      type: "module",
    },
  },
  i18n: {
    restructureDir: "",
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
  devtools: { enabled: process.env.NODE_ENV !== "production" },
});