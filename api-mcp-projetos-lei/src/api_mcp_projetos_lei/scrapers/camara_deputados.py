"""
Scraper para a Câmara dos Deputados
"""
from typing import List, Dict, Any, Optional
import logging
from seleniumbase import Driver
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CamaraScraper:
    """
    Scraper para coletar dados da Câmara dos Deputados
    
    Implementa scraping de:
    - Homepage do assunto
    - Notícias relacionadas ao assunto
    - Projetos de lei relacionados ao assunto
    """
    
    BASE_URL_SITE = "https://www.camara.leg.br"
    BASE_URL_API = "https://dadosabertos.camara.leg.br/api/v2"
    
    # Mapeamento de temas para URLs
    TEMAS = {
        "agropecuaria": "agropecuaria",
        "cidades-transportes": "cidades-e-transportes",
        "ciencia-tecnologia": "ciencia-tecnologia-e-comunicacoes",
        "consumidor": "consumidor",
        "direitos-humanos": "direitos-humanos",
        "economia": "economia",
        "educacao": "educacao-cultura-e-esportes",
        "meio-ambiente": "meio-ambiente-e-energia",
        "politica": "politica-e-administracao-publica",
        "relacoes-exteriores": "relacoes-exteriores",
        "saude": "saude",
        "seguranca": "seguranca",
        "trabalho": "trabalho-previdencia-e-assistencia"
    }
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
    
    def _normalizar_tema(self, tema: str) -> Optional[str]:
        """Normaliza o nome do tema para o formato usado nas URLs"""
        tema_lower = tema.lower().strip()
        
        # Busca exata
        if tema_lower in self.TEMAS:
            return self.TEMAS[tema_lower]
        
        # Busca por substring
        for key, value in self.TEMAS.items():
            if tema_lower in key or tema_lower in value:
                return value
        
        return None
    
    async def buscar_noticias_tema(self, tema: str, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca notícias da homepage de um tema específico
        
        Args:
            tema: Nome do tema (ex: "agropecuaria", "saude")
            limite: Número máximo de notícias a retornar
            
        Returns:
            Lista de notícias com título, descrição, data e link
        """
        tema_url = self._normalizar_tema(tema)
        if not tema_url:
            logger.warning(f"Tema não encontrado: {tema}")
            return []
        
        url = f"{self.BASE_URL_SITE}/assuntos/{tema_url}"
        logger.info(f"Scraping notícias de: {url}")
        
        driver = None
        try:
            driver = Driver(browser="chrome", headless=self.headless)
            driver.set_page_load_timeout(60)
            driver.open(url)
            # Aguarda um pouco para a página carregar
            import time
            time.sleep(3)
            
            html = driver.get_page_source()
            soup = BeautifulSoup(html, 'html.parser')
            
            noticias = []
            
            # Notícia em destaque (manchete)
            manchete = soup.find("article", class_="noticia-manchete")
            if manchete:
                titulo_elem = manchete.find("h2", class_="noticia-manchete__titulo")
                desc_elem = manchete.find("p", class_="noticia-manchete__descricao")
                link_elem = manchete.find("a", class_="faux-link__target")
                
                if titulo_elem and link_elem:
                    noticias.append({
                        "tipo": "manchete",
                        "titulo": titulo_elem.get_text(strip=True),
                        "descricao": desc_elem.get_text(strip=True) if desc_elem else "",
                        "link": link_elem.get("href", ""),
                        "data": datetime.now().strftime("%Y-%m-%d")
                    })
            
            # Últimas notícias
            ultimas = soup.find("div", class_="ultimas-noticias")
            if ultimas:
                items = ultimas.find_all("article", class_="noticia-lista")
                for item in items[:limite-1]:
                    titulo_elem = item.find("h3", class_="noticia-lista__titulo")
                    desc_elem = item.find("p", class_="noticia-lista__descricao")
                    link_elem = item.find("a")
                    data_elem = item.find("time")
                    
                    if titulo_elem and link_elem:
                        noticias.append({
                            "tipo": "ultima",
                            "titulo": titulo_elem.get_text(strip=True),
                            "descricao": desc_elem.get_text(strip=True) if desc_elem else "",
                            "link": link_elem.get("href", ""),
                            "data": data_elem.get("datetime", "") if data_elem else ""
                        })
            
            logger.info(f"Encontradas {len(noticias)} notícias para {tema}")
            return noticias[:limite]
            
        except Exception as e:
            logger.error(f"Erro ao scraping notícias de {tema}: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
    
    async def buscar_projetos_recentes(self, tema: str, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca projetos de lei recentes via API de Dados Abertos
        
        Args:
            tema: Tema para buscar
            limite: Número máximo de projetos
            
        Returns:
            Lista de projetos recentes
        """
        logger.info(f"Buscando projetos recentes sobre: {tema}")
        
        try:
            # Busca projetos do ano atual
            ano_atual = datetime.now().year
            params = {
                "ordem": "DESC",
                "ordenarPor": "id",
                "ano": ano_atual,
                "itens": 100  # Pega mais para filtrar por tema depois
            }
            
            response = requests.get(
                f"{self.BASE_URL_API}/proposicoes",
                params=params,
                headers={"accept": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Erro na API: {response.status_code}")
                return []
            
            data = response.json()
            proposicoes = data.get("dados", [])
            
            projetos = []
            tema_lower = tema.lower()
            
            for prop in proposicoes:
                # Pula se não tem ano (proposições antigas/inválidas)
                if not prop.get("ano") or prop.get("ano") == 0:
                    continue
                    
                ementa = str(prop.get("ementa", "")).lower()
                keywords = str(prop.get("keywords", "")).lower()
                sigla_tipo = str(prop.get("siglaTipo", "")).lower()
                
                # Filtra por tema se especificado (busca variações)
                tema_match = False
                if not tema:
                    tema_match = True
                else:
                    # Remove acentos e busca variações do tema
                    tema_busca = tema_lower.replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('ç', 'c')
                    ementa_busca = ementa.replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('ç', 'c')
                    
                    if tema_busca in ementa_busca or tema_lower in keywords or tema_lower in ementa:
                        tema_match = True
                    # Busca palavras relacionadas
                    elif tema_lower == 'educacao' and ('ensino' in ementa or 'escola' in ementa or 'professor' in ementa):
                        tema_match = True
                    elif tema_lower == 'saude' and ('hospital' in ementa or 'medico' in ementa or 'sus' in ementa):
                        tema_match = True
                
                if tema_match:
                    projetos.append({
                        "id": f"{prop.get('siglaTipo')}-{prop.get('numero')}/{prop.get('ano')}",
                        "uri": prop.get("uri", ""),
                        "tipo": prop.get("siglaTipo", ""),
                        "numero": prop.get("numero"),
                        "ano": prop.get("ano"),
                        "ementa": prop.get("ementa", ""),
                        "data_apresentacao": prop.get("dataApresentacao", ""),
                        "link": f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={prop.get('id')}"
                    })
                    
                    if len(projetos) >= limite:
                        break
            
            logger.info(f"Encontrados {len(projetos)} projetos recentes")
            return projetos
            
        except Exception as e:
            logger.error(f"Erro ao buscar projetos recentes: {str(e)}")
            return []
    
    async def buscar_projetos_mais_votados(self, tema: Optional[str] = None, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca projetos com mais votações recentes via API
        
        Args:
            tema: Tema opcional para filtrar
            limite: Número máximo de projetos
            
        Returns:
            Lista de projetos mais votados
        """
        logger.info(f"Buscando projetos mais votados sobre: {tema}")
        
        try:
            # Busca votações do último mês
            data_fim = datetime.now()
            data_inicio = data_fim - timedelta(days=30)
            
            params = {
                "dataInicio": data_inicio.strftime("%Y-%m-%d"),
                "dataFim": data_fim.strftime("%Y-%m-%d"),
                "ordem": "DESC",
                "ordenarPor": "data",
                "itens": 100
            }
            
            response = requests.get(
                f"{self.BASE_URL_API}/votacoes",
                params=params,
                headers={"accept": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Erro na API de votações: {response.status_code}")
                return []
            
            data = response.json()
            votacoes = data.get("dados", [])
            
            # Agrupa por proposição
            proposicoes_votadas = {}
            for votacao in votacoes:
                prop_uri = votacao.get("uriProposicaoObjeto")
                if prop_uri:
                    if prop_uri not in proposicoes_votadas:
                        proposicoes_votadas[prop_uri] = {
                            "uri": prop_uri,
                            "descricao": votacao.get("proposicaoObjeto", ""),
                            "num_votacoes": 0,
                            "ultima_votacao": votacao.get("data", "")
                        }
                    proposicoes_votadas[prop_uri]["num_votacoes"] += 1
            
            # Ordena por número de votações
            projetos_ordenados = sorted(
                proposicoes_votadas.values(),
                key=lambda x: x["num_votacoes"],
                reverse=True
            )
            
            # Busca detalhes dos projetos mais votados
            projetos = []
            for proj in projetos_ordenados[:limite]:
                try:
                    # Extrai ID da URI
                    prop_id = proj["uri"].split("/")[-1]
                    detalhes = await self._buscar_detalhes_api(prop_id)
                    
                    if detalhes:
                        detalhes["num_votacoes"] = proj["num_votacoes"]
                        detalhes["ultima_votacao"] = proj["ultima_votacao"]
                        
                        # Filtra por tema se especificado
                        if not tema or tema.lower() in detalhes.get("ementa", "").lower():
                            projetos.append(detalhes)
                            
                except Exception as e:
                    logger.warning(f"Erro ao buscar detalhes do projeto: {str(e)}")
                    continue
            
            logger.info(f"Encontrados {len(projetos)} projetos mais votados")
            return projetos[:limite]
            
        except Exception as e:
            logger.error(f"Erro ao buscar projetos mais votados: {str(e)}")
            return []
    
    async def _buscar_detalhes_api(self, proposicao_id: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes de uma proposição via API"""
        try:
            response = requests.get(
                f"{self.BASE_URL_API}/proposicoes/{proposicao_id}",
                headers={"accept": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json().get("dados", {})
            
            return {
                "id": f"{data.get('siglaTipo')}-{data.get('numero')}/{data.get('ano')}",
                "uri": data.get("uri", ""),
                "tipo": data.get("siglaTipo", ""),
                "numero": data.get("numero"),
                "ano": data.get("ano"),
                "ementa": data.get("ementa", ""),
                "data_apresentacao": data.get("dataApresentacao", ""),
                "autor": ", ".join([a.get("nome", "") for a in data.get("autores", [])]),
                "link": f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={proposicao_id}"
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes da proposição {proposicao_id}: {str(e)}")
            return None
    
    async def obter_projeto_detalhado(self, projeto_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um projeto específico
        
        Args:
            projeto_id: ID da proposição (número numérico) ou formato "PL-1234/2024"
            
        Returns:
            Detalhes completos do projeto
        """
        logger.info(f"Buscando detalhes do projeto: {projeto_id}")
        
        # Extrai ID numérico se vier no formato "PL-1234/2024"
        if "-" in projeto_id or "/" in projeto_id:
            try:
                parts = projeto_id.replace("-", " ").replace("/", " ").split()
                if len(parts) >= 3:
                    tipo, numero, ano = parts[0], parts[1], parts[2]
                    
                    params = {
                        "siglaTipo": tipo,
                        "numero": numero,
                        "ano": ano
                    }
                    
                    response = requests.get(
                        f"{self.BASE_URL_API}/proposicoes",
                        params=params,
                        headers={"accept": "application/json"},
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        proposicoes = data.get("dados", [])
                        if proposicoes:
                            projeto_id = str(proposicoes[0].get("id"))
                    
            except Exception as e:
                logger.error(f"Erro ao converter formato do projeto: {str(e)}")
                return {}
        
        # Busca detalhes via API
        try:
            response = requests.get(
                f"{self.BASE_URL_API}/proposicoes/{projeto_id}",
                headers={"accept": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Projeto não encontrado: {projeto_id}")
                return {}
            
            data = response.json().get("dados", {})
            
            projeto = {
                "id": f"{data.get('siglaTipo')}-{data.get('numero')}/{data.get('ano')}",
                "id_numerico": projeto_id,
                "uri": data.get("uri", ""),
                "tipo": data.get("siglaTipo", ""),
                "numero": data.get("numero"),
                "ano": data.get("ano"),
                "ementa": data.get("ementa", ""),
                "ementa_detalhada": data.get("ementaDetalhada", ""),
                "keywords": data.get("keywords", ""),
                "data_apresentacao": data.get("dataApresentacao", ""),
                "situacao": data.get("statusProposicao", {}).get("descricaoSituacao", ""),
                "link": f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={projeto_id}",
                "autores": [],
                "tramitacao": [],
                "votacoes": []
            }
            
            # Busca autores
            try:
                autores_resp = requests.get(
                    f"{self.BASE_URL_API}/proposicoes/{projeto_id}/autores",
                    headers={"accept": "application/json"},
                    timeout=self.timeout
                )
                if autores_resp.status_code == 200:
                    autores_data = autores_resp.json().get("dados", [])
                    projeto["autores"] = [
                        {
                            "nome": a.get("nome", ""),
                            "tipo": a.get("tipo", ""),
                            "partido": a.get("siglaPartido", ""),
                            "uf": a.get("siglaUF", "")
                        }
                        for a in autores_data
                    ]
            except Exception as e:
                logger.warning(f"Erro ao buscar autores: {str(e)}")
            
            # Busca tramitação
            try:
                tram_resp = requests.get(
                    f"{self.BASE_URL_API}/proposicoes/{projeto_id}/tramitacoes",
                    headers={"accept": "application/json"},
                    timeout=self.timeout
                )
                if tram_resp.status_code == 200:
                    tram_data = tram_resp.json().get("dados", [])
                    projeto["tramitacao"] = [
                        {
                            "data": t.get("dataHora", ""),
                            "sequencia": t.get("sequencia", 0),
                            "descricao": t.get("despacho", ""),
                            "orgao": t.get("siglaOrgao", "")
                        }
                        for t in tram_data[:10]
                    ]
            except Exception as e:
                logger.warning(f"Erro ao buscar tramitação: {str(e)}")
            
            # Busca votações
            try:
                vot_resp = requests.get(
                    f"{self.BASE_URL_API}/proposicoes/{projeto_id}/votacoes",
                    headers={"accept": "application/json"},
                    timeout=self.timeout
                )
                if vot_resp.status_code == 200:
                    vot_data = vot_resp.json().get("dados", [])
                    projeto["votacoes"] = [
                        {
                            "data": v.get("data", ""),
                            "descricao": v.get("descricao", ""),
                            "aprovacao": v.get("aprovacao"),
                            "orgao": v.get("siglaOrgao", "")
                        }
                        for v in vot_data
                    ]
            except Exception as e:
                logger.warning(f"Erro ao buscar votações: {str(e)}")
            
            logger.info(f"Detalhes do projeto {projeto_id} obtidos com sucesso")
            return projeto
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do projeto: {str(e)}")
            return {}
    
    async def buscar_projetos(self, tema: str, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca geral de projetos (combina recentes e votados)
        """
        logger.info(f"Busca geral de projetos sobre: {tema}")
        
        recentes = await self.buscar_projetos_recentes(tema, limite // 2)
        votados = await self.buscar_projetos_mais_votados(tema, limite // 2)
        
        todos = recentes + votados
        vistos = set()
        unicos = []
        
        for proj in todos:
            proj_id = proj.get("id") or proj.get("uri")
            if proj_id not in vistos:
                vistos.add(proj_id)
                unicos.append(proj)
        
        return unicos[:limite]
