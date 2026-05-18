FROM node:20-alpine AS builder

WORKDIR /app
COPY pnpm-lock.yaml package.json ./
RUN npm install -g pnpm@9
COPY . .
RUN pnpm install --frozen-lockfile
ARG NUXT_PUBLIC_APP_BASE_URL=/doisense/
ARG NUXT_PUBLIC_SITE_URL=https://projects.doimih.net
ENV NUXT_PUBLIC_APP_BASE_URL=${NUXT_PUBLIC_APP_BASE_URL}
ENV NUXT_PUBLIC_SITE_URL=${NUXT_PUBLIC_SITE_URL}
RUN pnpm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.output /app/.output
COPY --from=builder /app/package.json ./
ENV NODE_ENV=production
ENV NITRO_PORT=3000
ENV HOST=0.0.0.0
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
