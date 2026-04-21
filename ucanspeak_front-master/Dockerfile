FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

# Nuxt 4 build output в .output
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

ENV HOST=0.0.0.0 \
    PORT=3000 \
    NODE_ENV=production

CMD ["node", ".output/server/index.mjs"]
