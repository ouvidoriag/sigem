# 🏛️ Prefeitura Municipal de Duque de Caxias — Guia de Endereços & Painel Oficial

Bem-vindo ao repositório unificado de **Endereços, Equipamentos Públicos e Estrutura Administrativa de Duque de Caxias / RJ**.

---

## 🚀 Como Executar em Produção

### 1. Inicialização Rápida com NPM:
```powershell
# Iniciar o servidor de produção
npm start

# Ou modo desenvolvimento com recarregamento automático
npm run dev
```
Acesse no seu navegador: 👉 **`http://localhost:3333`**

---

### 2. Execução Gerenciada com PM2 (Daemon / Background):
O projeto inclui suporte nativo ao PM2 com reinicialização automática e logs estruturados:
```powershell
# Iniciar serviço com PM2
npm run pm2:start

# Ver status dos processos
npm run pm2:status

# Ver logs em tempo real
npm run pm2:logs

# Reiniciar / Parar serviço
npm run pm2:restart
npm run pm2:stop
```

---

### 3. Rotas da API RESTful Integrada (SQLite V2):
- **Healthcheck:** `GET /api/health`
- **KPIs e Estatísticas:** `GET /api/stats`
- **Equipamentos (Filtro e Busca):** `GET /api/equipamentos?q=hospital&distrito=1&categoria=Saude`
- **Detalhes de Equipamento:** `GET /api/equipamentos/:id`
- **Distritos:** `GET /api/distritos`
- **90 Bairros Oficiais:** `GET /api/bairros`
- **Categorias:** `GET /api/categorias`
- **Hubs e Prédios Compartilhados:** `GET /api/hubs`

---

### 4. Acesso Direto às Interfaces Web:
- 🌐 **Painel Web Principal:** `http://localhost:3333/`
- 🔐 **Login Administrativo:** `http://localhost:3333/login`
- 📑 **Gerenciador Institucional:** `http://localhost:3333/gerenciador`


---

## 🗂️ Estrutura de Diretórios

```
enderecos/
├── index.html                       # Painel Web Oficial Interativo
├── gerenciador_enderecos.html       # Cópia de segurança institucional
├── 00_INDICE_GERAL.md               # Índice Geral Unificado de Navegação
├── README.md                        # Documentação do Repositório
│
├── cadernos/                        # Cadernos Temáticos por Setor
│   ├── 01_Governo_e_Secretarias/   # Sedes centrais, secretarias oficiais 2026 e órgãos
│   ├── 02_Saude/                   # Hospitais, UPAs, Policlínicas e UBSs por Distrito
│   ├── 03_Educacao/                # Sede SMEDC, Polos FUNDEC e Escolas por Distrito
│   ├── 04_Assistencia_Social_e_Cidadania/ # CRAS, CREAS, Conselhos Tutelares e Restaurantes
│   ├── 05_Seguranca_Defesa_Civil_e_Servicos/ # Guarda, Defesa Civil, Obras e SINE
│   └── 06_Subprefeituras_Bairros_e_Comunidades/ # Subprefeituras, 90 Bairros e Comunidades
│
├── dados/                           # Bases de Dados Oficiais Unificadas (JSON e CSV)
│   ├── todos_os_enderecos_duque_de_caxias.csv  # Planilha MESTRE com todos os 405 equipamentos
│   ├── todos_os_enderecos_duque_de_caxias.json # Base JSON MESTRE com todos os 405 equipamentos
│   └── por_setor/                   # Planilhas segmentadas (Secretarias, Saúde, Educação, FUNDEC, etc.)
│
├── cartas_de_servico/               # 24 Cartas de Serviços Oficiais em Markdown com índice navegável
└── scripts/                         # 6 scripts essenciais de manutenção e pasta de arquivo histórico
```
