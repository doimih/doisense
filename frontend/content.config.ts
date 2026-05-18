import { defineCollection, defineContentConfig } from "@nuxt/content";

export default defineContentConfig({
  collections: {
    cms: defineCollection({
      type: "page",
      source: "cms/**/*.md",
    }),
  },
});
