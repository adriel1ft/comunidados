"""
Definição das ferramentas do MCP
Não importamos mcp aqui, apenas definimos as funções
"""
from typing import List, Dict, Any
import logging
from .scrapers.camara_deputados import CamaraScraper
from .config import settings

logger = logging.getLogger(__name__)


async def buscar_projetos_recentes(
    tema: str,
    limite: int = 10
) -> List[Dict[str, Any]]:
    """
    Busca projetos de lei recentes sobre um tema específico.
    
    Args:
        tema: Tema ou palavra-chave para buscar
        limite: Número máximo de resultados (padrão: 10)
    
    Returns:
        Lista de projetos de lei com informações básicas
    """
    logger.info(f"Buscando projetos recentes sobre: {tema}")
    
    scraper = CamaraScraper(
        headless=settings.scraping_headless,
        timeout=settings.scraping_timeout
    )
    
    return await scraper.buscar_projetos_recentes(tema, limite)


async def buscar_projetos_mais_votados(
    tema: str = "",
    limite: int = 10
) -> List[Dict[str, Any]]:
    """
    Busca projetos de lei com mais votações recentes.
    
    Args:
        tema: Tema opcional para filtrar (padrão: "")
        limite: Número máximo de resultados (padrão: 10)
    
    Returns:
        Lista de projetos mais votados com número de votações
    """
    logger.info(f"Buscando projetos mais votados sobre: {tema or 'todos os temas'}")
    
    scraper = CamaraScraper(
        headless=settings.scraping_headless,
        timeout=settings.scraping_timeout
    )
    
    return await scraper.buscar_projetos_mais_votados(tema or None, limite)


async def buscar_noticias_tema(
    tema: str,
    limite: int = 10
) -> List[Dict[str, Any]]:
    """
    Busca notícias da homepage de um tema específico na Câmara.
    
    Args:
        tema: Nome do tema (ex: "agropecuaria", "saude", "economia")
        limite: Número máximo de notícias (padrão: 10)
    
    Returns:
        Lista de notícias com título, descrição, data e link
    """
    logger.info(f"Buscando notícias sobre: {tema}")
    
    scraper = CamaraScraper(
        headless=settings.scraping_headless,
        timeout=settings.scraping_timeout
    )
    
    return await scraper.buscar_noticias_tema(tema, limite)


async def obter_detalhes_projeto(projeto_id: str) -> Dict[str, Any]:
    """
    Obtém detalhes completos de um projeto de lei específico.
    
    Args:
        projeto_id: ID do projeto (ex: "PL-1234/2024" ou ID numérico)
    
    Returns:
        Detalhes completos do projeto incluindo ementa, autores, tramitação e votações
    """
    logger.info(f"Obtendo detalhes do projeto: {projeto_id}")
    
    scraper = CamaraScraper(
        headless=settings.scraping_headless,
        timeout=settings.scraping_timeout
    )
    
    return await scraper.obter_projeto_detalhado(projeto_id)


async def buscar_noticias_relacionadas(
    tema: str,
    dias_atras: int = 7
) -> List[Dict[str, Any]]:
    """
    Busca notícias relacionadas a temas legislativos.
    Alias para buscar_noticias_tema (mantido para compatibilidade).
    
    Args:
        tema: Tema para buscar notícias
        dias_atras: Período de busca em dias (não usado no scraping atual)
    
    Returns:
        Lista de notícias com links para projetos relacionados
    """
    return await buscar_noticias_tema(tema, limite=10)

async def identificar_projetos_opiniao(mensagem_usuario: str, projetos_sugeridos: list) -> list:
    """
    Identifica sobre qual(is) PL(s) o usuário está emitindo opinião, a partir da mensagem e dos PLs sugeridos.
    Args:
        mensagem_usuario: Texto da opinião do usuário
        projetos_sugeridos: Lista de PLs sugeridos anteriormente
    Returns:
        Lista de PLs identificados na opinião
    """
    # Lógica de matching pode ser NLP, fuzzy, etc.
    # Aqui é só um stub
    return []

async def classificar_tema_opiniao(mensagem_usuario: str) -> str:
    """
    Classifica o tema principal da opinião do usuário.
    Args:
        mensagem_usuario: Texto da opinião do usuário
    Returns:
        Tema identificado (ex: 'saúde', 'educação', ...)
    """
    return ""

async def classificar_sentimento_opiniao(mensagem_usuario: str) -> str:
    """
    Classifica o sentimento da opinião do usuário.
    Args:
        mensagem_usuario: Texto da opinião do usuário
    Returns:
        Sentimento identificado (ex: 'alegre', 'raivoso', ...)
    """
    return ""

async def registrar_opiniao_usuario(
    projetos: list,
    tema: str,
    sentimento: str,
    opiniao: str,
    contexto: str = None
) -> dict:
    """
    Registra a opinião do usuário sobre um ou mais projetos de lei, tema e sentimento.
    Args:
        projetos: Lista de identificadores dos PLs (ex: ['PL-1234/2024', ...]) ou ['nova-lei']
        tema: Tema principal da opinião (ex: 'saúde', 'educação', ...)
        sentimento: Sentimento do usuário (ex: 'alegre', 'receoso', 'raivoso', 'esperançoso', ...)
        opiniao: Texto livre da opinião do usuário
        contexto: (opcional) Mensagem original/contexto
    Returns:
        dict com status e confirmação
    """
    logger.info(f"Registrando opinião: projetos={projetos}, tema={tema}, sentimento={sentimento}, opiniao={opiniao}")
    # Aqui você pode salvar em banco, enviar para fila, etc.
    return {
        "status": "ok",
        "projetos": projetos,
        "tema": tema,
        "sentimento": sentimento,
        "opiniao": opiniao,
        "contexto": contexto
    }