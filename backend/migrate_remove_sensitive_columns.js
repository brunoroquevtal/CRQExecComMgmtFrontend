/**
 * Script de migração para remover colunas sensíveis do banco de dados
 * Remove: executor, telefone, localidade
 * 
 * Uso: node migrate_remove_sensitive_columns.js
 */
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { DB_PATH } = require('./config');
const fs = require('fs');

async function migrate() {
  console.log('🔄 Iniciando migração para remover colunas sensíveis...');
  
  // Fazer backup do banco antes de migrar
  const backupPath = `${DB_PATH}.backup.${Date.now()}`;
  if (fs.existsSync(DB_PATH)) {
    fs.copyFileSync(DB_PATH, backupPath);
    console.log(`✅ Backup criado: ${backupPath}`);
  }
  
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('❌ Erro ao conectar ao banco:', err);
        reject(err);
        return;
      }
      
      console.log('📊 Verificando estrutura atual...');
      
      // Verificar se as colunas sensíveis existem
      db.all("PRAGMA table_info(excel_data)", (err, columns) => {
        if (err) {
          console.error('❌ Erro ao verificar estrutura:', err);
          db.close();
          reject(err);
          return;
        }
        
        const columnNames = columns.map(col => col.name);
        const sensitiveColumns = ['executor', 'telefone', 'localidade'];
        const columnsToRemove = sensitiveColumns.filter(col => columnNames.includes(col));
        
        if (columnsToRemove.length === 0) {
          console.log('✅ Nenhuma coluna sensível encontrada. Banco já está atualizado.');
          db.close();
          resolve();
          return;
        }
        
        console.log(`📋 Colunas sensíveis encontradas: ${columnsToRemove.join(', ')}`);
        console.log('🔄 Criando nova tabela sem colunas sensíveis...');
        
        // Criar nova tabela sem colunas sensíveis
        db.serialize(() => {
          // Criar tabela temporária
          db.run(`
            CREATE TABLE excel_data_new (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              seq INTEGER,
              sequencia TEXT,
              atividade TEXT,
              grupo TEXT,
              inicio TEXT,
              fim TEXT,
              tempo REAL,
              file_name TEXT,
              data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
          `, (err) => {
            if (err) {
              console.error('❌ Erro ao criar nova tabela:', err);
              db.close();
              reject(err);
              return;
            }
            
            console.log('✅ Nova tabela criada');
            console.log('📦 Copiando dados (sem colunas sensíveis)...');
            
            // Copiar dados excluindo colunas sensíveis
            db.run(`
              INSERT INTO excel_data_new 
              (id, seq, sequencia, atividade, grupo, inicio, fim, tempo, file_name, data_importacao)
              SELECT 
                id, seq, sequencia, atividade, grupo, inicio, fim, tempo, file_name, data_importacao
              FROM excel_data
            `, (err) => {
              if (err) {
                console.error('❌ Erro ao copiar dados:', err);
                db.run('DROP TABLE excel_data_new', () => {
                  db.close();
                  reject(err);
                });
                return;
              }
              
              console.log('✅ Dados copiados');
              console.log('🗑️  Removendo tabela antiga...');
              
              // Remover tabela antiga
              db.run('DROP TABLE excel_data', (err) => {
                if (err) {
                  console.error('❌ Erro ao remover tabela antiga:', err);
                  db.close();
                  reject(err);
                  return;
                }
                
                console.log('✅ Tabela antiga removida');
                console.log('🔄 Renomeando nova tabela...');
                
                // Renomear nova tabela
                db.run('ALTER TABLE excel_data_new RENAME TO excel_data', (err) => {
                  if (err) {
                    console.error('❌ Erro ao renomear tabela:', err);
                    db.close();
                    reject(err);
                    return;
                  }
                  
                  console.log('✅ Tabela renomeada');
                  console.log('🔍 Recriando índices...');
                  
                  // Recriar índices
                  db.run(`
                    CREATE INDEX IF NOT EXISTS idx_excel_data_seq ON excel_data(seq, sequencia)
                  `, (err) => {
                    if (err) {
                      console.warn('⚠️  Aviso ao recriar índice:', err);
                    }
                    
                    console.log('✅ Migração concluída com sucesso!');
                    console.log(`💾 Backup salvo em: ${backupPath}`);
                    db.close();
                    resolve();
                  });
                });
              });
            });
          });
        });
      });
    });
  });
}

if (require.main === module) {
  migrate()
    .then(() => {
      console.log('\n✅ Migração finalizada!');
      process.exit(0);
    })
    .catch((err) => {
      console.error('\n❌ Erro na migração:', err);
      process.exit(1);
    });
}

module.exports = { migrate };
