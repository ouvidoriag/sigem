# 🏛️ Prefeitura Municipal de Duque de Caxias — Guia de Endereços & Painel Oficial

Bem-vindo ao repositório unificado de **Endereços, Equipamentos Públicos e Estrutura Administrativa de Duque de Caxias / RJ**.

---

## 🚀 Como Acessar e Usar

1. **Aplicação Web Interativa (Painel SaaS):**
   - Dê um duplo clique em **[`index.html`](./index.html)** para abrir no seu navegador.
   - Recursos:
     - 🔍 Busca instantânea em tempo real por nome, bairro, telefone ou e-mail.
     - 🏢 Filtros por categoria (Secretarias, Saúde Especializada, Saúde Básica, FUNDEC, Educação, Assistência Social e Segurança).
     - 🗺️ Mapa georreferenciado interativo com marcadores de equipamentos.
     - 📑 Tabela paginada completa com 405 equipamentos oficiais cadastrados.
     - 🏛️ Gestão de Hubs e Complexos Administrativos compartilhados.
   - *Nota:* O arquivo [`gerenciador_enderecos.html`](./gerenciador_enderecos.html) é mantido como espelho institucional idêntico.

2. **Índice Mestre e Cadernos Técnicos:**
   - Abra o **[`00_INDICE_GERAL.md`](./00_INDICE_GERAL.md)** para navegar por todos os documentos temáticos.

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
