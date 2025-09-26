FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

# Crea e usa un utente non-root
RUN adduser -D appuser && chown -R appuser /app
USER appuser

# Healthcheck per sicurezza
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD wget --spider -q http://localhost:3000/ || exit 1

CMD ["npm", "start"]
