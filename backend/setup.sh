#!/bin/bash

# Script para setup do backend
echo "🚀 Configurando backend..."

# Instalar dependências
echo "📦 Instalando dependências..."
npm install

# Build TypeScript
echo "🔨 Compilando TypeScript..."
npm run build

echo "✅ Backend configurado com sucesso!"
echo ""
echo "Para rodar em desenvolvimento:"
echo "  npm run dev"
echo ""
echo "Para rodar em produção:"
echo "  npm start"
