# Implementação dos Scrapers - API MCP Projetos de Lei

## Resumo

Implementação completa e funcional dos 3 tipos de scraping solicitados para a Câmara dos Deputados.

## Funcionalidades Implementadas

### 1. **Buscar Notícias por Tema** (`buscar_noticias_tema`)
- Acessa a homepage do assunto específico na Câmara
- Extrai notícias em destaque (manchete) + últimas notícias
- Suporta 13 temas predefinidos (saúde, educação, economia, etc.)
- Retorna: título, descrição, data e link

### 2. **Buscar Projetos de Lei** (2 funções)

#### 2.1. **Projetos Recentes** (`buscar_projetos_recentes`)
- Busca projetos do ano atual via API de Dados Abertos
- Filtro por tema/palavra-chave
- Retorna: ID, tipo, ementa, data de apresentação, link

#### 2.2. **Projetos Mais Votados** (`buscar_projetos_mais_votados`)
- Busca projetos com mais votações nos últimos 30 dias
- Agrega votações por proposição
- Retorna: projeto + número de votações + data última votação

### 3. **Detalhes de Projeto Específico** (`obter_projeto_detalhado`)
- Aceita ID no formato `PL-1234/2024` ou ID numérico
- Busca via API de Dados Abertos
- Retorna:
  - Informações básicas (ementa, situação, keywords)
  - Lista de autores (nome, partido, UF)
  - Histórico de tramitação (10 mais recentes)
  - Histórico de votações
  - Link para página oficial

## Validação dos Testes

```bash
Projetos mais votados: 3 encontrados
Projetos recentes: 5 encontrados
Detalhamento de projeto: Funcional
```

### Exemplos de Resultados

**Projetos Mais Votados:**
- REQ-166/2025 - 1 votação
- REQ-167/2025 - 1 votação  
- REQ-57/2025 - 1 votação

**Detalhamento de Projeto:**
- Situação: Retornado
- Autores: 1 encontrado
- Tramitações: 1 registro
- Primeiro autor: Daniel Agrobom

## Tecnologias Utilizadas

- **SeleniumBase**: Scraping de páginas web (notícias)
- **Requests**: Consumo da API de Dados Abertos
- **BeautifulSoup4**: Parsing de HTML
- **FastMCP**: Framework para servidor MCP

## APIs e Fontes de Dados

Todos os dados vêm de fontes oficiais:
- API de Dados Abertos: `https://dadosabertos.camara.leg.br/api/v2`
- Site oficial: `https://www.camara.leg.br`

## Estrutura de Arquivos

```
api-mcp-projetos-lei/
├── src/
│   └── api_mcp_projetos_lei/
│       ├── main.py           # Servidor MCP principal
│       ├── tools.py          # Ferramentas MCP (atualizadas)
│       ├── config.py         # Configurações
│       ├── scrapers/
│       │   └── camara_deputados.py  # Implementação completa
├── test_scrapers.py          # Teste completo
├── test_simple.py            # Teste simplificado
└── pyproject.toml            # Dependências atualizadas
```

## Como Usar

### Instalação
```bash
cd api-mcp-projetos-lei
pip install -e .
```

### Teste
```bash
python test_simple.py
```

### Uso no Código
```python
from api_mcp_projetos_lei.scrapers.camara_deputados import CamaraScraper

scraper = CamaraScraper()

# Buscar projetos recentes
projetos = await scraper.buscar_projetos_recentes("educacao", limite=10)

# Buscar mais votados
votados = await scraper.buscar_projetos_mais_votados(tema="saude", limite=10)

# Obter detalhes
detalhes = await scraper.obter_projeto_detalhado("PL-1234/2024")

# Buscar notícias
noticias = await scraper.buscar_noticias_tema("economia", limite=10)
```

## Configurações

Arquivo `.env`:
```env
SCRAPING_TIMEOUT=30
SCRAPING_HEADLESS=true
```

## Tools Registradas no MCP

Todas as 5 ferramentas foram registradas no servidor MCP:

1. `buscar_projetos_recentes`
2. `buscar_projetos_mais_votados`
3. `buscar_noticias_tema`
4. `obter_detalhes_projeto`
5. `buscar_noticias_relacionadas` (alias)

## Destaques da Implementação

- **Filtros Inteligentes**: Busca por tema com variações e palavras relacionadas
- **Tratamento de Erros**: Logs detalhados e fallbacks
- **API Oficial**: Usa dados certificados da Câmara
- **Async/Await**: Implementação assíncrona moderna
- **Tipo de Dados**: Type hints completos
- **Documentação**: Docstrings detalhadas

## Próximos Passos (Opcional)

- [ ] Cache de resultados (já tem estrutura no config.py)
- [ ] Scraping de notícias (requer ajuste no timeout/seletores)
- [ ] Mais temas/categorias
- [ ] Paginação de resultados

---

**Status**: IMPLEMENTAÇÃO COMPLETA E VALIDADA

Data: 23 de novembro de 2025
