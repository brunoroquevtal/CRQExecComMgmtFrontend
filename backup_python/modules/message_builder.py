"""
Módulo para construção de mensagem consolidada para WhatsApp
"""
from datetime import datetime, timezone, timedelta
from config import DATE_FORMAT, SEQUENCIAS
from modules.calculations import (
    calculate_statistics, get_delayed_activities, 
    is_sequence_completed, format_delay
)


def build_whatsapp_message(data_dict):
    """
    Constrói mensagem consolidada para WhatsApp
    
    Args:
        data_dict: Dicionário com dataframes por CRQ
        
    Returns:
        str: Mensagem formatada para WhatsApp
    """
    stats = calculate_statistics(data_dict)
    
    # Obter total real importado
    total_geral = stats['geral']['total']
    
    # Cabeçalho - usar GMT-3 (Brasil)
    gmt_minus_3 = timezone(timedelta(hours=-3))
    now = datetime.now(gmt_minus_3)
    data_str = now.strftime("%d/%m/%Y")
    hora_str = now.strftime("%H:%M:%S")
    
    # Construir mensagem com quebras de linha explícitas
    message = f"🚀 *JANELA DE MUDANÇA - REDE*\n\n"
    message += f"📅 Data: {data_str} | 🕐 Horário: {hora_str}\n\n"
    message += f"━━━━━━━━━━━━━━━━━━\n\n"
    message += f"📈 *STATUS CRQ GERAL*\n"
    message += f"  ✅ Concluídas: {stats['geral']['concluidas']}/{total_geral} ({stats['geral'].get('pct_concluidas', 0):.1f}%)\n"
    message += f"  ⏳ Em Execução: {stats['geral']['em_execucao']}/{total_geral} ({stats['geral'].get('pct_em_execucao', 0):.1f}%)\n"
    message += f"  🟡 Planejadas: {stats['geral']['planejadas']}/{total_geral} ({stats['geral'].get('pct_planejadas', 0):.1f}%)\n"
    message += f"  🔴 Atrasadas: {stats['geral']['atrasadas']}/{total_geral} ({stats['geral'].get('pct_atrasadas', 0):.1f}%)\n\n"
    message += f"━━━━━━━━━━━━━━━━━━\n"
    
    # Separar CRQs iniciadas das não iniciadas
    crqs_iniciadas = []
    crqs_nao_iniciadas = []
    
    for sequencia_key, sequencia_info in SEQUENCIAS.items():
        if sequencia_key in stats["por_sequencia"]:
            seq_stats = stats["por_sequencia"][sequencia_key]
            
            if seq_stats["total"] > 0:
                # CRQ está iniciada se tiver atividades em execução, concluídas, atrasadas ou adiantadas
                # (ou seja, se não estiver 100% planejada)
                if (seq_stats["em_execucao"] > 0 or 
                    seq_stats["concluidas"] > 0 or 
                    seq_stats["atrasadas"] > 0 or
                    seq_stats.get("adiantadas", 0) > 0):
                    crqs_iniciadas.append((sequencia_key, sequencia_info, seq_stats))
                else:
                    crqs_nao_iniciadas.append((sequencia_key, sequencia_info, seq_stats))
    
    # Mostrar primeiro CRQs iniciadas (com detalhamento)
    if crqs_iniciadas:
        message += "\n📊 *CRQs INICIADAS*\n"
        for sequencia_key, sequencia_info, seq_stats in crqs_iniciadas:
            emoji = sequencia_info["emoji"]
            nome = sequencia_info["nome"]
            total = seq_stats["total"]
            
            message += f"\n{emoji} *STATUS CRQ {nome}*\n"
            message += f"  ✅ Concluídas: {seq_stats['concluidas']}/{total} ({seq_stats.get('pct_concluidas', 0):.1f}%)\n"
            message += f"  ⏳ Em Execução: {seq_stats['em_execucao']}/{total} ({seq_stats.get('pct_em_execucao', 0):.1f}%)\n"
            message += f"  🟡 Planejadas: {seq_stats['planejadas']}/{total} ({seq_stats.get('pct_planejadas', 0):.1f}%)\n"
            message += f"  🔴 Atrasadas: {seq_stats['atrasadas']}/{total} ({seq_stats.get('pct_atrasadas', 0):.1f}%)\n"
    
    # Mostrar depois CRQs não iniciadas (apenas indicador)
    if crqs_nao_iniciadas:
        message += "\n\n⏸️ *CRQs NÃO INICIADAS*\n"
        nomes_nao_iniciadas = []
        for sequencia_key, sequencia_info, seq_stats in crqs_nao_iniciadas:
            emoji = sequencia_info["emoji"]
            nome = sequencia_info["nome"]
            nomes_nao_iniciadas.append(f"{emoji} {nome}")
        
        message += f"  {', '.join(nomes_nao_iniciadas)}\n"
    
    message += "\n━━━━━━━━━━━━━━━━━━\n\n"
    
    # CRQs concluídos
    concluidas = []
    for sequencia_key in SEQUENCIAS.keys():
        if is_sequence_completed(data_dict, sequencia_key):
            concluidas.append(SEQUENCIAS[sequencia_key]["nome"])
    
    if concluidas:
        message += "📋 *CONCLUÍDAS*\n"
        message += f"  {', '.join(concluidas)}\n\n"
        message += "━━━━━━━━━━━━━━━━━━\n\n"
    
    # Atividades atrasadas
    delayed_df = get_delayed_activities(data_dict)
    
    if len(delayed_df) > 0:
        message += "🚨 *ATIVIDADES ATRASADAS*\n"
        
        # Agrupar por CRQ
        for sequencia_key, sequencia_info in SEQUENCIAS.items():
            seq_delayed = delayed_df[delayed_df["CRQ"] == sequencia_key]
            
            if len(seq_delayed) > 0:
                emoji = sequencia_info["emoji"]
                nome = sequencia_info["nome"]
                
                for _, row in seq_delayed.iterrows():
                    atividade = row["Atividade"]
                    atraso_min = row.get("Atraso_Minutos", 0)
                    observacoes = row.get("Observacoes", "")
                    
                    atraso_str = format_delay(atraso_min)
                    
                    message += f"\n  {emoji} [{nome}] {atividade}: {atraso_str}\n"
                    if observacoes and str(observacoes).strip():
                        message += f"     Observação: {observacoes}\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━\n\n"
    
    # Rodapé - usar o mesmo horário GMT-3
    atualizado_str = now.strftime("%d/%m/%Y %H:%M:%S")
    message += f"✅ Atualizado em: {atualizado_str}\n"
    
    return message
