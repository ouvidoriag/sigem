# 🚨 Guia & Prompt de Correção: Marca d'Água "API KEY REQUIRED" nos Mapas (CARTO)

Este documento contém o diagnóstico da recente quebra dos mapas da **CARTO** e um **prompt pronto para copiar e colar** para os desenvolvedores aplicarem nos seus respectivos projetos (ou enviarem para seus assistentes de IA).

---

## 📌 O que aconteceu?

A **CARTO** (antiga CartoDB) alterou sua política global e passou a **bloquear e inserir marcas d'água** (`API KEY REQUIRED carto.com/basemaps/apikey`) em todas as requisições diretas aos seus servidores de *tiles* (`basemaps.cartocdn.com/light_all/`, `dark_all/`, etc.) que não enviam uma chave de API paga/registrada.

---

## 📋 PROMPT PRONTO PARA ENVIAR AOS DEVS / ASSISTENTE DE IA

> **Como usar:** Copie o texto dentro da caixa abaixo e cole diretamente no chat do seu assistente de IA (Antigravity, Cursor, Copilot, ChatGPT) ou envie no grupo de desenvolvedores:

```markdown
Por favor, atualize o mapa (Leaflet/MapLibre/OpenLayers) deste projeto para remover a marca d'água "API KEY REQUIRED" da CARTO.

A CARTO começou a exigir chave de API paga/registrada nos servidores de tiles públicos (basemaps.cartocdn.com).

Substitua as camadas base da CARTO pelas camadas gratuitas, de alta performance e sem marca d'água da ESRI / ArcGIS (padrão utilizado no projeto oficial da Prefeitura) ou OpenStreetMap:

1. Mapa Claro / Vias (Street Map):
   - URL: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}'
   - Attribution: 'Tiles &copy; Esri &mdash; Prefeitura de Duque de Caxias'
   - maxZoom: 19

2. Satélite / Ortofoto (Satellite Imagery):
   - URL: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
   - Attribution: 'Tiles &copy; Esri'
   - maxZoom: 19

3. Rótulos e Nomes de Ruas sobre Satélite (Opcional - Reference Labels):
   - URL: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'

Certifique-se de procurar por ocorrências de 'basemaps.cartocdn.com' em todo o projeto (arquivos JS, HTML ou módulos de mapa) e atualizar os tileLayer correspondentes. Teste em seguida para garantir que o mapa carregue limpo.
```

---

## 💻 Como Corrigir Diretamente no Código (Antes vs Depois)

Se o desenvolvedor preferir alterar diretamente no código fonte, basta localizar onde o Leaflet inicializa o `L.tileLayer`:

### ❌ ANTES (Código que quebrou com a marca d'água):
```javascript
// Servidor CARTO antigo (Agora requer chave):
const light = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OSM &copy; CARTO',
  subdomains: 'abcd',
  maxZoom: 20
});

const dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OSM &copy; CARTO',
  subdomains: 'abcd',
  maxZoom: 20
});
```

---

###  DEPOIS (Opção 1 — Padrão Recomendado PMDC: ArcGIS / ESRI):
> **Vantagens:** 100% gratuito, sem marca d'água, carregamento ultrarrápido, excelente detalhamento cartográfico em Duque de Caxias e não precisa de cadastro nem chave.

```javascript
// Mapa de Ruas / Street Map:
const light = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Tiles &copy; Esri &mdash; Duque de Caxias',
  maxZoom: 19
});

// Satélite de Alta Resolução:
const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Tiles &copy; Esri',
  maxZoom: 19
});

// Nomes de vias para sobrepor no satélite:
const labels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 19
});
```

---

### 🌐 DEPOIS (Opção 2 — OpenStreetMap Standard):
> **Alternativa:** Servidor comunitário aberto do OSM.

```javascript
const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19
});
```

---

## 🔎 Dica para localizar nos projetos:
Para encontrar rapidamente onde está a chamada nos projetos, basta buscar no repositório por:
```bash
cartocdn
```
ou
```bash
basemaps.cartocdn.com
```
E substituir pela URL da ESRI acima.
