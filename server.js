/**
 * 🏛️ PREFEITURA MUNICIPAL DE DUQUE DE CAXIAS — RJ
 * SIGEM — Sistema Integrado de Gestão de Endereços Municipais
 * Servidor de Produção em Node.js com SQLite Integrado
 */

require('dotenv').config();
const express = require('express');
const compression = require('compression');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const { DatabaseSync } = require('node:sqlite');

const app = express();
const PORT = process.env.PORT || 3015;
const DB_PATH = process.env.DB_PATH || path.join(__dirname, 'dados', 'enderecos_duque_de_caxias_v2.db');

// Inicialização do Banco de Dados SQLite
let db;
try {
  if (fs.existsSync(DB_PATH)) {
    db = new DatabaseSync(DB_PATH);
    console.log(`📦 [Banco de Dados] Conectado com sucesso ao SQLite: ${DB_PATH}`);
  } else {
    console.warn(`⚠️ [Aviso] Banco de dados não encontrado no caminho: ${DB_PATH}`);
  }
} catch (err) {
  console.error('❌ [Erro Banco de Dados]:', err.message);
}

// Middlewares Globais de Produção
app.set('trust proxy', 1); // Permite identificar IP e protocolo reais via Nginx Reverse Proxy
app.use(compression());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Prefixo base configurável (padrão: sigem)
const BASE_PATH = (process.env.BASE_PATH || 'sigem').replace(/^\/+|\/+$/g, '');

// Log básico de requisições
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (!req.path.startsWith('/dados') && !req.path.endsWith('.png') && !req.path.endsWith('.ico')) {
      const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
      console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} ${res.statusCode} (${clientIp}) - ${duration}ms`);
    }
  });
  next();
});

// ==========================================
// 🚀 ROTAS DA API RESTful (SIGEM API V2)
// ==========================================
const apiRouter = express.Router();

// 1. Healthcheck do Sistema
apiRouter.get('/health', (req, res) => {
  let dbStatus = 'disconnected';
  let totalEquipamentos = 0;
  
  if (db) {
    try {
      const row = db.prepare('SELECT count(*) as total FROM vw_equipamentos_consolidada').get();
      dbStatus = 'connected';
      totalEquipamentos = row.total;
    } catch (e) {
      dbStatus = `error: ${e.message}`;
    }
  }

  res.json({
    status: 'online',
    app: 'SIGEM — Duque de Caxias',
    versao: '2.0.0',
    uptime_segundos: Math.floor(process.uptime()),
    memoria: process.memoryUsage(),
    banco_de_dados: {
      status: dbStatus,
      caminho: DB_PATH,
      total_equipamentos: totalEquipamentos
    },
    timestamp: new Date().toISOString()
  });
});

// 2. Estatísticas e KPIs Gerais
apiRouter.get('/stats', (req, res) => {
  if (!db) return res.status(500).json({ error: 'Banco de dados não disponível' });
  try {
    const total = db.prepare('SELECT count(*) as total FROM vw_equipamentos_consolidada').get().total;
    const porDistrito = db.prepare(`
      SELECT distrito, count(*) as total 
      FROM vw_equipamentos_consolidada 
      GROUP BY distrito 
      ORDER BY distrito ASC
    `).all();
    const porCategoria = db.prepare(`
      SELECT categoria, count(*) as total 
      FROM vw_equipamentos_consolidada 
      GROUP BY categoria 
      ORDER BY total DESC
    `).all();
    const totalHubs = db.prepare('SELECT count(*) as total FROM hubs_predios').get().total;

    res.json({
      total_equipamentos: total,
      total_hubs: totalHubs,
      por_distrito: porDistrito,
      por_categoria: porCategoria
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 3. Lista de Equipamentos (com busca e filtros flexíveis)
apiRouter.get('/equipamentos', (req, res) => {
  if (!db) return res.status(500).json({ error: 'Banco de dados não disponível' });

  const { categoria, distrito, bairro, hub_id, q, limit, offset } = req.query;
  let sql = 'SELECT * FROM vw_equipamentos_consolidada WHERE 1=1';
  const params = [];

  if (categoria) {
    sql += ' AND categoria = ?';
    params.push(categoria);
  }
  if (distrito) {
    sql += ' AND distrito = ?';
    params.push(distrito);
  }
  if (bairro) {
    sql += ' AND bairro LIKE ?';
    params.push(`%${bairro}%`);
  }
  if (hub_id) {
    sql += ' AND hub_id = ?';
    params.push(Number(hub_id));
  }
  if (q) {
    sql += ' AND (nome LIKE ? OR sigla LIKE ? OR endereco LIKE ? OR bairro LIKE ? OR telefone LIKE ? OR email LIKE ?)';
    const term = `%${q}%`;
    params.push(term, term, term, term, term, term);
  }

  sql += ' ORDER BY id ASC';

  if (limit) {
    sql += ' LIMIT ?';
    params.push(Number(limit));
    if (offset) {
      sql += ' OFFSET ?';
      params.push(Number(offset));
    }
  }

  try {
    const rows = db.prepare(sql).all(...params);
    res.json({
      total_resultados: rows.length,
      data: rows
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 4. Detalhes de um Equipamento específico
apiRouter.get('/equipamentos/:id', (req, res) => {
  if (!db) return res.status(500).json({ error: 'Banco de dados não disponível' });
  const id = Number(req.params.id);

  try {
    const equip = db.prepare('SELECT * FROM vw_equipamentos_consolidada WHERE id = ?').get(id);
    if (!equip) {
      return res.status(404).json({ error: 'Equipamento não encontrado' });
    }

    // Telefones normalizados
    const telefones = db.prepare('SELECT tipo, ddd, numero, ramal, whatsapp, observacao FROM equipamento_telefones WHERE equipamento_id = ?').all(id);
    // E-mails normalizados
    const emails = db.prepare('SELECT tipo, email, observacao FROM equipamento_emails WHERE equipamento_id = ?').all(id);
    // Secretarias vinculadas
    const secretarias = db.prepare(`
      SELECT s.id, s.nome, s.sigla, es.tipo_relacao
      FROM equipamento_secretarias es
      JOIN secretarias s ON s.id = es.secretaria_id
      WHERE es.equipamento_id = ?
    `).all(id);
    // Serviços ofertados
    const servicos = db.prepare(`
      SELECT s.id, s.nome, s.categoria, s.publico_alvo, s.gratuito
      FROM equipamento_servicos es
      JOIN servicos s ON s.id = es.servico_id
      WHERE es.equipamento_id = ?
    `).all(id);

    res.json({
      ...equip,
      contatos: {
        telefones,
        emails
      },
      secretarias,
      servicos_ofertados: servicos
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 5. Lista de Distritos
apiRouter.get('/distritos', (req, res) => {
  if (!db) return res.status(500).json({ error: 'Banco de dados não disponível' });
  try {
    const distritos = db.prepare(`
      SELECT d.*, count(e.id) as total_equipamentos
      FROM distritos d
      LEFT JOIN bairros b ON b.distrito_id = d.numero
      LEFT JOIN enderecos ed ON ed.bairro_id = b.id
      LEFT JOIN equipamentos e ON e.endereco_id = ed.id
      GROUP BY d.numero
      ORDER BY d.numero ASC
    `).all();
    res.json(distritos);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 6. Lista de 90 Bairros
apiRouter.get('/bairros', (req, res) => {
  if (!db) return res.status(500).json({ error: 'Banco de dados não disponível' });
  const { distrito } = req.query;
  let sql = 'SELECT * FROM bairros';
  const params = [];

  if (distrito) {
    sql += ' WHERE distrito_id = ?';
    params.push(Number(distrito));
  }
  sql += ' ORDER BY distrito_id ASC, nome ASC';

  try {
    const bairros = db.prepare(sql).all(...params);
    res.json({
      total: bairros.length,
      data: bairros
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 7. Lista de Categorias
apiRouter.get('/categorias', (req, res) => {
  if (!db) return res.status(500).json({ error: 'Banco de dados não disponível' });
  try {
    const categorias = db.prepare('SELECT * FROM categorias ORDER BY nome ASC').all();
    res.json(categorias);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 8. Lista de Hubs Prediais / Complexos Administrativos
apiRouter.get('/hubs', (req, res) => {
  if (!db) return res.status(500).json({ error: 'Banco de dados não disponível' });
  try {
    const hubs = db.prepare(`
      SELECT h.*, count(e.id) as total_ocupantes
      FROM hubs_predios h
      LEFT JOIN equipamentos e ON e.hub_id = h.id
      GROUP BY h.id
      ORDER BY h.id ASC
    `).all();
    res.json(hubs);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==========================================
// 🔌 MONTAGEM DOS ROTEADORES DE API
// ==========================================
// Permite que a API responda em /api e também com prefixos do Nginx (/sigem/api, /enderecos/api)
app.use('/api', apiRouter);
if (BASE_PATH && BASE_PATH !== 'api') {
  app.use(`/${BASE_PATH}/api`, apiRouter);
}
app.use('/sigem/api', apiRouter);
app.use('/enderecos/api', apiRouter);

// ==========================================
// 🖥️ ROTAS DE INTERFACE WEB (FRONTEND)
// ==========================================
const serveIndex = (req, res) => res.sendFile(path.join(__dirname, 'index.html'));
const serveLogin = (req, res) => res.sendFile(path.join(__dirname, 'login.html'));
const serveGerenciador = (req, res) => res.sendFile(path.join(__dirname, 'gerenciador_enderecos.html'));

// Rota Principal (Painel Web Oficial)
const indexPaths = new Set(['/', '/index.html', '/sigem', '/sigem/', '/sigem/index.html', '/enderecos', '/enderecos/', '/enderecos/index.html']);
if (BASE_PATH) {
  indexPaths.add(`/${BASE_PATH}`);
  indexPaths.add(`/${BASE_PATH}/`);
  indexPaths.add(`/${BASE_PATH}/index.html`);
}
indexPaths.forEach(p => app.get(p, serveIndex));

// Rota de Login Administrativo
const loginPaths = new Set(['/login', '/login.html', '/sigem/login', '/sigem/login.html', '/enderecos/login', '/enderecos/login.html']);
if (BASE_PATH) {
  loginPaths.add(`/${BASE_PATH}/login`);
  loginPaths.add(`/${BASE_PATH}/login.html`);
}
loginPaths.forEach(p => app.get(p, serveLogin));

// Rota do Gerenciador de Endereços
const gerenciadorPaths = new Set(['/gerenciador', '/gerenciador.html', '/gerenciador_enderecos.html', '/sigem/gerenciador', '/enderecos/gerenciador']);
if (BASE_PATH) {
  gerenciadorPaths.add(`/${BASE_PATH}/gerenciador`);
}
gerenciadorPaths.forEach(p => app.get(p, serveGerenciador));

// Servir arquivos estáticos (dados, cadernos, imagens, css, js)
const staticHandler = express.static(__dirname, {
  maxAge: '1h',
  etag: true
});
app.use(staticHandler);
if (BASE_PATH) {
  app.use(`/${BASE_PATH}`, staticHandler);
}
app.use('/sigem', staticHandler);
app.use('/enderecos', staticHandler);

// Tratamento 404
app.use((req, res) => {
  res.status(404).json({
    error: 'Recurso não encontrado',
    path: req.path
  });
});

// Inicia o Servidor HTTP
const server = app.listen(PORT, () => {
  console.log('================================================================');
  console.log(`🏛️  SIGEM — PREFEITURA DE DUQUE DE CAXIAS [PRODUÇÃO ATIVA]`);
  console.log('================================================================');
  console.log(`🌐 Servidor Web & API rodando em: http://localhost:${PORT}`);
  console.log(`📊 Painel Web Principal:          http://localhost:${PORT}/`);
  console.log(`🔐 Login Administrativo:          http://localhost:${PORT}/login`);
  console.log(`📑 Gerenciador Institucional:      http://localhost:${PORT}/gerenciador`);
  console.log(`🩺 Health Check da API:           http://localhost:${PORT}/api/health`);
  console.log(`📍 Endpoint de Equipamentos:      http://localhost:${PORT}/api/equipamentos`);
  console.log('================================================================');
});

// Encerramento Gracioso (Graceful Shutdown)
process.on('SIGTERM', () => {
  console.log('🛑 [SIGTERM] Encerrando servidor graciosamente...');
  server.close(() => {
    if (db) db.close();
    console.log('✅ Servidor finalizado com segurança.');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('🛑 [SIGINT] Encerrando servidor graciosamente...');
  server.close(() => {
    if (db) db.close();
    console.log('✅ Servidor finalizado com segurança.');
    process.exit(0);
  });
});
