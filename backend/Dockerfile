FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package*.json ./
COPY tsconfig.json ./

# Instalar dependências
RUN npm ci --only=production && \
    npm install -g typescript

# Copiar código fonte
COPY src ./src

# Build TypeScript
RUN npm run build

# Limpar dev dependencies
RUN npm prune --production

# Expor porta
EXPOSE 4000

# Comando de início
CMD ["npm", "start"]
