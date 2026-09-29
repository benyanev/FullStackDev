# Frontend image — two stages:
#   1. build the React app with Node (npm run build → dist/)
#   2. serve dist/ with nginx, which also forwards /api and /static to the backend

# ---- Stage 1: build ----
# Same Node major version as local development (package-lock.json is from npm 11)
FROM node:24-alpine AS build
WORKDIR /app

# Cypress is a dev tool for E2E tests; skip downloading its ~500 MB binary
ENV CYPRESS_INSTALL_BINARY=0

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---- Stage 2: serve ----
# stable = the maintained nginx branch that still gets security fixes
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
