# 🛠️ Scripts Oficiais de Manutenção — Duque de Caxias / RJ

Este diretório contém apenas as **6 ferramentas ativas e essenciais** para manutenção, calibração e atualização do projeto.

---

## 📋 Lista de Ferramentas Ativas

| Script | Linguagem | Finalidade | Como Usar |
| :--- | :--- | :--- | :--- |
| **`sincronizar_html.js`** | Node.js | Atualiza o `index.html` e `gerenciador_enderecos.html` incorporando os dados mais recentes do JSON mestre. | `node scripts/sincronizar_html.js` |
| **`migrar_banco_v2.py`** | Python | Reconstrói o banco relacional SQLite (`enderecos_duque_de_caxias_v2.db`) e o dump SQL (`schema_e_dados_v2.sql`) a partir do JSON mestre. | `python scripts/migrar_banco_v2.py` |
| **`localizador_por_cep.py`** | Python | Motor de cálculo de proximidade e busca geográfica via CEP e fórmula de Haversine. | `python scripts/localizador_por_cep.py` |
| **`geocodificar_com_google.py`** | Python | Calibração e auditoria de coordenadas GPS de alta precisão via Google Geocoding API (ROOFTOP). | `python scripts/geocodificar_com_google.py --help` |
| **`calibrar_com_arcgis.py`** | Python | Validação e calibração de coordenadas geográficas via serviço ArcGIS / ESRI. | `python scripts/calibrar_com_arcgis.py` |
| **`gerar_doc_bairros_distritos.py`** | Python | Gera e atualiza automaticamente o documento `GUIA_COMPLETO_BAIRROS_E_DISTRITOS.md`. | `python scripts/gerar_doc_bairros_distritos.py` |

---

## 🗄️ Pasta `arquivo/`

A subpasta [`arquivo/`](./arquivo/) contém scripts históricos, rotinas de testes pontuais (`test_*.py`), pequenos scripts de diagnóstico (`inspecionar_*`) e relatórios intermediários gerados durante as etapas de construção inicial do banco de dados. Eles foram preservados apenas para fins de histórico e auditoria técnica.
