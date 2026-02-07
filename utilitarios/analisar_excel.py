import pandas as pd
import openpyxl
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

def parse_datetime_from_excel(value):
    """Função similar à do sincronizador Python"""
    if pd.isna(value) or value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    
    if isinstance(value, (int, float)):
        # Pode ser número serial do Excel
        try:
            return pd.Timestamp.fromordinal(int(value) + 693594).to_pydatetime()
        except:
            return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() in ['n/a', 'na', '']:
            return None
        
        # Tentar vários formatos
        formats = [
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except:
                continue
    
    return None

def analisar_logica_python(df, sequencia='REDE'):
    """Analisa segundo a lógica do sincronizador Python"""
    atividades_enviadas = []
    atividades_rejeitadas = []
    
    # Identificar colunas (similar ao sincronizador)
    seq_col = None
    atividade_col = None
    status_col = None
    inicio_planejado_col = None
    fim_planejado_col = None
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if not seq_col and ('seq' in col_lower or 'sequência' in col_lower):
            seq_col = col
        elif not atividade_col and ('atividade' in col_lower):
            atividade_col = col
        elif not status_col and ('status' in col_lower or 'situação' in col_lower):
            status_col = col
        elif not inicio_planejado_col and ('inicio' in col_lower or 'início' in col_lower) and 'real' not in col_lower:
            inicio_planejado_col = col
        elif not fim_planejado_col and ('fim' in col_lower) and 'real' not in col_lower:
            fim_planejado_col = col
    
    print(f"\n[PYTHON] Colunas identificadas:")
    print(f"  Seq: {seq_col}")
    print(f"  Atividade: {atividade_col}")
    print(f"  Status: {status_col}")
    print(f"  Início Planejado: {inicio_planejado_col}")
    print(f"  Fim Planejado: {fim_planejado_col}")
    
    for idx, row in df.iterrows():
        motivo_rejeicao = None
        
        # Validar Seq
        seq_value = row[seq_col] if seq_col else None
        if pd.isna(seq_value):
            motivo_rejeicao = "Seq vazio ou NaN"
            atividades_rejeitadas.append({
                'linha': idx + 2,  # +2 porque Excel começa em 1 e tem header
                'seq': seq_value,
                'sequencia': sequencia,
                'atividade': row[atividade_col] if atividade_col else 'N/A',
                'status': row[status_col] if status_col else 'N/A',
                'motivo_rejeicao': motivo_rejeicao
            })
            continue
        
        try:
            seq = int(float(seq_value))
        except:
            motivo_rejeicao = f"Seq inválido (valor: {seq_value})"
            atividades_rejeitadas.append({
                'linha': idx + 2,
                'seq': seq_value,
                'sequencia': sequencia,
                'atividade': row[atividade_col] if atividade_col else 'N/A',
                'status': row[status_col] if status_col else 'N/A',
                'motivo_rejeicao': motivo_rejeicao
            })
            continue
        
        # Validar atividade
        atividade = None
        if atividade_col and atividade_col in row:
            atividade_value = row[atividade_col]
            if not pd.isna(atividade_value):
                atividade = str(atividade_value).strip()
        
        if not atividade or atividade == "":
            motivo_rejeicao = "Atividade vazia ou não encontrada"
            atividades_rejeitadas.append({
                'linha': idx + 2,
                'seq': seq,
                'sequencia': sequencia,
                'atividade': 'N/A',
                'status': row[status_col] if status_col else 'N/A',
                'motivo_rejeicao': motivo_rejeicao
            })
            continue
        
        # Validar início/fim planejado
        inicio_planejado = None
        fim_planejado = None
        
        if inicio_planejado_col and inicio_planejado_col in row:
            if pd.notna(row[inicio_planejado_col]):
                inicio_planejado = parse_datetime_from_excel(row[inicio_planejado_col])
        
        if fim_planejado_col and fim_planejado_col in row:
            if pd.notna(row[fim_planejado_col]):
                fim_planejado = parse_datetime_from_excel(row[fim_planejado_col])
        
        if not inicio_planejado and not fim_planejado:
            motivo_rejeicao = "Sem início ou fim planejado"
            atividades_rejeitadas.append({
                'linha': idx + 2,
                'seq': seq,
                'sequencia': sequencia,
                'atividade': atividade[:100] if atividade else 'N/A',
                'status': row[status_col] if status_col else 'N/A',
                'inicio_planejado': row[inicio_planejado_col] if inicio_planejado_col else 'N/A',
                'fim_planejado': row[fim_planejado_col] if fim_planejado_col else 'N/A',
                'motivo_rejeicao': motivo_rejeicao
            })
            continue
        
        # Se passou todas as validações, será enviado
        atividades_enviadas.append({
            'linha': idx + 2,
            'seq': seq,
            'sequencia': sequencia,
            'atividade': atividade[:100] if atividade else 'N/A',
            'status': row[status_col] if status_col else 'N/A',
        })
    
    return atividades_enviadas, atividades_rejeitadas

def analisar_logica_backend(df, sequencia='REDE'):
    """Analisa segundo a lógica do backend (upload Excel)"""
    atividades_persistidas = []
    atividades_nao_persistidas = []
    
    def getValue(possibleNames, row):
        for name in possibleNames:
            for col in df.columns:
                if str(col).lower().strip() == name.lower().strip():
                    if col in row:
                        return row[col]
        return None
    
    def parseExcelDate(value):
        """Função similar à do backend"""
        if pd.isna(value) or value is None:
            return None
        
        if isinstance(value, datetime):
            year = value.year
            if year >= 1900 and year <= 2100:
                return value
            return None
        
        if isinstance(value, pd.Timestamp):
            year = value.year
            if year >= 1900 and year <= 2100:
                return value.to_pydatetime()
            return None
        
        if isinstance(value, (int, float)):
            # Número serial do Excel
            if value >= 1 and value < 100000:
                try:
                    excelEpoch = datetime(1899, 12, 30)
                    jsDate = excelEpoch + pd.Timedelta(days=value - 1)
                    year = jsDate.year
                    if year >= 1900 and year <= 2100:
                        return jsDate
                except:
                    pass
            return None
        
        if isinstance(value, str):
            str_val = value.strip()
            if not str_val or str_val.lower() in ['n/a', 'na', '']:
                return None
            
            # Verificar se não é status
            statusKeywords = [
                'concluído', 'concluido', 
                'em execução no prazo', 'em execucao no prazo',
                'em execução fora do prazo', 'em execucao fora do prazo',
                'a iniciar no prazo',
                'a iniciar fora do prazo'
            ]
            if any(kw in str_val.lower() for kw in statusKeywords):
                return None
            
            # Tentar parsear
            formats = [
                '%d/%m/%Y %H:%M',
                '%d/%m/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(str_val, fmt)
                    if dt.year >= 1900 and dt.year <= 2100:
                        return dt
                except:
                    continue
            
            # Tentar parse direto
            try:
                dt = pd.to_datetime(str_val)
                if dt.year >= 1900 and dt.year <= 2100:
                    return dt.to_pydatetime()
            except:
                pass
        
        return None
    
    for idx, row in df.iterrows():
        seq = getValue(['Seq', 'seq', 'SEQ', 'Sequência', 'sequencia'], row)
        atividade = getValue(['Atividade', 'atividade', 'ATIVIDADE'], row)
        grupo = getValue(['Grupo', 'grupo', 'GRUPO'], row)
        inicio = getValue(['Inicio', 'inicio', 'INICIO', 'Início', 'início', 'INÍCIO'], row)
        fim = getValue(['Fim', 'fim', 'FIM'], row)
        status = getValue(['Status', 'status', 'STATUS', 'Situação', 'situacao', 'SITUACAO'], row)
        
        motivo_nao_persistir = None
        
        # Validar campos básicos
        hasSeq = seq and not pd.isna(seq) and (isinstance(seq, (int, float)) or str(seq).strip() != '')
        hasAtividade = atividade and not pd.isna(atividade) and str(atividade).strip() != ''
        
        # Converter datas
        inicioDate = parseExcelDate(inicio) if inicio else None
        fimDate = parseExcelDate(fim) if fim else None
        hasInicio = inicioDate is not None
        hasFim = fimDate is not None
        
        # Verificar grupo e status para is_visible
        grupoStr = str(grupo).strip().lower() if grupo and not pd.isna(grupo) else ''
        grupoVazioOuNA = not grupoStr or grupoStr == '' or grupoStr in ['n/a', 'na']
        
        statusStr = str(status).strip().lower() if status and not pd.isna(status) else ''
        if statusStr in ['n/a', 'na', '']:
            statusStr = ''
        statusVazioOuNA = not statusStr or statusStr == ''
        
        # Critérios para is_visible = 1
        isVisible = hasSeq and hasAtividade and (hasInicio or hasFim) and not (grupoVazioOuNA and statusVazioOuNA)
        
        if not isVisible:
            motivos = []
            if not hasSeq:
                motivos.append("Seq inválido ou vazio")
            if not hasAtividade:
                motivos.append("Atividade vazia")
            if not hasInicio and not hasFim:
                motivos.append("Sem início ou fim válido")
            if grupoVazioOuNA and statusVazioOuNA:
                motivos.append("Grupo E Status vazios/N/A (is_visible=0)")
            
            motivo_nao_persistir = " | ".join(motivos)
            
            atividades_nao_persistidas.append({
                'linha': idx + 2,
                'seq': seq if hasSeq else 'N/A',
                'sequencia': sequencia,
                'atividade': str(atividade)[:100] if hasAtividade else 'N/A',
                'grupo': str(grupo) if grupo and not pd.isna(grupo) else 'N/A',
                'status': str(status) if status and not pd.isna(status) else 'N/A',
                'inicio': str(inicio) if inicio and not pd.isna(inicio) else 'N/A',
                'fim': str(fim) if fim and not pd.isna(fim) else 'N/A',
                'motivo_nao_persistir': motivo_nao_persistir,
                'is_visible': 0
            })
        else:
            atividades_persistidas.append({
                'linha': idx + 2,
                'seq': seq,
                'sequencia': sequencia,
                'atividade': str(atividade)[:100] if atividade else 'N/A',
                'grupo': str(grupo) if grupo and not pd.isna(grupo) else 'N/A',
                'status': str(status) if status and not pd.isna(status) else 'N/A',
                'is_visible': 1
            })
    
    return atividades_persistidas, atividades_nao_persistidas

def main():
    # Caminho do arquivo Excel
    excel_path = r"C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub\CRQExecComMgmtFrontend\utilitarios\CRQ VIRADA REDE.xlsx"
    
    print(f"Lendo arquivo: {excel_path}")
    
    # Ler todas as abas do Excel
    excel_file = pd.ExcelFile(excel_path)
    
    todas_atividades_enviadas = []
    todas_atividades_rejeitadas = []
    todas_atividades_persistidas = []
    todas_atividades_nao_persistidas = []
    
    # Processar cada aba
    for sheet_name in excel_file.sheet_names:
        print(f"\n{'='*60}")
        print(f"Processando aba: {sheet_name}")
        print(f"{'='*60}")
        
        # Identificar sequência (similar ao backend)
        sequencia = None
        sequencias_possiveis = ['REDE', 'OPENSHIFT', 'NFS', 'SI']
        for seq in sequencias_possiveis:
            if seq.upper() in sheet_name.upper():
                sequencia = seq
                break
        
        if not sequencia:
            print(f"  ⚠️ Aba '{sheet_name}' não reconhecida, pulando...")
            continue
        
        # Ler dados da aba
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        print(f"  Total de linhas: {len(df)}")
        
        # Analisar segundo lógica Python
        print(f"\n[ANÁLISE PYTHON - Lógica do Sincronizador]")
        enviadas, rejeitadas = analisar_logica_python(df, sequencia)
        todas_atividades_enviadas.extend(enviadas)
        todas_atividades_rejeitadas.extend(rejeitadas)
        print(f"  ✅ Serão enviadas à API: {len(enviadas)}")
        print(f"  ❌ NÃO serão enviadas: {len(rejeitadas)}")
        
        # Analisar segundo lógica Backend
        print(f"\n[ANÁLISE BACKEND - Lógica de Upload Excel]")
        persistidas, nao_persistidas = analisar_logica_backend(df, sequencia)
        todas_atividades_persistidas.extend(persistidas)
        todas_atividades_nao_persistidas.extend(nao_persistidas)
        print(f"  ✅ Serão persistidas no banco: {len(persistidas)}")
        print(f"  ❌ NÃO serão persistidas: {len(nao_persistidas)}")
    
    # Resumo geral
    print(f"\n{'='*60}")
    print("RESUMO GERAL")
    print(f"{'='*60}")
    print(f"[PYTHON - Sincronizador]")
    print(f"  Total que SERÃO enviados à API: {len(todas_atividades_enviadas)}")
    print(f"  Total que NÃO serão enviados: {len(todas_atividades_rejeitadas)}")
    print(f"\n[BACKEND - Upload Excel]")
    print(f"  Total que SERÃO persistidos: {len(todas_atividades_persistidas)}")
    print(f"  Total que NÃO serão persistidos: {len(todas_atividades_nao_persistidas)}")
    
    # Salvar CSVs
    if todas_atividades_rejeitadas:
        df_rejeitadas = pd.DataFrame(todas_atividades_rejeitadas)
        csv_path_python = "registros_nao_enviados_python.csv"
        df_rejeitadas.to_csv(csv_path_python, index=False, encoding='utf-8-sig')
        print(f"\n✅ CSV salvo: {csv_path_python}")
        print(f"   Total de registros: {len(df_rejeitadas)}")
    
    if todas_atividades_nao_persistidas:
        df_nao_persistidas = pd.DataFrame(todas_atividades_nao_persistidas)
        csv_path_backend = "registros_nao_persistidos_backend.csv"
        df_nao_persistidas.to_csv(csv_path_backend, index=False, encoding='utf-8-sig')
        print(f"✅ CSV salvo: {csv_path_backend}")
        print(f"   Total de registros: {len(df_nao_persistidas)}")
    
    print(f"\n{'='*60}")
    print("Análise concluída!")

if __name__ == "__main__":
    main()