# 📍 Passo a Passo dos Endereços de Duque de Caxias
## 10 Passos do que a gente fez e do que falta fazer

Guia direto ao ponto, focado exclusivamente no cadastro, conferência e publicação dos **449 endereços e equipamentos públicos** do município.

---

### 🟢 O QUE JÁ FIZEMOS

#### 1. Juntar todos os endereços espalhados
* Pegamos os endereços que estavam soltos em várias fontes: Diários Oficiais, postos de saúde (CNES), escolas (Auge SME), polos da FUNDEC, CRAS e no sistema da Ouvidoria (OrientaHub).
* Resultado: juntamos todos os locais públicos dos 4 distritos num catálogo só.

#### 2. Padronizar e corrigir os dados
* Arrumamos os CEPs para o formato certinho (sem traço ou traço padronizado).
* Padronizamos os nomes dos bairros oficiais (para ninguém cadastrar o mesmo bairro com 3 nomes diferentes).
* Corrigimos telefones úteis, e-mails de atendimento e tiramos dados pessoais/particulares (LGPD).

#### 3. Achar as coordenadas de cada prédio (Lat / Lon)
* Buscamos a latitude e longitude exata de cada um dos 449 locais para o pino cair no telhado certo (Rooftop), e não no meio da rua ou em outro município.

#### 4. Tirar a marca d'água do mapa (Troca da CARTO pela ESRI)
* Como a CARTO começou a cobrar chave e jogou aquela marca d'água cinza (*API KEY REQUIRED*) na tela, trocamos o mapa base para os servidores da **ESRI / ArcGIS**.
* Agora o mapa de ruas e o de satélite abrem limpinhos, leves e sem precisar de chave.

#### 5. Montar a planilha e o JSON mestre
* Geramos um arquivo CSV unificado (para abrir no Excel) e um JSON completo (`todos_os_enderecos_duque_de_caxias.json`).
* Esses arquivos são a fonte única de verdade que alimenta o sistema.

#### 6. Fazer a faxina geral no código
* O projeto estava com quase 60 arquivos e scripts de teste misturados.
* Guardamos 51 scripts velhos e temporários dentro de uma pasta de arquivo (`scripts/arquivo/`), tiramos arquivos soltos da raiz e deixamos o projeto leve, organizado e fácil de mexer.

---

### 🔵 O QUE VAMOS FAZER AGORA

#### 7. Abrir a plataforma e conferir ponto a ponto
* Abrir o `index.html` no navegador e navegar por secretaria e por distrito.
* Testar a busca e ver se o pino de cada equipamento está no lugar certinho no mapa.
* Se algum posto mudou de endereço ou foi reformado recentemente, arrastar o pino no mini-mapa para acertar a posição.

#### 8. Validar e autorizar os dados
* Dar uma checada nos telefones de contato e nos horários de funcionamento de cada local.
* Pegar o "de acordo" e a autorização final das secretarias e da Ouvidoria para confirmar que a lista está 100% aprovada para o público.

#### 9. Subir no servidor oficial (Colocar no Ar)
* Fazer o upload dos arquivos (`index.html`, `login.html`, a pasta `dados/` e o `logo.png`) para o servidor web da prefeitura.
* Configurar o link oficial (com HTTPS/cadeado seguro) para que qualquer pessoa ou setor possa acessar pelo navegador.

#### 10. Ligar o buscador por CEP e proximidade
* Deixar ativo o script de cálculo de distância (`scripts/localizador_por_cep.py`).
* Assim, quando o munícipe (ou a inteligência artificial) mandar um CEP, o sistema calcula na hora a distância e responde qual é o posto, hospital, escola ou CRAS mais perto da casa dele.
