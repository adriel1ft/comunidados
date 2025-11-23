"""
Script de teste para validar os scrapers implementados
"""
import asyncio
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_mcp_projetos_lei.scrapers.camara_deputados import CamaraScraper


async def testar_scraper():
    """Testa todas as funções do scraper"""
    
    print("=" * 80)
    print("TESTE DO SCRAPER DA CÂMARA DOS DEPUTADOS")
    print("=" * 80)
    
    scraper = CamaraScraper(headless=True, timeout=30)
    
    # Teste 1: Buscar notícias de um tema
    print("\nTESTE 1: Buscar notícias sobre SAÚDE")
    print("-" * 80)
    noticias = await scraper.buscar_noticias_tema("saude", limite=3)
    if noticias:
        print(f"Encontradas {len(noticias)} notícias:")
        for i, noticia in enumerate(noticias[:3], 1):
            print(f"\n{i}. {noticia.get('titulo')}")
            print(f"   Tipo: {noticia.get('tipo')}")
            print(f"   Data: {noticia.get('data')}")
            print(f"   Link: {noticia.get('link')[:80]}...")
    else:
        print("Nenhuma notícia encontrada")
    
    # Teste 2: Buscar projetos recentes
    print("\n\nTESTE 2: Buscar projetos recentes sobre EDUCAÇÃO")
    print("-" * 80)
    projetos_recentes = await scraper.buscar_projetos_recentes("educacao", limite=3)
    if projetos_recentes:
        print(f"Encontrados {len(projetos_recentes)} projetos recentes:")
        for i, proj in enumerate(projetos_recentes[:3], 1):
            print(f"\n{i}. {proj.get('id')}")
            print(f"   Tipo: {proj.get('tipo')}")
            print(f"   Ementa: {proj.get('ementa')[:100]}...")
            print(f"   Data: {proj.get('data_apresentacao')}")
    else:
        print("Nenhum projeto recente encontrado")
    
    # Teste 3: Buscar projetos mais votados
    print("\n\nTESTE 3: Buscar projetos mais votados")
    print("-" * 80)
    projetos_votados = await scraper.buscar_projetos_mais_votados(tema=None, limite=3)
    if projetos_votados:
        print(f"Encontrados {len(projetos_votados)} projetos mais votados:")
        for i, proj in enumerate(projetos_votados[:3], 1):
            print(f"\n{i}. {proj.get('id')}")
            print(f"   Ementa: {proj.get('ementa')[:100]}...")
            print(f"   Votações: {proj.get('num_votacoes', 'N/A')}")
            print(f"   Última votação: {proj.get('ultima_votacao', 'N/A')}")
    else:
        print("Nenhum projeto votado encontrado")
    
    # Teste 4: Obter detalhes de um projeto específico
    if projetos_recentes:
        print("\n\nTESTE 4: Obter detalhes de um projeto específico")
        print("-" * 80)
        projeto_id = projetos_recentes[0].get('id')
        print(f"Buscando detalhes de: {projeto_id}")
        
        detalhes = await scraper.obter_projeto_detalhado(projeto_id)
        if detalhes:
            print(f"\nDetalhes obtidos:")
            print(f"   ID: {detalhes.get('id')}")
            print(f"   Tipo: {detalhes.get('tipo')}")
            print(f"   Ementa: {detalhes.get('ementa')[:150]}...")
            print(f"   Situação: {detalhes.get('situacao')}")
            print(f"   Autores: {len(detalhes.get('autores', []))} autor(es)")
            print(f"   Tramitações: {len(detalhes.get('tramitacao', []))} registro(s)")
            print(f"   Votações: {len(detalhes.get('votacoes', []))} votação(ões)")
            
            if detalhes.get('autores'):
                print(f"\n   Primeiro autor:")
                autor = detalhes['autores'][0]
                print(f"     - {autor.get('nome')} ({autor.get('partido')}/{autor.get('uf')})")
        else:
            print("Não foi possível obter os detalhes")
    
    print("\n" + "=" * 80)
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(testar_scraper())
