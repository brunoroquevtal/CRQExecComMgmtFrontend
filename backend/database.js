/**
 * Módulo para gerenciamento do banco de dados SQLite
 */
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { DB_PATH } = require('./config');

class DatabaseManager {
  constructor() {
    this.db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('Erro ao conectar ao banco de dados:', err);
      } else {
        this.createTables().then(() => {
          // Executar migrações após criar/verificar tabelas
          this.migrateTables().catch(err => {
            console.error('Erro ao executar migrações:', err);
          });
        }).catch(err => {
          console.error('Erro ao criar tabelas:', err);
        });
      }
    });
  }

  async createTables() {
    return new Promise((resolve, reject) => {
      // Criar tabela excel_data (sem dados sensíveis: executor, telefone, localidade)
      this.db.run(`
        CREATE TABLE IF NOT EXISTS excel_data (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          seq INTEGER,
          sequencia TEXT,
          atividade TEXT,
          grupo TEXT,
          inicio TEXT,
          fim TEXT,
          tempo REAL,
          file_name TEXT,
          is_rollback INTEGER DEFAULT 0,
          is_encerramento INTEGER DEFAULT 0,
          data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `, (err) => {
        if (err) {
          reject(err);
          return;
        }

        // Criar tabela activity_control
        this.db.run(`
          CREATE TABLE IF NOT EXISTS activity_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seq INTEGER,
            sequencia TEXT,
            excel_data_id INTEGER,
            status TEXT DEFAULT 'Planejado',
            horario_inicio_real TEXT,
            horario_fim_real TEXT,
            atraso_minutos INTEGER DEFAULT 0,
            observacoes TEXT,
            is_milestone INTEGER DEFAULT 0,
            predecessoras TEXT,
            arquivado INTEGER DEFAULT 0,
            is_rollback INTEGER DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(seq, sequencia, excel_data_id)
          )
        `, (err) => {
          if (err) {
            reject(err);
            return;
          }

          // Criar tabela para controlar estado de rollback por CRQ
          this.db.run(`
            CREATE TABLE IF NOT EXISTS crq_rollback_state (
              sequencia TEXT PRIMARY KEY,
              rollback_active INTEGER DEFAULT 0,
              data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
          `, (err) => {
            if (err) {
              reject(err);
              return;
            }

            // Criar índices
            this.db.run(`
              CREATE INDEX IF NOT EXISTS idx_excel_data_seq ON excel_data(seq, sequencia)
            `, (err) => {
              if (err) {
                reject(err);
                return;
              }

              this.db.run(`
                CREATE INDEX IF NOT EXISTS idx_activity_control_seq ON activity_control(seq, sequencia, excel_data_id)
              `, (err) => {
                if (err) {
                  reject(err);
                } else {
                  resolve();
                }
              });
            });
          });
        });
      });
    });
  }

  async migrateTables() {
    return new Promise((resolve, reject) => {
      // Verificar colunas existentes
      this.db.all("PRAGMA table_info(excel_data)", (err, columns) => {
        if (err) {
          console.warn('Erro ao verificar colunas da tabela excel_data:', err);
          resolve(); // Continuar mesmo se não conseguir verificar
          return;
        }

        const columnNames = columns.map(col => col.name.toLowerCase());
        const migrations = [];

        // Verificar e adicionar is_rollback se não existir
        if (!columnNames.includes('is_rollback')) {
          migrations.push(() => {
            return new Promise((resolveCol) => {
              this.db.run(`
                ALTER TABLE excel_data ADD COLUMN is_rollback INTEGER DEFAULT 0
              `, (err) => {
                if (err) {
                  console.warn('Aviso ao adicionar coluna is_rollback:', err.message);
                } else {
                  console.log('✅ Coluna is_rollback adicionada');
                }
                resolveCol();
              });
            });
          });
        }

        // Verificar e adicionar is_encerramento se não existir
        if (!columnNames.includes('is_encerramento')) {
          migrations.push(() => {
            return new Promise((resolveCol) => {
              this.db.run(`
                ALTER TABLE excel_data ADD COLUMN is_encerramento INTEGER DEFAULT 0
              `, (err) => {
                if (err) {
                  console.warn('Aviso ao adicionar coluna is_encerramento:', err.message);
                } else {
                  console.log('✅ Coluna is_encerramento adicionada');
                }
                resolveCol();
              });
            });
          });
        }

        // Verificar e adicionar file_name se não existir
        if (!columnNames.includes('file_name')) {
          migrations.push(() => {
            return new Promise((resolveCol) => {
              this.db.run(`
                ALTER TABLE excel_data ADD COLUMN file_name TEXT
              `, (err) => {
                if (err) {
                  console.warn('Aviso ao adicionar coluna file_name:', err.message);
                } else {
                  console.log('✅ Coluna file_name adicionada');
                }
                resolveCol();
              });
            });
          });
        }

        // Verificar e adicionar data_importacao se não existir
        if (!columnNames.includes('data_importacao')) {
          migrations.push(() => {
            return new Promise((resolveCol) => {
              this.db.run(`
                ALTER TABLE excel_data ADD COLUMN data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              `, (err) => {
                if (err) {
                  console.warn('Aviso ao adicionar coluna data_importacao:', err.message);
                } else {
                  console.log('✅ Coluna data_importacao adicionada');
                }
                resolveCol();
              });
            });
          });
        }

        // Verificar e adicionar ultima_sincronizacao se não existir
        if (!columnNames.includes('ultima_sincronizacao')) {
          migrations.push(() => {
            return new Promise((resolveCol) => {
              this.db.run(`
                ALTER TABLE excel_data ADD COLUMN ultima_sincronizacao TIMESTAMP
              `, (err) => {
                if (err) {
                  console.warn('Aviso ao adicionar coluna ultima_sincronizacao:', err.message);
                } else {
                  console.log('✅ Coluna ultima_sincronizacao adicionada');
                }
                resolveCol();
              });
            });
          });
        }

        // Executar todas as migrações em sequência
        if (migrations.length === 0) {
          console.log('✅ Todas as colunas já existem, nenhuma migração necessária');
          resolve();
        } else {
          console.log(`🔄 Executando ${migrations.length} migração(ões)...`);
          migrations.reduce((promise, migration) => {
            return promise.then(() => migration());
          }, Promise.resolve()).then(() => {
            console.log('✅ Migrações concluídas');
            resolve();
          }).catch((migrateErr) => {
            console.error('Erro ao executar migrações:', migrateErr);
            resolve(); // Continuar mesmo se migração falhar
          });
        }
      });
    });
  }

  getConnection() {
    return this.db;
  }

  async query(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  async get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }

  async run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  // Métodos para excel_data
  async saveExcelData(dataDict, fileName) {
    // Limpar dados antigos
    await this.run('DELETE FROM excel_data');

    let totalSaved = 0;

    for (const [sequencia, data] of Object.entries(dataDict)) {
      const df = data.dataframe;
      
      for (const row of df) {
        try {
          await this.run(`
            INSERT INTO excel_data 
            (seq, sequencia, atividade, grupo, inicio, fim, tempo, file_name, is_rollback, is_encerramento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          `, [
            row.Seq || null,
            sequencia,
            row.Atividade || '',
            row.Grupo || '',
            row.Inicio ? (row.Inicio.toISOString ? row.Inicio.toISOString() : row.Inicio) : null,
            row.Fim ? (row.Fim.toISOString ? row.Fim.toISOString() : row.Fim) : null,
            row.Tempo || 0,
            fileName,
            row.IsRollback ? 1 : 0,
            row.IsEncerramento ? 1 : 0
          ]);
          totalSaved++;
        } catch (error) {
          console.error(`Erro ao salvar registro: ${error.message}`);
        }
      }
    }

    return totalSaved;
  }

  async loadExcelData() {
    const rows = await this.query('SELECT * FROM excel_data ORDER BY sequencia, seq');

    // Agrupar por sequencia
    const dataDict = {};
    for (const row of rows) {
      if (!dataDict[row.sequencia]) {
        dataDict[row.sequencia] = {
          dataframe: [],
          sheet_name: row.sequencia
        };
      }
      dataDict[row.sequencia].dataframe.push(row);
    }

    return Object.keys(dataDict).length > 0 ? dataDict : null;
  }

  // Métodos para activity_control
  async getActivityControl(seq, sequencia, excelDataId = null) {
    if (excelDataId) {
      return await this.get(`
        SELECT * FROM activity_control 
        WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
      `, [seq, sequencia, excelDataId]);
    } else {
      return await this.get(`
        SELECT * FROM activity_control 
        WHERE seq = ? AND sequencia = ?
        ORDER BY excel_data_id DESC
        LIMIT 1
      `, [seq, sequencia]);
    }
  }

  async getAllActivitiesControl() {
    const rows = await this.query('SELECT * FROM activity_control');

    // Converter para formato de dicionário
    const controlData = {};
    for (const row of rows) {
      const key = row.excel_data_id 
        ? `${row.seq}_${row.sequencia}_${row.excel_data_id}`
        : `${row.seq}_${row.sequencia}`;
      controlData[key] = {
        status: row.status,
        horario_inicio_real: row.horario_inicio_real,
        horario_fim_real: row.horario_fim_real,
        atraso_minutos: row.atraso_minutos,
        observacoes: row.observacoes,
        is_milestone: row.is_milestone === 1,
        predecessoras: row.predecessoras || ''
      };
    }

    return controlData;
  }

  async saveActivityControl(data) {
    await this.run(`
      INSERT OR REPLACE INTO activity_control 
      (seq, sequencia, excel_data_id, status, horario_inicio_real, horario_fim_real, 
       atraso_minutos, observacoes, is_milestone, predecessoras, arquivado, is_rollback, data_atualizacao)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    `, [
      data.seq,
      data.sequencia,
      data.excel_data_id || null,
      data.status || 'Planejado',
      data.horario_inicio_real || null,
      data.horario_fim_real || null,
      data.atraso_minutos || 0,
      data.observacoes || '',
      data.is_milestone ? 1 : 0,
      data.predecessoras || '',
      data.arquivado ? 1 : 0,
      data.is_rollback ? 1 : 0
    ]);
  }

  async updateActivityControl(seq, sequencia, excelDataId, updates) {
    // Campos permitidos na tabela activity_control
    const allowedFields = [
      'status',
      'horario_inicio_real',
      'horario_fim_real',
      'atraso_minutos',
      'observacoes',
      'is_milestone',
      'predecessoras',
      'arquivado',
      'is_rollback'
    ];

    // Campos booleanos que devem ser convertidos para INTEGER (0 ou 1)
    const booleanFields = ['is_milestone', 'arquivado', 'is_rollback'];

    const fields = [];
    const values = [];

    for (const [key, value] of Object.entries(updates)) {
      // Filtrar apenas campos permitidos e que não são usados na cláusula WHERE
      if (allowedFields.includes(key)) {
        fields.push(`${key} = ?`);
        
        // Converter valores booleanos para inteiros (0 ou 1)
        // Também tratar strings "true"/"false" que podem vir do frontend
        if (booleanFields.includes(key)) {
          if (typeof value === 'boolean') {
            values.push(value ? 1 : 0);
          } else if (typeof value === 'string') {
            // Converter strings "true"/"false" para inteiros
            values.push(value.toLowerCase() === 'true' ? 1 : 0);
          } else if (value === null || value === undefined) {
            values.push(0);
          } else {
            // Tentar converter para número (1 ou 0)
            values.push(value ? 1 : 0);
          }
        } else {
          values.push(value);
        }
      }
    }

    if (fields.length === 0) {
      return false;
    }

    values.push('CURRENT_TIMESTAMP'); // data_atualizacao
    values.push(seq);
    values.push(sequencia);
    if (excelDataId) {
      values.push(excelDataId);
    }

    const sql = `
      UPDATE activity_control 
      SET ${fields.join(', ')}, data_atualizacao = ?
      WHERE seq = ? AND sequencia = ? ${excelDataId ? 'AND excel_data_id = ?' : ''}
    `;

    const result = await this.run(sql, values);
    return result.changes > 0;
  }

  // Criar nova atividade em excel_data
  async createExcelData(data) {
    const result = await this.run(`
      INSERT INTO excel_data 
      (seq, sequencia, atividade, grupo, inicio, fim, tempo, file_name, is_rollback, is_encerramento, ultima_sincronizacao)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      data.seq,
      data.sequencia,
      data.atividade || '',
      data.grupo || '',
      data.inicio || null,
      data.fim || null,
      data.tempo || 0,
      data.file_name || 'manual',
      data.is_rollback ? 1 : 0,
      data.is_encerramento ? 1 : 0,
      data.ultima_sincronizacao || null
    ]);
    return result.lastID;
  }

  // Atualizar atividade em excel_data
  async updateExcelData(id, updates) {
    // Campos permitidos na tabela excel_data
    const allowedFields = [
      'atividade',
      'grupo',
      'inicio',
      'fim',
      'tempo',
      'file_name',
      'is_rollback',
      'is_encerramento',
      'ultima_sincronizacao'
    ];

    const fields = [];
    const values = [];

    for (const [key, value] of Object.entries(updates)) {
      // Filtrar apenas campos permitidos e que não são usados na cláusula WHERE
      if (allowedFields.includes(key)) {
        fields.push(`${key} = ?`);
        values.push(value);
      }
    }

    if (fields.length === 0) {
      return false;
    }

    values.push(id);

    const sql = `UPDATE excel_data SET ${fields.join(', ')} WHERE id = ?`;
    const result = await this.run(sql, values);
    return result.changes > 0;
  }

  // Deletar atividade de excel_data
  async deleteExcelData(id) {
    const result = await this.run('DELETE FROM excel_data WHERE id = ?', [id]);
    return result.changes > 0;
  }

  // Deletar atividade de activity_control
  async deleteActivityControl(seq, sequencia, excelDataId) {
    let sql, params;
    if (excelDataId) {
      sql = 'DELETE FROM activity_control WHERE seq = ? AND sequencia = ? AND excel_data_id = ?';
      params = [seq, sequencia, excelDataId];
    } else {
      sql = 'DELETE FROM activity_control WHERE seq = ? AND sequencia = ? AND (excel_data_id IS NULL OR excel_data_id = 0)';
      params = [seq, sequencia];
    }
    const result = await this.run(sql, params);
    return result.changes > 0;
  }

  // Limpar todos os dados do banco
  async clearAllData() {
    return new Promise((resolve, reject) => {
      // Contar registros antes de deletar
      this.db.all('SELECT COUNT(*) as count FROM excel_data', [], (err, rows) => {
        if (err) {
          reject(err);
          return;
        }
        const excelCount = rows[0]?.count || 0;

        this.db.all('SELECT COUNT(*) as count FROM activity_control', [], (err2, rows2) => {
          if (err2) {
            reject(err2);
            return;
          }
          const controlCount = rows2[0]?.count || 0;

          // Deletar todos os dados
          this.db.run('DELETE FROM excel_data', (err3) => {
            if (err3) {
              reject(err3);
              return;
            }

            this.db.run('DELETE FROM activity_control', (err4) => {
              if (err4) {
                reject(err4);
                return;
              }

              // Deletar também da tabela crq_rollback_state
              this.db.run('DELETE FROM crq_rollback_state', (err5) => {
                if (err5) {
                  // Não é crítico se esta tabela não existir ou falhar
                  console.warn('Aviso ao limpar crq_rollback_state:', err5.message);
                }

                resolve({
                  excel_deleted: excelCount,
                  control_deleted: controlCount,
                  success: true
                });
              });
            });
          });
        });
      });
    });
  }

  // Obter excel_data por id
  async getExcelDataById(id) {
    return await this.get('SELECT * FROM excel_data WHERE id = ?', [id]);
  }

  async getExcelDataBySeq(seq, sequencia) {
    return await this.get('SELECT * FROM excel_data WHERE seq = ? AND sequencia = ?', [seq, sequencia]);
  }

  // Obter atividades não sincronizadas (para exclusão)
  async getUnsyncedActivities(syncTimestamp, sequencias) {
    if (!sequencias || sequencias.length === 0) {
      return [];
    }
    
    const placeholders = sequencias.map(() => '?').join(',');
    const sql = `
      SELECT * FROM excel_data 
      WHERE sequencia IN (${placeholders}) 
      AND (ultima_sincronizacao IS NULL OR ultima_sincronizacao < ?)
    `;
    
    const params = [...sequencias, syncTimestamp];
    return await this.query(sql, params);
  }

  // Métodos para controle de rollback por CRQ
  async getRollbackState(sequencia) {
    const result = await this.get(
      'SELECT * FROM crq_rollback_state WHERE sequencia = ?',
      [sequencia]
    );
    return result ? { ...result, rollback_active: result.rollback_active === 1 } : { sequencia, rollback_active: false };
  }

  async getAllRollbackStates() {
    const rows = await this.query('SELECT * FROM crq_rollback_state');
    const states = {};
    for (const row of rows) {
      states[row.sequencia] = {
        sequencia: row.sequencia,
        rollback_active: row.rollback_active === 1,
        data_atualizacao: row.data_atualizacao
      };
    }
    return states;
  }

  async setRollbackState(sequencia, rollbackActive) {
    await this.run(`
      INSERT OR REPLACE INTO crq_rollback_state 
      (sequencia, rollback_active, data_atualizacao)
      VALUES (?, ?, CURRENT_TIMESTAMP)
    `, [sequencia, rollbackActive ? 1 : 0]);
  }

  close() {
    return new Promise((resolve, reject) => {
      this.db.close((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }
}

module.exports = DatabaseManager;
