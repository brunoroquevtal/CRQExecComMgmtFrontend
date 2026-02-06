"""
Módulo para gerenciamento do banco de dados SQLite
"""
import sqlite3
import os
from datetime import datetime
from config import DB_PATH


class DatabaseManager:
    """Gerenciador do banco de dados SQLite"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
    
    def get_connection(self):
        """Retorna conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa o banco de dados e cria tabelas se não existirem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar se a tabela já existe e qual constraint ela tem
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='activity_control'")
        existing_table = cursor.fetchone()
        
        # Se a tabela existe e tem constraint antiga, vamos recriá-la
        if existing_table:
            old_sql = existing_table[0]
            # Se tem constraint antiga sem excel_data_id, precisa recriar
            if 'UNIQUE(seq, sequencia)' in old_sql and 'UNIQUE(seq, sequencia, excel_data_id)' not in old_sql:
                print("AVISO: Tabela activity_control tem constraint antiga, será recriada na migração abaixo")
        else:
            # Tabela não existe, criar com constraint correta
            cursor.execute("""
                CREATE TABLE activity_control (
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
            """)
        
        # Migração: Adicionar coluna excel_data_id se não existir
        try:
            cursor.execute("ALTER TABLE activity_control ADD COLUMN excel_data_id INTEGER")
            # Para registros antigos, usar NULL (será tratado como 0 para compatibilidade)
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Migração: Adicionar coluna arquivado se não existir
        try:
            cursor.execute("ALTER TABLE activity_control ADD COLUMN arquivado INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Migração: Adicionar coluna is_rollback se não existir
        try:
            cursor.execute("ALTER TABLE activity_control ADD COLUMN is_rollback INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Migração: Remover constraint UNIQUE antiga e criar nova com excel_data_id
        try:
            # SQLite não suporta DROP CONSTRAINT, então precisamos recriar a tabela
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='activity_control'")
            old_sql_result = cursor.fetchone()
            
            # Verificar se precisa migrar
            needs_migration = False
            if old_sql_result:
                old_sql = old_sql_result[0]
                # Verificar se tem constraint antiga sem excel_data_id
                has_old_constraint = 'UNIQUE(seq, sequencia)' in old_sql and 'UNIQUE(seq, sequencia, excel_data_id)' not in old_sql
                # Se tem UNIQUE mas não tem excel_data_id na constraint, precisa migrar
                if has_old_constraint:
                    needs_migration = True
                    print(f"DEBUG: Detectada constraint antiga: {old_sql[:200]}")
            
            # Verificar também se a coluna excel_data_id existe mas não está na constraint
            if not needs_migration:
                try:
                    cursor.execute("PRAGMA table_info(activity_control)")
                    columns = cursor.fetchall()
                    has_excel_data_id_col = any(col[1] == 'excel_data_id' for col in columns)
                    if has_excel_data_id_col and old_sql_result:
                        old_sql = old_sql_result[0]
                        # Se tem a coluna mas não está na constraint UNIQUE, precisa migrar
                        if 'UNIQUE(seq, sequencia, excel_data_id)' not in old_sql:
                            needs_migration = True
                            print("DEBUG: Coluna excel_data_id existe mas não está na constraint UNIQUE")
                except:
                    pass
            
            if needs_migration:
                # Tabela antiga precisa ser migrada
                print("AVISO: Migrando tabela activity_control para suportar excel_data_id")
                
                # Verificar se a tabela tem dados
                cursor.execute("SELECT COUNT(*) FROM activity_control")
                has_data = cursor.fetchone()[0] > 0
                
                if has_data:
                    # Criar tabela nova
                    cursor.execute("""
                        CREATE TABLE activity_control_new (
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
                            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(seq, sequencia, excel_data_id)
                        )
                    """)
                    
                    # Copiar dados existentes (usar NULL para excel_data_id de registros antigos)
                    cursor.execute("""
                        INSERT INTO activity_control_new 
                        (id, seq, sequencia, excel_data_id, status, horario_inicio_real, 
                         horario_fim_real, atraso_minutos, observacoes, is_milestone, 
                         predecessoras, data_criacao, data_atualizacao)
                        SELECT id, seq, sequencia, 
                               COALESCE(excel_data_id, 0) as excel_data_id,
                               status, horario_inicio_real, 
                               horario_fim_real, atraso_minutos, observacoes, is_milestone, 
                               predecessoras, data_criacao, data_atualizacao
                        FROM activity_control
                    """)
                    
                    # Remover tabela antiga e renomear nova
                    cursor.execute("DROP TABLE activity_control")
                    cursor.execute("ALTER TABLE activity_control_new RENAME TO activity_control")
                else:
                    # Sem dados, apenas recriar a tabela
                    cursor.execute("DROP TABLE activity_control")
                    cursor.execute("""
                        CREATE TABLE activity_control (
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
                            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(seq, sequencia, excel_data_id)
                        )
                    """)
                
                # Recriar índices
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_seq_sequencia 
                    ON activity_control(seq, sequencia)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_excel_data_id 
                    ON activity_control(excel_data_id)
                """)
                
                conn.commit()
                print("AVISO: Migração concluída com sucesso")
            else:
                # Tabela já tem constraint correta, não precisa migrar
                print("DEBUG: Tabela activity_control já tem constraint correta")
        except Exception as e:
            print(f"AVISO: Erro na migração (pode ser ignorado se tabela já está correta): {e}")
            import traceback
            print(traceback.format_exc())
        
        # Adicionar novas colunas se a tabela já existir (migração)
        try:
            cursor.execute("ALTER TABLE activity_control ADD COLUMN is_milestone INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        try:
            cursor.execute("ALTER TABLE activity_control ADD COLUMN predecessoras TEXT")
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Criar índices para melhor performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_seq_sequencia 
            ON activity_control(seq, sequencia)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_excel_data_id 
            ON activity_control(excel_data_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON activity_control(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sequencia 
            ON activity_control(sequencia)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_seq 
            ON activity_control(seq)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_is_milestone 
            ON activity_control(is_milestone)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status_sequencia 
            ON activity_control(status, sequencia)
        """)
        
        # Criar tabela para persistir dados base do Excel
        # IMPORTANTE: Não usar UNIQUE(sequencia, seq) porque pode haver múltiplas linhas
        # com o mesmo Seq no mesmo CRQ no Excel. Cada linha do Excel deve ser única.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS excel_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequencia TEXT,
                seq INTEGER,
                atividade TEXT,
                grupo TEXT,
                localidade TEXT,
                executor TEXT,
                telefone TEXT,
                inicio TEXT,
                fim TEXT,
                tempo TEXT,
                data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Remover constraint UNIQUE se existir (migração)
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS temp_idx ON excel_data(sequencia, seq)
            """)
            cursor.execute("DROP INDEX IF EXISTS temp_idx")
        except:
            pass
        
        # Criar índices para excel_data (sem UNIQUE, permitir duplicatas de Seq no mesmo CRQ)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_excel_sequencia 
            ON excel_data(sequencia)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_excel_seq_sequencia 
            ON excel_data(seq, sequencia)
        """)
        
        # Migração: Remover constraint UNIQUE se existir em tabelas antigas
        # SQLite não suporta DROP CONSTRAINT diretamente, então precisamos recriar a tabela
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='excel_data'")
            old_sql = cursor.fetchone()
            if old_sql and 'UNIQUE(sequencia, seq)' in old_sql[0]:
                # Tabela antiga tem UNIQUE, precisa recriar
                print("AVISO: Removendo constraint UNIQUE da tabela excel_data (migração)")
                cursor.execute("""
                    CREATE TABLE excel_data_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sequencia TEXT,
                        seq INTEGER,
                        atividade TEXT,
                        grupo TEXT,
                        localidade TEXT,
                        executor TEXT,
                        telefone TEXT,
                        inicio TEXT,
                        fim TEXT,
                        tempo TEXT,
                        data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    INSERT INTO excel_data_new 
                    SELECT * FROM excel_data
                """)
                cursor.execute("DROP TABLE excel_data")
                cursor.execute("ALTER TABLE excel_data_new RENAME TO excel_data")
                
                # Recriar índices
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_excel_sequencia 
                    ON excel_data(sequencia)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_excel_seq_sequencia 
                    ON excel_data(seq, sequencia)
                """)
        except Exception as e:
            # Se der erro na migração, continuar (pode ser que a tabela já esteja correta)
            print(f"AVISO: Erro na migração (pode ser ignorado se tabela já está correta): {e}")
        
        conn.commit()
        conn.close()
    
    def get_activity_control(self, seq, sequencia, excel_data_id=None):
        """
        Busca dados de controle de uma atividade específica
        
        Args:
            seq: Número sequencial
            sequencia: Sequência/CRQ
            excel_data_id: ID da linha no excel_data (opcional, para identificar linha única)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if excel_data_id is not None:
            # Buscar por excel_data_id (mais preciso quando há duplicatas)
            cursor.execute("""
                SELECT status, horario_inicio_real, horario_fim_real, 
                       atraso_minutos, observacoes, is_milestone, predecessoras
                FROM activity_control
                WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
            """, (seq, sequencia, excel_data_id))
        else:
            # Buscar apenas por seq e sequencia (compatibilidade com código antigo)
            # Se houver múltiplas linhas, retorna a primeira
            cursor.execute("""
                SELECT status, horario_inicio_real, horario_fim_real, 
                       atraso_minutos, observacoes, is_milestone, predecessoras
                FROM activity_control
                WHERE seq = ? AND sequencia = ?
                LIMIT 1
            """, (seq, sequencia))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "status": result[0],
                "horario_inicio_real": result[1],
                "horario_fim_real": result[2],
                "atraso_minutos": result[3],
                "observacoes": result[4],
                "is_milestone": bool(result[5]) if result[5] is not None else False,
                "predecessoras": result[6] if result[6] else ""
            }
        return None
    
    def save_activity_control(self, seq, sequencia, status=None, 
                             horario_inicio_real=None, horario_fim_real=None,
                             atraso_minutos=None, observacoes=None,
                             is_milestone=None, predecessoras=None, excel_data_id=None):
        """
        Salva ou atualiza dados de controle de uma atividade
        
        Args:
            seq: Número sequencial
            sequencia: Sequência/CRQ
            excel_data_id: ID da linha no excel_data (opcional, para identificar linha única)
            ... outros parâmetros ...
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Normalizar excel_data_id: None vira 0, mas manter 0 se fornecido explicitamente
        if excel_data_id is None:
            excel_data_id = 0
        
        # Verificar se já existe (sempre usar excel_data_id na busca, mesmo se for 0)
        existing = self.get_activity_control(seq, sequencia, excel_data_id)
        
        if existing:
            # Atualizar
            updates = []
            params = []
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if horario_inicio_real is not None:
                updates.append("horario_inicio_real = ?")
                params.append(horario_inicio_real)
            if horario_fim_real is not None:
                updates.append("horario_fim_real = ?")
                params.append(horario_fim_real)
            if atraso_minutos is not None:
                updates.append("atraso_minutos = ?")
                params.append(atraso_minutos)
            if observacoes is not None:
                updates.append("observacoes = ?")
                params.append(observacoes)
            if is_milestone is not None:
                updates.append("is_milestone = ?")
                params.append(1 if is_milestone else 0)
            if predecessoras is not None:
                updates.append("predecessoras = ?")
                params.append(predecessoras)
            
            updates.append("data_atualizacao = ?")
            params.append(datetime.now().isoformat())
            
            # Sempre usar excel_data_id na cláusula WHERE (mesmo se for 0)
            params.extend([seq, sequencia, excel_data_id])
            cursor.execute(f"""
                UPDATE activity_control
                SET {', '.join(updates)}
                WHERE seq = ? AND sequencia = ? AND excel_data_id = ?
            """, params)
        else:
            # Inserir novo - sempre usar excel_data_id (mesmo se for 0)
            cursor.execute("""
                INSERT INTO activity_control 
                (seq, sequencia, excel_data_id, status, horario_inicio_real, horario_fim_real, 
                 atraso_minutos, observacoes, is_milestone, predecessoras)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (seq, sequencia, excel_data_id,
                  status or "Planejado",
                  horario_inicio_real,
                  horario_fim_real,
                  atraso_minutos or 0,
                  observacoes,
                  1 if is_milestone else 0,
                  predecessoras or ""))
        
        conn.commit()
        conn.close()
    
    def get_all_activities_control(self):
        """Retorna todos os dados de controle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT seq, sequencia, excel_data_id, status, horario_inicio_real, 
                   horario_fim_real, atraso_minutos, observacoes,
                   is_milestone, predecessoras
            FROM activity_control
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        activities = {}
        for row in results:
            seq, sequencia, excel_data_id = row[0], row[1], row[2]
            # Usar excel_data_id na chave se disponível, senão usar chave antiga
            if excel_data_id and excel_data_id != 0:
                key = f"{seq}_{sequencia}_{excel_data_id}"
            else:
                key = f"{seq}_{sequencia}"
            activities[key] = {
                "seq": seq,
                "sequencia": sequencia,
                "excel_data_id": excel_data_id if excel_data_id else 0,
                "status": row[3],
                "horario_inicio_real": row[4],
                "horario_fim_real": row[5],
                "atraso_minutos": row[6],
                "observacoes": row[7],
                "is_milestone": bool(row[8]) if row[8] is not None else False,
                "predecessoras": row[9] if row[9] else ""
            }
        
        return activities
    
    def clear_all_control_data(self):
        """Limpa todos os dados de controle (útil para reset)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM activity_control")
        
        conn.commit()
        conn.close()
    
    def bulk_save_activities(self, activities_data):
        """Salva múltiplas atividades de uma vez"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for activity in activities_data:
            cursor.execute("""
                INSERT OR REPLACE INTO activity_control
                (seq, sequencia, status, horario_inicio_real, horario_fim_real,
                 atraso_minutos, observacoes, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity["seq"],
                activity["sequencia"],
                activity.get("status", "Planejado"),
                activity.get("horario_inicio_real"),
                activity.get("horario_fim_real"),
                activity.get("atraso_minutos", 0),
                activity.get("observacoes"),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def save_excel_data(self, data_dict, file_name=None):
        """
        Salva dados do Excel no banco de dados
        
        Args:
            data_dict: Dicionário com dataframes de cada sequência
            file_name: Nome do arquivo Excel (opcional)
        """
        import pandas as pd
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Limpar dados antigos do Excel ANTES de salvar novos
        # Isso garante que não haja dados duplicados ou antigos
        cursor.execute("DELETE FROM excel_data")
        conn.commit()
        
        # Verificar se há dados sendo salvos
        if not data_dict or len(data_dict) == 0:
            conn.close()
            return 0
        
        # Contador de registros salvos
        total_saved = 0
        
        # Salvar novos dados
        for sequencia, data in data_dict.items():
            df = data["dataframe"]
            print(f"DEBUG: Salvando {len(df)} registros da sequência {sequencia}")
            
            for idx, row in df.iterrows():
                try:
                    # Converter datas para string ISO
                    inicio_str = None
                    fim_str = None
                    
                    if "Inicio" in row and pd.notna(row["Inicio"]):
                        if hasattr(row["Inicio"], 'isoformat'):
                            inicio_str = row["Inicio"].isoformat()
                        elif isinstance(row["Inicio"], str):
                            inicio_str = row["Inicio"]
                        else:
                            inicio_str = str(row["Inicio"])
                    
                    if "Fim" in row and pd.notna(row["Fim"]):
                        if hasattr(row["Fim"], 'isoformat'):
                            fim_str = row["Fim"].isoformat()
                        elif isinstance(row["Fim"], str):
                            fim_str = row["Fim"]
                        else:
                            fim_str = str(row["Fim"])
                    
                    # Converter Seq para int - ser mais tolerante
                    seq_value = None
                    if "Seq" in row:
                        seq_raw = row["Seq"]
                        if pd.notna(seq_raw):
                            try:
                                # Tentar converter diretamente
                                seq_value = int(seq_raw)
                            except (ValueError, TypeError):
                                # Tentar extrair número de string
                                try:
                                    seq_str = str(seq_raw).strip()
                                    # Remover caracteres não numéricos e tentar converter
                                    import re
                                    numbers = re.findall(r'\d+', seq_str)
                                    if numbers:
                                        seq_value = int(numbers[0])
                                    else:
                                        # Se não conseguir, usar índice como fallback
                                        seq_value = 999000 + total_saved
                                        print(f"AVISO: Seq inválido '{seq_raw}' na sequência {sequencia}, usando Seq temporário {seq_value}")
                                except Exception as e:
                                    # Usar índice como fallback
                                    seq_value = 999000 + total_saved
                                    print(f"AVISO: Erro ao processar Seq '{seq_raw}' na sequência {sequencia}: {e}, usando Seq temporário {seq_value}")
                        else:
                            # Seq é NaN, verificar se tem Atividade
                            atividade = str(row.get("Atividade", "")).strip()
                            if atividade and atividade != "":
                                # Tem Atividade mas não Seq, gerar Seq temporário
                                seq_value = 999000 + total_saved
                                print(f"AVISO: Linha sem Seq mas com Atividade '{atividade[:50]}...' na sequência {sequencia}, usando Seq temporário {seq_value}")
                            else:
                                # Sem Seq e sem Atividade, pular
                                print(f"AVISO: Linha sem Seq e sem Atividade na sequência {sequencia}, linha pulada")
                                continue
                    
                    if seq_value is None:
                        print(f"AVISO: Não foi possível determinar Seq para linha na sequência {sequencia}, linha pulada")
                        continue
                    
                    # Validar que temos pelo menos Seq e Atividade
                    atividade = str(row.get("Atividade", "")).strip()
                    if not atividade or atividade == "":
                        print(f"AVISO: Linha com Seq {seq_value} mas sem Atividade na sequência {sequencia}, linha pulada")
                        continue
                    
                    # IMPORTANTE: Cada linha do Excel é única, mesmo que tenha o mesmo Seq
                    # Não usar UNIQUE constraint, permitir múltiplas linhas com mesmo (sequencia, seq)
                    # A chave primária 'id' garante unicidade de cada linha
                    
                    # Inserir novo registro (sempre INSERT, não UPDATE)
                    # Como limpamos a tabela antes, não há risco de duplicatas de importação anterior
                    cursor.execute("""
                        INSERT INTO excel_data
                        (sequencia, seq, atividade, grupo, localidade, executor, 
                         telefone, inicio, fim, tempo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sequencia,
                        seq_value,
                            atividade,
                            str(row.get("Grupo", "")),
                            str(row.get("Localidade", "")),
                            str(row.get("Executor", "")),
                            str(row.get("Telefone", "")),
                            inicio_str,
                            fim_str,
                            float(row.get("Tempo", 0)) if pd.notna(row.get("Tempo", 0)) else 0
                        ))
                    total_saved += 1
                except Exception as e:
                    # Log do erro mas continua
                    import traceback
                    print(f"ERRO ao salvar linha {row.get('Seq', 'N/A')} da sequência {sequencia}: {e}")
                    print(traceback.format_exc())
                    continue
            
            print(f"DEBUG: Processados {total_saved} registros até agora da sequência {sequencia}")
        
        # Fazer commit de todos os registros de uma vez
        conn.commit()
        
        # Verificar quantos registros foram realmente salvos
        cursor.execute("SELECT COUNT(*) FROM excel_data")
        actual_count = cursor.fetchone()[0]
        print(f"DEBUG: Total de registros realmente salvos no banco: {actual_count}")
        
        if actual_count != total_saved:
            print(f"AVISO: Discrepância detectada! Processados {total_saved} mas salvos {actual_count}")
        
        conn.close()
        
        # Retornar o número real de registros salvos, não o contador
        return actual_count
    
    def load_excel_data(self):
        """
        Carrega dados do Excel salvos no banco de dados
        
        Returns:
            dict: Dicionário com dataframes de cada sequência ou None se não houver dados
        """
        import pandas as pd
        from modules.calculations import convert_time_to_minutes
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, sequencia, seq, atividade, grupo, localidade, executor, 
                   telefone, inicio, fim, tempo
            FROM excel_data
            ORDER BY sequencia, seq
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return None
        
        # Agrupar por sequência e criar lista de dados
        data_by_sequence = {}
        for row in results:
            excel_data_id = row[0]  # ID único da linha no excel_data
            sequencia = row[1]
            if sequencia not in data_by_sequence:
                data_by_sequence[sequencia] = []
            
            # Converter datas
            inicio = None
            fim = None
            try:
                if row[8]:  # Ajustado para nova posição (id agora é row[0])
                    inicio = pd.to_datetime(row[8], errors='coerce')
                if row[9]:
                    fim = pd.to_datetime(row[9], errors='coerce')
            except:
                pass
            
            data_by_sequence[sequencia].append({
                "Seq": int(row[2]) if row[2] is not None else None,
                "Atividade": row[3] or "",
                "Grupo": row[4] or "",
                "Localidade": row[5] or "",
                "Executor": row[6] or "",
                "Telefone": row[7] or "",
                "Inicio": inicio,
                "Fim": fim,
                "Tempo": convert_time_to_minutes(row[10]) if row[10] else 0,
                "CRQ": sequencia,
                "Excel_Data_ID": excel_data_id  # ID único para identificar a linha
            })
        
        # Criar dataframes para cada sequência
        data_dict = {}
        for sequencia, rows in data_by_sequence.items():
            if rows:
                # Criar DataFrame com tipos explícitos para evitar warnings
                df = pd.DataFrame(rows)
                # Converter Seq para Int64
                if "Seq" in df.columns:
                    df["Seq"] = pd.to_numeric(df["Seq"], errors='coerce').astype('Int64')
                
                # Converter colunas sensíveis para string (evitar tipos mistos do PyArrow)
                def safe_str_convert(val):
                    if pd.isna(val) or val is None:
                        return ""
                    try:
                        if isinstance(val, (int, float)):
                            return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
                        return str(val)
                    except:
                        return ""
                
                for col in ["Telefone", "Grupo", "Localidade", "Executor", "Tempo", "Atividade"]:
                    if col in df.columns:
                        df[col] = df[col].apply(safe_str_convert)
                
                data_dict[sequencia] = {
                    "dataframe": df,
                    "sheet_name": sequencia
                }
        
        return data_dict if data_dict else None
    
    def clear_all_data(self):
        """
        Limpa todos os dados do banco (Excel e controle)
        
        Returns:
            tuple: (excel_deleted, control_deleted) - número de registros deletados
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Contar registros antes de deletar
        cursor.execute("SELECT COUNT(*) FROM excel_data")
        excel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM activity_control")
        control_count = cursor.fetchone()[0]
        
        # Deletar todos os dados
        cursor.execute("DELETE FROM excel_data")
        cursor.execute("DELETE FROM activity_control")
        
        # Verificar se foi deletado
        cursor.execute("SELECT COUNT(*) FROM excel_data")
        excel_remaining = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM activity_control")
        control_remaining = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return (excel_count, control_count, excel_remaining == 0 and control_remaining == 0)
    
    def export_all_data(self):
        """
        Exporta todos os dados do banco (Excel + controle) para um formato JSON
        
        Returns:
            dict: Dicionário com todos os dados exportados
        """
        import json
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Exportar dados do Excel
        cursor.execute("""
            SELECT sequencia, seq, atividade, grupo, localidade, executor, 
                   telefone, inicio, fim, tempo
            FROM excel_data
            ORDER BY sequencia, seq
        """)
        excel_rows = cursor.fetchall()
        
        excel_data = []
        for row in excel_rows:
            excel_data.append({
                "sequencia": row[0],
                "seq": row[1],
                "atividade": row[2],
                "grupo": row[3],
                "localidade": row[4],
                "executor": row[5],
                "telefone": row[6],
                "inicio": row[7],
                "fim": row[8],
                "tempo": row[9]
            })
        
        # Exportar dados de controle
        cursor.execute("""
            SELECT seq, sequencia, status, horario_inicio_real, horario_fim_real,
                   atraso_minutos, observacoes, is_milestone, predecessoras,
                   data_criacao, data_atualizacao
            FROM activity_control
            ORDER BY sequencia, seq
        """)
        control_rows = cursor.fetchall()
        
        control_data = []
        for row in control_rows:
            control_data.append({
                "seq": row[0],
                "sequencia": row[1],
                "status": row[2],
                "horario_inicio_real": row[3],
                "horario_fim_real": row[4],
                "atraso_minutos": row[5],
                "observacoes": row[6],
                "is_milestone": bool(row[7]) if row[7] is not None else False,
                "predecessoras": row[8],
                "data_criacao": row[9],
                "data_atualizacao": row[10]
            })
        
        conn.close()
        
        # Criar estrutura de exportação
        export_data = {
            "version": "1.0",
            "export_date": datetime.now().isoformat(),
            "excel_data": excel_data,
            "control_data": control_data,
            "metadata": {
                "excel_count": len(excel_data),
                "control_count": len(control_data)
            }
        }
        
        return export_data
    
    def import_all_data(self, import_data):
        """
        Importa todos os dados do formato JSON para o banco
        
        Args:
            import_data: Dicionário com dados exportados
            
        Returns:
            tuple: (excel_imported, control_imported, success) - número de registros importados
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Limpar dados existentes
            cursor.execute("DELETE FROM excel_data")
            cursor.execute("DELETE FROM activity_control")
            
            excel_imported = 0
            control_imported = 0
            
            # Importar dados do Excel
            if "excel_data" in import_data:
                for row in import_data["excel_data"]:
                    try:
                        cursor.execute("""
                            INSERT INTO excel_data
                            (sequencia, seq, atividade, grupo, localidade, executor, 
                             telefone, inicio, fim, tempo)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row.get("sequencia"),
                            row.get("seq"),
                            row.get("atividade", ""),
                            row.get("grupo", ""),
                            row.get("localidade", ""),
                            row.get("executor", ""),
                            row.get("telefone", ""),
                            row.get("inicio"),
                            row.get("fim"),
                            row.get("tempo", "")
                        ))
                        excel_imported += 1
                    except Exception as e:
                        print(f"Erro ao importar linha Excel: {e}")
                        continue
            
            # Importar dados de controle
            if "control_data" in import_data:
                for row in import_data["control_data"]:
                    try:
                        cursor.execute("""
                            INSERT INTO activity_control
                            (seq, sequencia, status, horario_inicio_real, horario_fim_real,
                             atraso_minutos, observacoes, is_milestone, predecessoras,
                             data_criacao, data_atualizacao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row.get("seq"),
                            row.get("sequencia"),
                            row.get("status", "Planejado"),
                            row.get("horario_inicio_real"),
                            row.get("horario_fim_real"),
                            row.get("atraso_minutos", 0),
                            row.get("observacoes"),
                            1 if row.get("is_milestone", False) else 0,
                            row.get("predecessoras"),
                            row.get("data_criacao"),
                            row.get("data_atualizacao")
                        ))
                        control_imported += 1
                    except Exception as e:
                        print(f"Erro ao importar linha controle: {e}")
                        continue
            
            conn.commit()
            conn.close()
            
            return excel_imported, control_imported, True
            
        except Exception as e:
            print(f"Erro ao importar dados: {e}")
            return 0, 0, False