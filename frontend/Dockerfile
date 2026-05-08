FROM node:22-alpine AS builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY docker/nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=builder /frontend/dist /usr/share/nginx/html

EXPOSE 80
