# API 1 - MCP / projetos de lei

- api pra servir o agente via mcp fastapi
- vai ter um crawler de rotina (ou ondemand) embutido pra pegar as legislações / notícias mais recentes ou mais relevantes
  - grey zone, pretendo usar seleniumbase e fazer 3 páginas pro assunto
  - homepage do assunto
  - notícia relacionada ao assunto
  - projeto de lei relacionado ao assunto
- também ter como pegar as notícias e identificar o link da proposta de lei
- ter uma forma de visitar a página do projeto de lei e extrair as informações para que possamos passar pro usuário
- biblioteca fast-mcp

# Documentação sobre a camara dos deputados e e-cidadão

1. https://www.camara.leg.br/servicos-ao-cidadao

- caso o usuário se interesse em algum desses serviços, podemos enviar esse link

2. https://www12.senado.leg.br/institucional/ouvidoria

- o usuário também pode querer contatar o senado federal, o link é esse

3. ideia legislativa pagina principal: https://www12.senado.leg.br/ecidadania/principalideia

- caso o usuário queira propor uma ideia legislativa, esse é o link

4. oficina legislativa: https://www12.senado.leg.br/ecidadania/oficinalegislativa

- parecido com a ideia legislativa, mas caso o usuário tenha um interesse escolar em participar de uma oficina legislativa
  Obs.: Fazer de um formato que seja entendível para agentes. Como uma biblioteca de links e informações.  
  Pegar conceito do context7

# API 2 - Dados abertos da câmara dos deputados

- api para servir os dados abertos da camara dos deputados,
- fazer por mcp e fazer uma estruturação inicial a partir do swagger
- https://dadosabertos.camara.leg.br/swagger/api.html?tab=api

# Homepage do projeto

- trazer as principais informações do projeto e ter um call to action
- já implementado

# API 3 - text to speech / speech to text

- api que vai servir como fila / worker pra processar áudios em geral
- poderemos passar um texto para criar um áudio,

* definindo parâmetros de personalização
* retorna um link baixável que o servidor do whatsapp vai baixar localmente (temp) e enviar

- poderemos passar um arquivo de áudio via localstack (simular AWS S3), ele vai fazer a transcrição via whisper e retornar o texto
- pode ser tudo síncrono. Podemos pegar só a ideia de uma fila.

# Serviço do WhatsApp

- wwebjs de cria, o servidor node vai servir basicamente só pra enviar e receber mensagem
- podemos fazer o enviador de mensagem ser embutido em um webhook, que vai disparar a mensagem assim que receber  
  um sinal do backend "orquestrador" que pode ser a API 1 ou 3 ou outra
- ao receber a mensagem, ele só envia pro servidor via POST, que por si só vai fazer todo o processamento necessário
