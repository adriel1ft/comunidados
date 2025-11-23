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

## API 1.2 - Documentação sobre a camara dos deputados e e-cidadão

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

## API 1.3 - Dados abertos da câmara dos deputados

- api para servir os dados abertos da camara dos deputados,
- fazer por mcp e fazer uma estruturação inicial a partir do swagger
- https://dadosabertos.camara.leg.br/swagger/api.html?tab=api
- Pode ser uma extensão do mcp que já existe / API 1

# Homepage do projeto

- trazer as principais informações do projeto e ter um call to action
- já implementado

# API 2 - text to speech / speech to text

- api que vai servir como fila / worker pra processar áudios em geral
- poderemos passar um texto para criar um áudio,

* definindo parâmetros de personalização
* retorna um link baixável que o servidor do whatsapp vai baixar localmente (temp) e enviar

- poderemos passar um arquivo de áudio via localstack (simular AWS S3), ele vai fazer a transcrição via whisper e retornar o texto
- pode ser tudo síncrono. Podemos pegar só a ideia de uma fila.

# Serviço do WhatsApp

- wwebjs de cria, o servidor node vai servir basicamente só pra enviar e receber mensagem
- podemos fazer o enviador de mensagem ser embutido em um webhook, que vai disparar a mensagem assim que receber um sinal do backend "orquestrador"
- ao receber a mensagem, ele só envia pro servidor via POST, que por si só vai fazer todo o processamento necessário

# API 3 - Agentes que geram mensagens do WhatsApp

- o orquestrador irá pedir pra certos agentes expostos gerarem outputs com base nas entradas do usuário
- ou pode ser um agente que irá chamar outros agentes hierarquicamente com base na classificação da mensagem
- pode fazer pesquisas no google, mas vamos focar nas fontes diretas e oficiais
- é importante ter um texto auxiliar em casos de que faremos uma transcrição, para enviar junto
- também vai decidir se o usuário deve receber a resposta em áudio

* caso sim, enviar texto + texto auxiliar, fazendo com que o orquestrador dispare duas mensagens
* caso não, enviar apenas texto
* a decisão é feita através de duas formas: 1. inferência pela mensagem do usuário (se ele mandou um áudio primeiro), ou 2. se ele explicitou que queria a resposta em áudio
* esse envio de texto auxiliar / sinalização de mensagem via áudio é importante pro orquestrador decidir qual será o formato das próximas mensagens

# API orquestradora de mensagem

- que recebe e envia as mensagens por session id
- a ideia do session id aqui é que seja uma janela de tempo que o usuário fala sobre um determinado
  contexto
- estilo messagequeue (?)
- ele vai agrupar mensagens enviadas em um curto período de tempo, fazendo com que seja apenas uma mensagem
- ele deve ter acesso ao histórico de mensagens daquela session (?) e passar para a LLM (?)
- deve fazer um gerenciamento de usuários e suas preferências de comunicação no quesito áudio/texto
- tratamento de áudio: vai receber um {data: "..."} em base64, salvar como arquivo local temp e enviar para a API 2
- deve ter um MCP integrado para gerenciamento de usuários
* pegar cadastro do usuário (nome, idade)
- vai requerer um banco de dados simples (mongodb) em dockerfile ou .sh

## Fluxo

- caso a mensagem seja áudio, transcrever para texto na API 2
- irá fazer a chamada para o agente na API 3, que vai gerar um resultado textual
- caso o usuário prefira áudio
  (ficou explícito/implícito na mensagem (API 3 gerenciaria isso)) ou
  é uma preferência do usuário cadastrado
  o orquestrador vai fazer a chamada pra API 2 de text to speech
  e pegar o url de resposta do áudio
- enviar via POST webhook pro servidor do whatsapp `/send-message`

## Cadastro do Usuário

- Precisamos agrupar os tópicos de interesse do usuário 
  ou decidir com base em regras de inferência simples
  ou para o mvp decidir uma entre 3 aleatoriamente
- precisamos coletar informações de 
* identificação (nome, idade) 
* localização (bairro, cidade)
- tudo isso é feito a partir da primeira mensagem do usuário
* caso seja primeira mensagem / não tem cadastro,
  * pedimos pra pessoa se identificar passando os parâmetros que dizemos
  * podemos decidir aí também qual categoria a pessoa se encaixa
  * pra simplificar, escolhemos os assuntos disponíveis na camara dos deputados


orquestrador
- agrupar mensagens por janela de tempo
- gerenciar session id (quais sessões estão ativas no momento) com o mongo
- gerenciar informações dos usuários
- if/else de processamento de áudio
- mcp de cadastro do usuário