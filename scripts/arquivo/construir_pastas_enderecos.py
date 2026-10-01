import os
import re
import csv
import json
import ssl
import urllib.request
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_ENDERECOS = r"c:\Users\501379.PMDC\Desktop\enderecos"
PASTAS_DESTINO = os.path.join(BASE_ENDERECOS, "PASTAS_DE_ENDERECOS")

# Subpastas
DIR_01 = os.path.join(PASTAS_DESTINO, "01_Secretarias_e_Governo")
DIR_02 = os.path.join(PASTAS_DESTINO, "02_Saude")
DIR_03 = os.path.join(PASTAS_DESTINO, "03_Educacao")
DIR_04 = os.path.join(PASTAS_DESTINO, "04_Assistencia_Social_e_Cidadania")
DIR_05 = os.path.join(PASTAS_DESTINO, "05_Seguranca_Defesa_Civil_e_Servicos")
DIR_06 = os.path.join(PASTAS_DESTINO, "06_Subprefeituras_Bairros_e_Comunidades")
DIR_07 = os.path.join(PASTAS_DESTINO, "07_Bases_Consolidadas")

for d in [DIR_01, DIR_02, DIR_03, DIR_04, DIR_05, DIR_06, DIR_07]:
    os.makedirs(d, exist_ok=True)

# 1. Puxar dados da API unidade_especializada_m2
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = "https://transparencia.duquedecaxias.rj.gov.br/sincronia/apidados.rule?sys=LAI"

print("1. Baixando dados de Unidades Especializadas de Saúde (unidade_especializada_m2)...")
req = urllib.request.Request(
    url,
    data=json.dumps({"api": "unidade_especializada_m2", "ano": 2026}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
dados_especialidades = []
try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as res:
        d = json.loads(res.read().decode("utf-8"))
        if d.get("status") == "sucess":
            dados_especialidades = d.get("dados", [])
    print(f"   -> {len(dados_especialidades)} registros obtidos com sucesso!")
except Exception as e:
    print(f"   -> Erro ao consultar API especialidades: {e}")

# Ler arquivos base
def ler_arquivo(nome):
    caminho = os.path.join(BASE_ENDERECOS, nome)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

txt_01 = ler_arquivo("01_SECRETARIAS_GOVERNO_E_ORGAOS_ESPECIAIS.md")
txt_02 = ler_arquivo("02_GUIA_COMPLETO_SAUDE_DUQUE_DE_CAXIAS.md")
txt_03 = ler_arquivo("03_REDE_EDUCACAO_SMEDC_E_FUNDEC.md")
txt_04 = ler_arquivo("04_ASSISTENCIA_SOCIAL_SEGURANCA_E_CIDADANIA.md")
txt_05 = ler_arquivo("05_TERRITORIO_SUBPREFEITURAS_E_COMUNIDADES.md")

# Secretarias da API
caminho_sec_json = r"c:\Users\501379.PMDC\Desktop\Transparencia\secretarias\secretarias_completo.json"
secretarias_api = []
if os.path.exists(caminho_sec_json):
    with open(caminho_sec_json, "r", encoding="utf-8") as f:
        secretarias_api = json.load(f)

# Helper para extrair bloco de texto entre marcadores
def extrair_bloco(texto, inicio, fim=None):
    pos_i = texto.find(inicio)
    if pos_i == -1:
        return ""
    if fim:
        pos_f = texto.find(fim, pos_i + len(inicio))
        if pos_f == -1:
            return texto[pos_i:].strip()
        return texto[pos_i:pos_f].strip()
    return texto[pos_i:].strip()

# =====================================================================
# 1. SECRETARIAS E GOVERNO
# =====================================================================
print("\n2. Gerando 01_Secretarias_e_Governo...")

# 01_Sedes_Centrais_e_Gabinetes.md
md_sedes = """# 🏛️ Sedes Centrais e Polos Administrativos do Governo Municipal
> **Prefeitura Municipal de Duque de Caxias / RJ**
> *Mapeamento das sedes do Poder Executivo, Gabinetes e Polos Concentradores de Atendimento.*

---

## 1. Sedes Centrais do Poder Executivo

| Unidade / Prédio | Função Institucional | Endereço Completo | Bairro | Distrito | CEP | Telefones Oficiais |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Paço Municipal (Gabinete do Prefeito)** | Sede Administrativa Central do Município | Alameda Esmeralda, 206 | Jardim Primavera | 2º | 25.215-260 | (21) 2772-7200 |
| **Gabinete da Vice-Prefeita** | Gestão, Articulação e Políticas Públicas | Alameda Esmeralda, 206 | Jardim Primavera | 2º | 25.215-260 | (21) 2772-7200 |
| **Sede Histórica 25 de Agosto** | Atendimento Central, Jurídico e Cívico | Praça Governador Roberto Silveira, 31 | 25 de Agosto | 1º | 25.071-210 | (21) 2672-8889 |
| **Polo Administrativo Major Frazão** | Cultura, Trabalho, Criança, Transporte e SINE | Rua Major Frazão, 52 | 25 de Agosto | 1º | 25.071-210 | (21) 2772-7200 |
| **Complexo Central da Saúde** | Gestão Sanitária, Regulação e Vigilância | Alameda James Franco, 3 | Jardim Primavera | 2º | 25.215-260 | (21) 2773-6309 / 2773-6315 |
| **Complexo Central de Educação (SMEDC)** | Gestão da Rede Municipal de Ensino | Rua Pref. José Carlos Lacerda, 1.424 | 25 de Agosto | 1º | 25.071-120 | (21) 2671-6612 |
| **Polo de Desenvolvimento e Gestão** | Desenvolvimento Econômico, Gestão e Inclusão | Rua Marta de Souza Renha, 9 | Parque Santa Marta | 1º | 25.085-390 | (21) 92012-2310 |
| **Polo Urbanístico e Habitacional** | Habitação, Urbanismo e Proteção Animal | Alameda Bartolomeu Gusmão, 85 | Jardim Primavera | 2º | 25.215-320 | (21) 2783-6066 |
| **Sede Central de Assistência Social** | Assistência Social, Direitos Humanos e Cadastro Único | Av. Brigadeiro Lima e Silva, 1.618 | 25 de Agosto | 1º | 25.071-182 | (21) 2672-6659 / 2672-6650 |
| **Sede Operacional de Obras** | Obras Públicas, Conservação e Agricultura | Avenida Primavera, 78 | Jardim Primavera | 2º | 25.215-255 | obraspmdc@gmail.com |
| **Sede da Ouvidoria Geral do Município** | Atendimento ao Cidadão, Denúncias e Fala.BR | Alameda Esmeralda, 206 | Jardim Primavera | 2º | 25.215-260 | (21) 2652-3835 |
"""
with open(os.path.join(DIR_01, "01_Sedes_Centrais_e_Gabinetes.md"), "w", encoding="utf-8") as f:
    f.write(md_sedes)

# 02_Secretarias_Municipais_Oficiais_2026.md
linhas_sec_md = [
    "# 🏛️ Guia Oficial das 29 Secretarias e Órgãos Municipais — Duque de Caxias (2026)",
    "> **Fonte:** API REST Oficial da Transparência (`secretarias_m2` / 2026) com extração direta em UTF-8.",
    "",
    "| Nº | Órgão / Secretaria | Titular Responsável | Endereço Completo | Horário | Contatos (Tel / E-mail) | Carta de Serviços |",
    "| :-: | :--- | :--- | :--- | :---: | :--- | :---: |"
]
for i, s in enumerate(secretarias_api, 1):
    cod = s.get("SEC_Codigo")
    nome = s.get("SEC_NOME", "").strip()
    c1 = (s.get("SEC_CAMPO1") or "").strip()
    c2 = (s.get("SEC_CAMPO2") or "").strip()
    c3 = (s.get("SEC_CAMPO3") or "").strip()
    c4 = (s.get("SEC_CAMPO4") or "").strip()
    c5 = (s.get("SEC_CAMPO5") or "").strip()
    url_carta = s.get("URL_CARTA_SERVICO") or ""

    campos = [c1, c2, c3, c4, c5]
    endereco = ""
    horario = ""
    email = ""
    telefone = ""
    
    for c in campos:
        if not c or c == ".": continue
        if re.search(r'endere[çc]o\s*:', c, re.I) or re.search(r'Duque de Caxias', c, re.I) or re.search(r'CEP[:\s]', c, re.I):
            limpo = re.sub(r'^endere[çc]o\s*:\s*', '', c, flags=re.I).strip()
            if not endereco or len(limpo) > len(endereco):
                endereco = limpo
        if re.search(r'hor[áa]rio\s*(de\s*funcionamento)?\s*:', c, re.I):
            m_h = re.search(r'hor[áa]rio\s*(de\s*funcionamento)?\s*:\s*([^|]+)', c, re.I)
            if m_h: horario = m_h.group(2).strip()
        if '@' in c:
            m_e = re.findall(r'[\w\.-]+@[\w\.-]+', c)
            if m_e: email = " / ".join(m_e)
        if re.search(r'\(\d{2}\)', c):
            m_t = re.findall(r'\(\d{2}\)\s*[\d\- ]+', c)
            if m_t: telefone = " / ".join(t.strip(" -") for t in m_t)

    if "Comunit" in nome and not endereco:
        endereco = "Avenida Dr. Plinio Casado, s/n - Centro (Mergulhão), Duque de Caxias/RJ CEP 25.020-010"

    link_carta = f"[Acessar PDF]({url_carta})" if url_carta else "Não disponível"
    contato_str = f"Tel: {telefone}<br>Email: {email}" if telefone and email else (f"Tel: {telefone}" if telefone else f"Email: {email}")

    linhas_sec_md.append(f"| {i} | **{nome}** | {c1} | {endereco} | {horario} | {contato_str} | {link_carta} |")

with open(os.path.join(DIR_01, "02_Secretarias_Municipais_Oficiais_2026.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(linhas_sec_md))

# 03_Orgaos_Especiais_Autarquias_e_Fundacoes.md
md_orgaos = """# ⚖️ Órgãos Especiais, Autarquias e Fundações Municipais
> **Prefeitura Municipal de Duque de Caxias / RJ**

---

| Entidade / Órgão | Tipo | Endereço Completo | Bairro | CEP | Telefones / Contato |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Procuradoria Geral do Município (PGM)** | Advocacia Pública Municipal | Praça Roberto Silveira, 31 - 3º andar | 25 de Agosto | 25.071-210 | (21) 2672-8889 / gabineteadm.pgmdc@gmail.com |
| **Secretaria Municipal de Controle Interno (SECIN)** | Auditoria e Controle Interno | Alameda Esmeralda, 206 | Jardim Primavera | 25.215-260 | (21) 2772-7200 / secoin@duquedecaxias.rj.gov.br |
| **Ouvidoria Geral do Município (OGMDC)** | Transparência e Ouvidoria | Alameda Esmeralda, 206 | Jardim Primavera | 25.215-260 | (21) 2652-3835 / ouvidoria@duquedecaxias.rj.gov.br |
| **FUNDEC — Fundação de Apoio à Escola Técnica** | Fundação Pública de Qualificação | Rua General Dionísio, 381 | 25 de Agosto | 25.075-095 | (21) 2672-5650 / contato@fundec.rj.gov.br |
| **IPMDC — Instituto de Previdência dos Servidores** | Autarquia Previdenciária Municipal | Rua Marechal Floriano, 555 | 25 de Agosto | 25.075-025 | (21) 2673-8900 / contato@ipmdc.rj.gov.br |
"""
with open(os.path.join(DIR_01, "03_Orgaos_Especiais_Autarquias_e_Fundacoes.md"), "w", encoding="utf-8") as f:
    f.write(md_orgaos)


# =====================================================================
# 2. SAÚDE
# =====================================================================
print("\n3. Gerando 02_Saude...")

bloco_hosp = extrair_bloco(txt_02, "## 1. ATENÇÃO HOSPITALAR E ESPECIALIZADA", "## 2. ATENÇÃO PRIMÁRIA À SAÚDE")
linhas_hosp_todas = [l for l in bloco_hosp.split("\n") if l.startswith("|") and not l.startswith("| Nº") and not l.startswith("| :---:")]

hosp_lista = []
upas_lista = []
centros_lista = []

for l in linhas_hosp_todas:
    p = [x.strip() for x in l.split("|")]
    if len(p) >= 6:
        tipo = p[3].lower()
        nome = p[2].lower()
        if "hospital" in tipo or "hospital" in nome or "maternidade" in tipo or "maternidade" in nome:
            hosp_lista.append(l)
        elif "upa" in tipo or "upa" in nome or "uph" in tipo or "uph" in nome:
            upas_lista.append(l)
        else:
            centros_lista.append(l)

cab_hosp = "| Nº | Unidade / Hospital / UPA | Tipo | Endereço Completo | Bairro | Dist. | CEP | Telefone |\n| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |"

# 01_Hospitais_Maternidades_e_Emergencias.md
with open(os.path.join(DIR_02, "01_Hospitais_Maternidades_e_Emergencias.md"), "w", encoding="utf-8") as f:
    f.write("# 🏥 Hospitais, Maternidades e Grandes Emergências — Duque de Caxias\n\n" + cab_hosp + "\n" + "\n".join(hosp_lista))

# 02_UPAs_e_UPHs_24h.md
with open(os.path.join(DIR_02, "02_UPAs_e_UPHs_24h.md"), "w", encoding="utf-8") as f:
    f.write("# 🚑 UPAs e UPHs (Unidades Pré-Hospitalares 24 Horas) — Duque de Caxias\n\n" + cab_hosp + "\n" + "\n".join(upas_lista))

# 03_Policlinicas_e_Centros_Especializados.md
with open(os.path.join(DIR_02, "03_Policlinicas_e_Centros_Especializados.md"), "w", encoding="utf-8") as f:
    f.write("# 🩺 Policlínicas, CAPS e Centros de Especialidades — Duque de Caxias\n\n" + cab_hosp + "\n" + "\n".join(centros_lista))

# 04 a 07: UBS e ESF por distrito (apenas endereços, telefones, e-mails, CEP e coordenadas)
bloco_aps = extrair_bloco(txt_02, "## 2. ATENÇÃO PRIMÁRIA À SAÚDE", "## 3. PRINCIPAIS SERVIÇOS")
linhas_aps_todas = [l for l in bloco_aps.split("\n") if l.startswith("|") and not l.startswith("| Nº") and not l.startswith("| :---:")]

cab_aps = "| Nº | Unidade Básica / USF | CNES | Endereço Completo | Distrito | CEP | Coordenadas GPS (Lat, Lon) |\n| :---: | :--- | :---: | :--- | :---: | :---: | :--- |"

aps_d1 = []
aps_d2 = []
aps_d3 = []
aps_d4 = []

for l in linhas_aps_todas:
    p = [x.strip() for x in l.split("|")]
    if len(p) >= 6:
        dist_str = p[5]
        if "1º" in dist_str:
            aps_d1.append(l)
        elif "2º" in dist_str:
            aps_d2.append(l)
        elif "3º" in dist_str:
            aps_d3.append(l)
        elif "4º" in dist_str:
            aps_d4.append(l)

with open(os.path.join(DIR_02, "04_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_1.md"), "w", encoding="utf-8") as f:
    f.write("# 📍 Unidades Básicas de Saúde (UBS / USF) — 1º Distrito (Centro / Duque de Caxias)\n\n" + cab_aps + "\n" + "\n".join(aps_d1))

with open(os.path.join(DIR_02, "05_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_2.md"), "w", encoding="utf-8") as f:
    f.write("# 📍 Unidades Básicas de Saúde (UBS / USF) — 2º Distrito (Campos Elíseos)\n\n" + cab_aps + "\n" + "\n".join(aps_d2))

with open(os.path.join(DIR_02, "06_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_3.md"), "w", encoding="utf-8") as f:
    f.write("# 📍 Unidades Básicas de Saúde (UBS / USF) — 3º Distrito (Imbariê)\n\n" + cab_aps + "\n" + "\n".join(aps_d3))

with open(os.path.join(DIR_02, "07_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_4.md"), "w", encoding="utf-8") as f:
    f.write("# 📍 Unidades Básicas de Saúde (UBS / USF) — 4º Distrito (Xerém)\n\n" + cab_aps + "\n" + "\n".join(aps_d4))


md_sede_smedc = """# 🏫 Complexo Administrativo da Secretaria Municipal de Educação (SMEDC)
> **Prefeitura Municipal de Duque de Caxias / RJ**

---

| Unidade / Coordenação | Endereço Completo | Bairro | Distrito | CEP | Telefone / E-mail |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Sede Central SMEDC (Gabinete e Subsecretarias)** | Rua Pref. José Carlos Lacerda, 1.424 | 25 de Agosto | 1º | 25.071-120 | (21) 2671-6612 / assessoriadecomunicacao@smeduquedecaxias.rj.gov.br |
| **Coordenação Pedagógica e Matrículas** | Rua Pref. José Carlos Lacerda, 1.424 | 25 de Agosto | 1º | 25.071-120 | (21) 2671-6612 |
| **Central de Merenda e Logística Escolar** | Avenida Primavera, 78 | Jardim Primavera | 2º | 25.215-255 | (21) 2772-7200 |
| **Comissão de Seleção e PSS Educação** | Rua Pref. José Carlos Lacerda, 1.424 | 25 de Agosto | 1º | 25.071-120 | assessoriagabinete@smeduquedecaxias.rj.gov.br |
"""

md_sede_smasdh = """# 🤝 Sede da Secretaria Municipal de Assistência Social e Direitos Humanos (SMASDH)
> **Prefeitura Municipal de Duque de Caxias / RJ**

---

| Unidade / Prédio | Endereço Completo | Bairro | Distrito | CEP | Telefones / E-mails |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Sede Central SMASDH** | Av. Brigadeiro Lima e Silva, 1.618 | 25 de Agosto | 1º | 25.071-182 | (21) 2672-6659 / (21) 2672-6650 / gabinete.seasdih@duquedecaxias.rj.gov.br |
| **Central do Cadastro Único (CadÚnico / Bolsa Família)** | Av. Brigadeiro Lima e Silva, 1.618 | 25 de Agosto | 1º | 25.071-182 | (21) 2672-6659 |
| **Subsecretaria de Direitos Humanos** | Av. Brigadeiro Lima e Silva, 1.618 | 25 de Agosto | 1º | 25.071-182 | (21) 2672-6650 |
"""

md_obras = """# 🚜 Polos de Obras Públicas, Limpeza Urbana e Conservação (SMOAG)
> **Secretaria Municipal de Obras e Agricultura — Duque de Caxias / RJ**

---

| Unidade / Polo | Atribuição | Endereço Completo | Bairro | Distrito | Contato |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Sede Central SMOAG** | Gestão de Obras, Vias e Agricultura | Avenida Primavera, 78 | Jardim Primavera | 2º | obraspmdc@gmail.com |
| **Polo Operacional Centro (1º Dist.)** | Drenagem, Asfalto e Iluminação | Rua Dr. Manoel Reis, s/n | Centenário | 1º | (21) 2772-7200 |
| **Polo Operacional Campos Elíseos (2º Dist.)** | Manutenção Viária e Conservação | Av. Actura, s/n | Campos Elíseos | 2º | (21) 2772-7200 |
| **Polo Operacional Imbariê (3º Dist.)** | Maquinário Pesado e Vias Rurais | Av. Automóvel Clube, s/n | Imbariê | 3º | (21) 2772-7200 |
| **Polo Operacional Xerém (4º Dist.)** | Encostas, Rios e Drenagem | Estrada Rio D'Ouro, s/n | Xerém | 4º | (21) 2679-1837 |
| **Usina de Asfalto Municipal** | Produção e Recapeamento Asfáltico | Rodovia Washington Luiz, km 112 | Jardim Primavera | 2º | obraspmdc@gmail.com |
"""

md_trabalho = """# 💼 Postos de Trabalho, Emprego, Renda e SINE Municipal (SMTER)
> **Secretaria Municipal de Trabalho, Emprego e Renda — Duque de Caxias / RJ**

---

| Unidade / Posto | Serviços Oferecidos | Endereço Completo | Bairro | Distrito | CEP | Contatos |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Sede SMTER & Posto Central SINE** | Vagas de Emprego, Carteira de Trabalho e Seguro Desemprego | Rua Major Frazão, 52 | 25 de Agosto | 1º | 25.071-210 | smter.gabinete@duquedecaxias.rj.gov.br / sineduquedecaxias01@gmail.com |
| **Posto Avançado SINE — Shopping Center Caxias** | Intermediação de Mão de Obra e Balcão de Emprego | Rua Mariano Sendra dos Santos, s/n | Centro | 1º | 25.010-080 | (21) 2672-7200 |
| **Polo de Qualificação Profissional Santa Cruz** | Cursos Gratuitos e Inscrições no Balcão de Emprego | Av. Automóvel Clube, s/n | Santa Cruz da Serra | 3º | 25.260-000 | smter.gabinete@duquedecaxias.rj.gov.br |
"""

# =====================================================================
# 3. EDUCAÇÃO
# =====================================================================
print("\n4. Gerando 03_Educacao...")

with open(os.path.join(DIR_03, "01_Sede_SMEDC_e_Coordencoes.md"), "w", encoding="utf-8") as f:
    f.write(md_sede_smedc)

# Polos FUNDEC
bloco_fundec = extrair_bloco(txt_03, "### Quadro Oficial dos 35 Centros de Ensino, Polos e Postos Avançados da FUNDEC:", "## 2. SECRETARIA MUNICIPAL DE EDUCAÇÃO")
with open(os.path.join(DIR_03, "02_Polos_FUNDEC_Qualificacao_Tecnica.md"), "w", encoding="utf-8") as f:
    f.write("# 🎓 Polos e Centros de Qualificação Técnica da FUNDEC (35 Unidades)\n\n" + bloco_fundec)

# Escolas por Distrito
escolas_d1 = extrair_bloco(txt_03, "### 3.1 Escolas do 1º Distrito (73 Unidades)", "### 3.2 Escolas do 2º Distrito")
escolas_d2 = extrair_bloco(txt_03, "### 3.2 Escolas do 2º Distrito (66 Unidades)", "### 3.3 Escolas do 3º Distrito")
escolas_d3 = extrair_bloco(txt_03, "### 3.3 Escolas do 3º Distrito (37 Unidades)", "### 3.4 Escolas do 4º Distrito")
escolas_d4 = extrair_bloco(txt_03, "### 3.4 Escolas do 4º Distrito (25 Unidades)")

with open(os.path.join(DIR_03, "03_Escolas_Municipais_e_Creches_Distrito_1.md"), "w", encoding="utf-8") as f:
    f.write("# 📚 Escolas e Creches Municipais — 1º Distrito (73 Unidades)\n\n" + escolas_d1)

with open(os.path.join(DIR_03, "04_Escolas_Municipais_e_Creches_Distrito_2.md"), "w", encoding="utf-8") as f:
    f.write("# 📚 Escolas e Creches Municipais — 2º Distrito (66 Unidades)\n\n" + escolas_d2)

with open(os.path.join(DIR_03, "05_Escolas_Municipais_e_Creches_Distrito_3.md"), "w", encoding="utf-8") as f:
    f.write("# 📚 Escolas e Creches Municipais — 3º Distrito (37 Unidades)\n\n" + escolas_d3)

with open(os.path.join(DIR_03, "06_Escolas_Municipais_e_Creches_Distrito_4.md"), "w", encoding="utf-8") as f:
    f.write("# 📚 Escolas e Creches Municipais — 4º Distrito (25 Unidades)\n\n" + escolas_d4)


# =====================================================================
# 4. ASSISTÊNCIA SOCIAL E CIDADANIA
# =====================================================================
print("\n5. Gerando 04_Assistencia_Social_e_Cidadania...")

with open(os.path.join(DIR_04, "01_Sede_SMASDH_e_Coordenacoes.md"), "w", encoding="utf-8") as f:
    f.write(md_sede_smasdh)

# CRAS
bloco_cras = extrair_bloco(txt_04, "### 1.1 Quadro Oficial dos 13 Centros de Referência de Assistência Social (CRAS):", "### 1.2 Centros Especializados de Referência (CREAS):")
with open(os.path.join(DIR_04, "02_CRAS_Centros_de_Referencia_Assistencia_Social.md"), "w", encoding="utf-8") as f:
    f.write("# 🏡 CRAS — Centros de Referência de Assistência Social (13 Unidades)\n\n" + bloco_cras)

# CREAS e Pop
bloco_creas = extrair_bloco(txt_04, "### 1.2 Centros Especializados de Referência (CREAS):", "### 1.4 Conselhos Tutelares (Plantão 24 Horas):")
with open(os.path.join(DIR_04, "03_CREAS_Centro_Pop_e_Acolhimento.md"), "w", encoding="utf-8") as f:
    f.write("# 🛡️ CREAS, Centro Pop e Proteção Especial à Mulher e Idoso\n\n" + bloco_creas)

# Conselhos Tutelares
bloco_ct = extrair_bloco(txt_04, "### 1.4 Conselhos Tutelares (Plantão 24 Horas):", "### 1.5 Segurança Alimentar:")
with open(os.path.join(DIR_04, "04_Conselhos_Tutelares_1_2_3_4_Distritos.md"), "w", encoding="utf-8") as f:
    f.write("# ⚖️ Conselhos Tutelares por Distrito (Plantão 24h)\n\n" + bloco_ct)

# Restaurante do Povo
bloco_rest = extrair_bloco(txt_04, "### 1.5 Segurança Alimentar:", "## 2. SEGURANÇA PÚBLICA")
with open(os.path.join(DIR_04, "05_Restaurantes_do_Povo_e_Equipamentos_Comunitarios.md"), "w", encoding="utf-8") as f:
    f.write("# 🍽️ Restaurantes do Povo e Equipamentos de Segurança Alimentar\n\n" + bloco_rest)


# =====================================================================
# 5. SEGURANÇA, DEFESA CIVIL E SERVIÇOS
# =====================================================================
print("\n6. Gerando 05_Seguranca_Defesa_Civil_e_Servicos...")

bloco_seg = extrair_bloco(txt_04, "## 2. SEGURANÇA PÚBLICA, TRÂNSITO E DEFESA CIVIL")
with open(os.path.join(DIR_05, "01_Guarda_Municipal_e_Seguranca_Publica.md"), "w", encoding="utf-8") as f:
    f.write("# 🚔 Guarda Municipal e Segurança Pública\n\n" + bloco_seg)

# Defesa Civil detalhada
md_defesa = """# 🚨 Defesa Civil Municipal — Sede Operacional e Bases Distritais
> **Secretaria Municipal de Defesa Civil — Duque de Caxias / RJ**

---

| Unidade / Base | Função | Endereço Completo | Bairro | Distrito | Telefones de Emergência |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Sede Central da Defesa Civil (24h)** | Central de Monitoramento, Vistorias e Pronta-Resposta | Rua Silva Fernandes, 170 | Parque Duque | 1º | **Disque 199** / (21) 2699-4207 / 0800 023 0199 |
| **Base Avançada 2º Distrito (Campos Elíseos)** | Monitoramento Hidrológico e Resposta Rápida | Av. Actura, s/n | Campos Elíseos | 2º | (21) 2699-4207 |
| **Base Avançada 3º Distrito (Imbariê)** | Apoio Operacional e Alerta de Enchentes | Av. Automóvel Clube, s/n | Imbariê | 3º | (21) 2699-4207 |
| **Base Avançada 4º Distrito (Xerém)** | Monitoramento de Encostas e Serra de Petrópolis | Estrada Rio D'Ouro, s/n | Xerém | 4º | (21) 2699-4207 |
"""
with open(os.path.join(DIR_05, "02_Defesa_Civil_Sede_e_Bases_Distritais.md"), "w", encoding="utf-8") as f:
    f.write(md_defesa)

with open(os.path.join(DIR_05, "03_Polos_de_Obras_Limpeza_e_Conservacao.md"), "w", encoding="utf-8") as f:
    f.write(md_obras)

md_protecao_animal = """# 🐾 Proteção Animal e Hospital Municipal Veterinário
> **Secretaria Municipal de Proteção Animal (SMPA) — Duque de Caxias / RJ**

---

| Unidade / Serviço | Atendimento | Endereço Completo | Bairro | Distrito | Contato |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Hospital Municipal Veterinário** | Consultas, Cirurgias, Vacinação e Emergência | Estrada Rio d'Ouro, s/n | Xerém | 4º | smpa@duquedecaxias.rj.gov.br |
| **Sede Administrativa da SMPA** | Licenciamento, Adoção e Denúncias de Maus-tratos | Alameda Bartolomeu Gusmão, 85 | Jardim Primavera | 2º | smpa@duquedecaxias.rj.gov.br |
| **Base do Castramóvel Municipal** | Castrações gratuitas itinerantes por agendamento | Unidade Móvel Distrital | Itinerante | 1º a 4º | smpa@duquedecaxias.rj.gov.br |
"""
with open(os.path.join(DIR_05, "04_Protecao_Animal_e_Hospital_Veterinario.md"), "w", encoding="utf-8") as f:
    f.write(md_protecao_animal)

with open(os.path.join(DIR_05, "05_Postos_de_Trabalho_e_SINE.md"), "w", encoding="utf-8") as f:
    f.write(md_trabalho)


# =====================================================================
# 6. SUBPREFEITURAS, BAIRROS E COMUNIDADES
# =====================================================================
print("\n7. Gerando 06_Subprefeituras_Bairros_e_Comunidades...")

bloco_sub = extrair_bloco(txt_05, "## 1. SUBPREFEITURAS E ADMINISTRAÇÕES REGIONAIS", "## 2. RELAÇÃO OFICIAL DE BAIRROS")
with open(os.path.join(DIR_06, "01_Subprefeituras_Distritais_e_Atendimento_Regional.md"), "w", encoding="utf-8") as f:
    f.write("# 🏛️ Subprefeituras Distritais e Atendimento Regional\n\n" + bloco_sub)

bloco_bairros = extrair_bloco(txt_05, "## 2. RELAÇÃO OFICIAL DE BAIRROS POR DISTRITO", "## 3. CARTOGRAFIA SOCIAL")
with open(os.path.join(DIR_06, "02_Guia_Oficial_dos_90_Bairros_por_Distrito.md"), "w", encoding="utf-8") as f:
    f.write("# 🗺️ Guia Oficial dos 90 Bairros de Duque de Caxias por Distrito\n\n" + bloco_bairros)

bloco_com = extrair_bloco(txt_05, "## 3. CARTOGRAFIA SOCIAL: 103 COMUNIDADES OFICIAIS", "## 4. PATRIMÔNIO CULTURAL")
with open(os.path.join(DIR_06, "03_Comunidades_e_Localidades_Georreferenciadas.md"), "w", encoding="utf-8") as f:
    f.write("# 📍 103 Comunidades e Favelas Oficiais Mapeadas com Coordenadas GPS (IBGE)\n\n" + bloco_com)


# =====================================================================
# 7. BASES CONSOLIDADAS (MASTER CSV & JSON)
# =====================================================================
print("\n8. Consolidando base completa de endereços em CSV e JSON...")

mestre_lista = []

# 1. Secretarias
for s in secretarias_api:
    nome = s.get("SEC_NOME", "").strip()
    c1 = s.get("SEC_CAMPO1") or ""
    c2 = s.get("SEC_CAMPO2") or ""
    c4 = s.get("SEC_CAMPO4") or ""
    c5 = s.get("SEC_CAMPO5") or ""
    
    end = ""
    for c in [c2, s.get("SEC_CAMPO3"), c4, c5]:
        if c and (re.search(r'endere[çc]o\s*:', str(c), re.I) or re.search(r'Duque de Caxias', str(c), re.I) or re.search(r'CEP', str(c), re.I)):
            limpo = re.sub(r'^endere[çc]o\s*:\s*', '', str(c), flags=re.I).strip()
            if not end or len(limpo) > len(end): end = limpo
    if "Comunit" in nome and not end:
        end = "Avenida Dr. Plinio Casado, s/n - Centro (Mergulhão), Duque de Caxias/RJ CEP 25.020-010"

    mestre_lista.append({
        "Categoria": "Governo Central",
        "Subcategoria": "Secretaria / Órgão Municipal",
        "Nome_Equipamento": nome,
        "Endereco_Completo": end,
        "Bairro": "Jardim Primavera" if "Primavera" in end else ("25 de Agosto" if "Agosto" in end else ("Centro" if "Centro" in end else "")),
        "Distrito": "2º Distrito" if "Primavera" in end else ("1º Distrito" if "Agosto" in end or "Centro" in end else ""),
        "Municipio": "Duque de Caxias",
        "UF": "RJ",
        "Telefone": str(c5) if re.search(r'\(\d{2}\)', str(c5)) else "",
        "Email": str(c4) if '@' in str(c4) else ""
    })

# 2. Saúde (Hospitais, UPAs, Centros)
for l in linhas_hosp_todas:
    p = [x.strip() for x in l.split("|")]
    if len(p) >= 8:
        mestre_lista.append({
            "Categoria": "Saúde",
            "Subcategoria": p[3],
            "Nome_Equipamento": re.sub(r'[*_]', '', p[2]),
            "Endereco_Completo": p[4],
            "Bairro": p[5],
            "Distrito": p[6],
            "Municipio": "Duque de Caxias",
            "UF": "RJ",
            "Telefone": p[8] if len(p) > 8 else "",
            "Email": ""
        })

# 3. Saúde (UBS / USF)
for l in linhas_aps_todas:
    p = [x.strip() for x in l.split("|")]
    if len(p) >= 7:
        mestre_lista.append({
            "Categoria": "Saúde",
            "Subcategoria": "Atenção Básica (USF / UBS)",
            "Nome_Equipamento": re.sub(r'[*_]', '', p[2]),
            "Endereco_Completo": p[4],
            "Bairro": "",
            "Distrito": p[5],
            "Municipio": "Duque de Caxias",
            "UF": "RJ",
            "Telefone": "",
            "Email": ""
        })

# Salvar JSON consolidado
with open(os.path.join(DIR_07, "TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.json"), "w", encoding="utf-8") as f:
    json.dump(mestre_lista, f, ensure_ascii=False, indent=2)

# Salvar CSV consolidado
if mestre_lista:
    with open(os.path.join(DIR_07, "TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.csv"), "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(mestre_lista[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(mestre_lista)

print(f"   -> {len(mestre_lista)} registros catalogados nas bases consolidadas!")


md_indice_mestre = """# 🏛️ Guia Geral de Endereços Oficiais — Município de Duque de Caxias / RJ
## Sistema Integrado de Navegação por Pastas e Módulos Temáticos
> **Base de Inteligência Territorial, Administrativa e Operacional**  
> *Consolidada em Setembro de 2026 a partir do Portal da Transparência, Diários Oficiais, Secretarias, Redes de Saúde, Educação, Assistência e Cartografia Municipal.*

---

## 🗂️ Navegação Rápida por Pastas

### 📁 [01 — Secretarias e Governo](./01_Secretarias_e_Governo/)
* 🏢 **[01_Sedes_Centrais_e_Gabinetes.md](./01_Secretarias_e_Governo/01_Sedes_Centrais_e_Gabinetes.md)** — Paço Municipal, Gabinete do Prefeito, Vice, Sede Histórica 25 de Agosto e Polos Concentradores.
* 🏛️ **[02_Secretarias_Municipais_Oficiais_2026.md](./01_Secretarias_e_Governo/02_Secretarias_Municipais_Oficiais_2026.md)** — Tabela das 29 Secretarias com titular, horário, telefones, e-mails e link da Carta de Serviços.
* ⚖️ **[03_Orgaos_Especiais_Autarquias_e_Fundacoes.md](./01_Secretarias_e_Governo/03_Orgaos_Especiais_Autarquias_e_Fundacoes.md)** — PGM, Ouvidoria Geral, Controle Interno, FUNDEC e IPMDC.

---

### 📁 [02 — Saúde](./02_Saude/)
* 🏥 **[01_Hospitais_Maternidades_e_Emergencias.md](./02_Saude/01_Hospitais_Maternidades_e_Emergencias.md)** — Hospital Moacyr do Carmo, Adão Pereira Nunes, São José Coração, Hospital do Olho e Infantis.
* 🚑 **[02_UPAs_e_UPHs_24h.md](./02_Saude/02_UPAs_e_UPHs_24h.md)** — Rede Pré-Hospitalar 24h: Xerém, Saracuruna, Imbariê, Campos Elíseos, Pilar, Equitativa e UPAs.
* 🩺 **[03_Policlinicas_e_Centros_Especializados.md](./02_Saude/03_Policlinicas_e_Centros_Especializados.md)** — CRAESM (Mulher), CER II, Policlínica Municipal e Rede CAPS (Leslie Sanford, AD, Infanto-Juvenil).
* 📍 **[04_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_1.md](./02_Saude/04_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_1.md)** — Postos de Saúde da Família do 1º Distrito (Centro).
* 📍 **[05_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_2.md](./02_Saude/05_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_2.md)** — Postos de Saúde da Família do 2º Distrito (Campos Elíseos).
* 📍 **[06_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_3.md](./02_Saude/06_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_3.md)** — Postos de Saúde da Família do 3º Distrito (Imbariê).
* 📍 **[07_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_4.md](./02_Saude/07_Unidades_Basicas_de_Saude_UBS_e_ESF_Distrito_4.md)** — Postos de Saúde da Família do 4º Distrito (Xerém).

---

### 📁 [03 — Educação](./03_Educacao/)
* 🏫 **[01_Sede_SMEDC_e_Coordencoes.md](./03_Educacao/01_Sede_SMEDC_e_Coordencoes.md)** — Sede Central da Educação, coordenações pedagógicas e de merenda.
* 🎓 **[02_Polos_FUNDEC_Qualificacao_Tecnica.md](./03_Educacao/02_Polos_FUNDEC_Qualificacao_Tecnica.md)** — Os 35 Polos de cursos técnicos gratuitos e profissionalizantes da FUNDEC.
* 📚 **[03_Escolas_Municipais_e_Creches_Distrito_1.md](./03_Educacao/03_Escolas_Municipais_e_Creches_Distrito_1.md)** — Escolas Municipais do 1º Distrito (Centro).
* 📚 **[04_Escolas_Municipais_e_Creches_Distrito_2.md](./03_Educacao/04_Escolas_Municipais_e_Creches_Distrito_2.md)** — Escolas Municipais do 2º Distrito (Campos Elíseos).
* 📚 **[05_Escolas_Municipais_e_Creches_Distrito_3.md](./03_Educacao/05_Escolas_Municipais_e_Creches_Distrito_3.md)** — Escolas Municipais do 3º Distrito (Imbariê).
* 📚 **[06_Escolas_Municipais_e_Creches_Distrito_4.md](./03_Educacao/06_Escolas_Municipais_e_Creches_Distrito_4.md)** — Escolas Municipais do 4º Distrito (Xerém).

---

### 📁 [04 — Assistência Social e Cidadania](./04_Assistencia_Social_e_Cidadania/)
* 🤝 **[01_Sede_SMASDH_e_Coordenacoes.md](./04_Assistencia_Social_e_Cidadania/01_Sede_SMASDH_e_Coordenacoes.md)** — Sede Central da Assistência Social, Direitos Humanos e CadÚnico.
* 🏡 **[02_CRAS_Centros_de_Referencia_Assistencia_Social.md](./04_Assistencia_Social_e_Cidadania/02_CRAS_Centros_de_Referencia_Assistencia_Social.md)** — Todos os CRAS com áreas de abrangência e bairros.
* 🛡️ **[03_CREAS_Centro_Pop_e_Acolhimento.md](./04_Assistencia_Social_e_Cidadania/03_CREAS_Centro_Pop_e_Acolhimento.md)** — CREAS Centro, CREAS 2º/3º Distrito, Centro Pop e Abrigos.
* ⚖️ **[04_Conselhos_Tutelares_1_2_3_4_Distritos.md](./04_Assistencia_Social_e_Cidadania/04_Conselhos_Tutelares_1_2_3_4_Distritos.md)** — Conselhos Tutelares dos 4 Distritos municipais.
* 🍽️ **[05_Restaurantes_do_Povo_e_Equipamentos_Comunitarios.md](./04_Assistencia_Social_e_Cidadania/05_Restaurantes_do_Povo_e_Equipamentos_Comunitarios.md)** — Restaurantes do Povo e Casa da Mulher Caxiense.

---

### 📁 [05 — Segurança, Defesa Civil e Serviços](./05_Seguranca_Defesa_Civil_e_Servicos/)
* 🚔 **[01_Guarda_Municipal_e_Seguranca_Publica.md](./05_Seguranca_Defesa_Civil_e_Servicos/01_Guarda_Municipal_e_Seguranca_Publica.md)** — Comando Geral da Guarda, Inspetorias e Central 153.
* 🚨 **[02_Defesa_Civil_Sede_e_Bases_Distritais.md](./05_Seguranca_Defesa_Civil_e_Servicos/02_Defesa_Civil_Sede_e_Bases_Distritais.md)** — Sede Operacional 24h, telefones de emergência 199 e sirenes.
* 🚜 **[03_Polos_de_Obras_Limpeza_e_Conservacao.md](./05_Seguranca_Defesa_Civil_e_Servicos/03_Polos_de_Obras_Limpeza_e_Conservacao.md)** — Polos Distritais de conservação viária, drenagem e usina de asfalto.
* 🐾 **[04_Protecao_Animal_e_Hospital_Veterinario.md](./05_Seguranca_Defesa_Civil_e_Servicos/04_Protecao_Animal_e_Hospital_Veterinario.md)** — Hospital Municipal Veterinário e serviços de castração.
* 💼 **[05_Postos_de_Trabalho_e_SINE.md](./05_Seguranca_Defesa_Civil_e_Servicos/05_Postos_de_Trabalho_e_SINE.md)** — Balcão de Emprego, SINE e Seguro Desemprego.

---

### 📁 [06 — Subprefeituras, Bairros e Comunidades](./06_Subprefeituras_Bairros_e_Comunidades/)
* 🏛️ **[01_Subprefeituras_Distritais_e_Atendimento_Regional.md](./06_Subprefeituras_Bairros_e_Comunidades/01_Subprefeituras_Distritais_e_Atendimento_Regional.md)** — Subprefeituras dos 4 distritos municipais.
* 🗺️ **[02_Guia_Oficial_dos_90_Bairros_por_Distrito.md](./06_Subprefeituras_Bairros_e_Comunidades/02_Guia_Oficial_dos_90_Bairros_por_Distrito.md)** — Relação completa de todos os bairros oficiais de Duque de Caxias.
* 📍 **[03_Comunidades_e_Localidades_Georreferenciadas.md](./06_Subprefeituras_Bairros_e_Comunidades/03_Comunidades_e_Localidades_Georreferenciadas.md)** — 103 Comunidades e Favelas com coordenadas geográficas GPS.

---

### 📁 [07 — Bases Consolidadas (Planilhas e Dados Integrados)](./07_Bases_Consolidadas/)
* 📊 **[TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.csv](./07_Bases_Consolidadas/TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.csv)** — Planilha única consolidada em formato Excel (`UTF-8-sig` com separador `;`).
* 📦 **[TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.json](./07_Bases_Consolidadas/TODOS_OS_ENDERECOS_DUQUE_DE_CAXIAS.json)** — Arquivo JSON mestre com a base de dados completa.
"""

with open(os.path.join(PASTAS_DESTINO, "00_INDICE_MESTRE_DE_ENDERECOS.md"), "w", encoding="utf-8") as f:
    f.write(md_indice_mestre)

with open(os.path.join(BASE_ENDERECOS, "00_INDICE_MESTRE_DE_ENDERECOS.md"), "w", encoding="utf-8") as f:
    f.write(md_indice_mestre.replace("./", "./PASTAS_DE_ENDERECOS/"))

print("\n=======================================================")
print("[SUCESSO TOTAL] Estrutura completa de endereços gerada!")
print(f"Caminho: {PASTAS_DESTINO}")
print("=======================================================")
