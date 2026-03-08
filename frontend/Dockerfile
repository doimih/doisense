FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY . .
ARG NUXT_PUBLIC_APP_BASE_URL=/doisense/
ENV NUXT_PUBLIC_APP_BASE_URL=${NUXT_PUBLIC_APP_BASE_URL}
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.output /app/.output
COPY --from=builder /app/package.json ./
ENV NODE_ENV=production
ENV NITRO_PORT=3000
ENV HOST=0.0.0.0
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
