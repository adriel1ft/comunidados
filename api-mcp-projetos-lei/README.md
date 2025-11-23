# API MCP - Projetos de Lei

Servidor MCP (Model Context Protocol) para fornecer dados sobre projetos de lei e legislações brasileiras através de scraping da Câmara dos Deputados.

## Visão Geral

Esta API implementa um servidor MCP que disponibiliza ferramentas para:

- **Buscar projetos de lei** recentes e mais votados
- **Obter detalhes completos** de projetos específicos (autores, tramitação, votações)
- **Buscar notícias** sobre temas legislativos
- Integração com a API oficial de Dados Abertos da Câmara

## Recursos Implementados

### Tools Disponíveis

1. **buscar_projetos_recentes**: Busca projetos de lei do ano atual por tema
2. **buscar_projetos_mais_votados**: Busca projetos com mais votações nos últimos 30 dias
3. **buscar_noticias_tema**: Busca notícias da homepage de temas específicos
4. **obter_detalhes_projeto**: Obtém detalhes completos de um projeto (ementa, autores, tramitação, votações)
5. **buscar_noticias_relacionadas**: Alias para buscar notícias por tema

### Resources

- **links://e-cidadania**: Links importantes para participação cidadã

### Prompts

- **prompt_analise_projeto**: Template para análise de projetos de lei

## Quick Start

### Pré-requisitos

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)**: Gerenciador de pacotes ultrarrápido

### Instalação

```bash
# Instalar uv se ainda não tiver
curl -LsSf https://astral.sh/uv/install.sh | sh

# Criar ambiente e instalar dependências
cd api-mcp-projetos-lei
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows
uv pip install -e .
```

### Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
uv pip install -e ".[dev]"

# Rodar testes
python test_simple.py

# Formatação
black src/
ruff check src/
```

## Configuração

Copie `.env.example` para `.env`:

```bash
cp .env.example .env
```

Variáveis disponíveis:

```bash
OPENAI_API_KEY="sk-..."
MCP_SERVER_PORT=8000
SCRAPING_TIMEOUT=30
SCRAPING_HEADLESS=true
```

## Uso

### Iniciar o Servidor

```bash
api-mcp-projetos-lei
```

O servidor estará disponível na porta configurada (padrão: 8000) usando transporte `streamable-http`.

### Exemplo de Uso Programático

```python
from api_mcp_projetos_lei.scrapers.camara_deputados import CamaraScraper

scraper = CamaraScraper()

# Buscar projetos recentes
projetos = await scraper.buscar_projetos_recentes("educacao", limite=10)

# Buscar mais votados
votados = await scraper.buscar_projetos_mais_votados(tema="saude", limite=10)

# Obter detalhes
detalhes = await scraper.obter_projeto_detalhado("PL-1234/2024")
```

## Arquitetura

```
api-mcp-projetos-lei/
├── src/
│   └── api_mcp_projetos_lei/
│       ├── __init__.py
│       ├── main.py              # Servidor MCP + registros de tools
│       ├── config.py            # Configurações e settings
│       ├── tools.py             # Implementação das tools MCP
│       ├── resources.py         # Resources do MCP
│       ├── prompts.py           # Prompts templates
│       └── scrapers/
│           └── camara_deputados.py  # Scraper da Câmara
├── test_simple.py               # Teste de validação
├── test_scrapers.py             # Teste completo
├── .env.example                 # Exemplo de variáveis
└── pyproject.toml               # Dependências
```

## Fontes de Dados

Todos os dados são obtidos de fontes oficiais:

- **API de Dados Abertos da Câmara**: `https://dadosabertos.camara.leg.br/api/v2`
- **Site oficial da Câmara**: `https://www.camara.leg.br`

## Tecnologias

- **FastMCP**: Framework para servidores MCP
- **SeleniumBase**: Scraping de páginas web
- **Requests**: Consumo de APIs REST
- **BeautifulSoup4**: Parsing de HTML
- **Pydantic**: Validação de dados e configurações

## Temas Suportados

O scraper de notícias suporta os seguintes temas da Câmara:

- agropecuaria
- cidades-transportes
- ciencia-tecnologia
- consumidor
- direitos-humanos
- economia
- educacao
- meio-ambiente
- politica
- relacoes-exteriores
- saude
- seguranca
- trabalho
  - [ ] Homepage do assunto
  - [ ] Notícia relacionada ao assunto
  - [ ] Projeto de lei relacionado ao assunto
- [ ] Sistema de crawler periódico ou on-demand
- [ ] Extração de links de propostas de lei em notícias
