import { defineNuxtConfig } from "nuxt/config";

const normalizeAppBaseUrl = (value?: string) => {
  const normalized = (value || "/").trim();
  if (!normalized || normalized === "/") {
    return "/";
  }

  return `/${normalized.replace(/^\/+|\/+$/g, "")}/`;
};

const escapeRegExp = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const appBaseUrl = normalizeAppBaseUrl(process.env.NUXT_PUBLIC_APP_BASE_URL);
const appBasePath = appBaseUrl === "/" ? "" : appBaseUrl.replace(/\/$/, "");
const withBase = (path: string) => `${appBasePath}${path.startsWith("/") ? path : `/${path}`}` || "/";
const adminBasePath = withBase("/ro/admin");
const routeRules = {
  "/**": {
    headers: {
      "cache-control": "no-store",
    },
  },
  "/_nuxt/**": {
    headers: {
      "cache-control": "public, max-age=31536000, immutable",
    },
  },
  ...(appBasePath
    ? {
        [`${appBasePath}/**`]: {
          headers: {
            "cache-control": "no-store",
          },
        },
        [`${appBasePath}/_nuxt/**`]: {
          headers: {
            "cache-control": "public, max-age=31536000, immutable",
          },
        },
      }
    : {}),
};

export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  app: {
    baseURL: appBaseUrl,
    head: {
      title: "Doisense",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "apple-mobile-web-app-capable", content: "yes" },
        { name: "apple-mobile-web-app-status-bar-style", content: "default" },
        { name: "apple-mobile-web-app-title", content: "Doisense" },
        { name: "mobile-web-app-capable", content: "yes" },
      ],
      link: [
        { rel: "apple-touch-icon", href: withBase("/apple-touch-icon.png") },
      ],
      script: [
        {
          key: "chunk-recovery",
          src: withBase("/chunk-recovery.js"),
          defer: true,
        },
      ],
    },
  },
  runtimeConfig: {
    public: {
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || "https://www.doisense.eu",
      appBaseUrl,
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api",
      googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID || "",
    },
  },
  experimental: {
    payloadExtraction: true,
    emitRouteChunkError: "automatic",
  },
  nitro: {
    compressPublicAssets: true,
    routeRules,
  },
  sourcemap: {
    client: process.env.NODE_ENV !== "production",
    server: process.env.NODE_ENV !== "production",
  },
  modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss", "@nuxtjs/i18n", "@nuxt/content", "@vite-pwa/nuxt"],
  pwa: {
    disable: false,
    registerType: "autoUpdate",
    manifest: {
      id: appBaseUrl,
      name: "Doisense",
      short_name: "Doisense",
      description: "Your wellbeing companion. Journal, chat with AI, and follow guided programs.",
      theme_color: "#0f766e",
      background_color: "#f3f5f8",
      display: "standalone",
      start_url: appBaseUrl,
      scope: appBaseUrl,
      lang: "en",
      icons: [
        {
            src: withBase("/pwa-192x192.png"),
          sizes: "192x192",
            type: "image/png",
          purpose: "any maskable",
        },
        {
            src: withBase("/pwa-512x512.png"),
          sizes: "512x512",
            type: "image/png",
          purpose: "any maskable",
        },
      ],
    },
    workbox: {
      navigateFallback: appBaseUrl,
      navigateFallbackDenylist: [
        new RegExp(`^${escapeRegExp(adminBasePath)}(?:/|$)`),
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