# Stage de desarrollo: hot-reload con Vite
FROM node:20-alpine AS dev

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# En desarrollo, el código se monta como volumen (ver docker-compose.override.yml)
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage de build para producción
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Stage de producción: Nginx interno sirve la SPA
# y proxea /api/* al backend en la red de Docker Compose.
FROM nginx:alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
