# X版Jockie Music Docサイト（Next.js静的エクスポート）をnginxで配信
FROM node:22-alpine AS build
WORKDIR /app
RUN corepack enable
COPY docs/package.json docs/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY docs/ ./
RUN pnpm build

FROM nginx:alpine
COPY --from=build /app/out/ /usr/share/nginx/html/
EXPOSE 80
