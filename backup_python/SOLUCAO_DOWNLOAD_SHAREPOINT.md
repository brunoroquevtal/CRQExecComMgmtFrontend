# ✅ Solução Rápida: Erro ao Baixar do SharePoint

## 🔴 Problema
O script não consegue baixar automaticamente do SharePoint porque:
- SharePoint requer autenticação (sessão do navegador)
- Certificados SSL corporativos
- URL de visualização não funciona para download direto

## ✅ Solução (Escolha uma)

### Opção 1: Download Manual (MAIS FÁCIL) ⭐

1. **Abra o SharePoint** no navegador:
   ```powershell
   python download_sharepoint_helper.py
   ```
   Ou abra manualmente a URL do SharePoint

2. **Baixe o arquivo**:
   - Clique em "Arquivo" → "Salvar como" → "Baixar uma cópia"
   - Ou clique com botão direito no arquivo → "Download"

3. **Execute o script com o caminho local**:
   ```powershell
   python sync_excel.py "$env:USERPROFILE\Downloads\CRQ VIRADA REDE.xlsx"
   ```

### Opção 2: Usar Caminho Fixo

Se você sempre baixa para a mesma pasta:

1. **Crie uma pasta** (ex: `C:\CRQMinAMin\excel\`)

2. **Baixe o arquivo sempre para essa pasta**

3. **Execute**:
   ```powershell
   python sync_excel.py "C:\CRQMinAMin\excel\CRQ VIRADA REDE.xlsx"
   ```

### Opção 3: Script Automatizado

Crie um script que baixa e processa:

```powershell
# download_e_sync.ps1
# 1. Abre SharePoint
Start-Process "https://vtalcorp.sharepoint.com/..."

# 2. Aguarda download manual
Write-Host "Baixe o arquivo e pressione Enter..."
Read-Host

# 3. Executa sincronização
python sync_excel.py "$env:USERPROFILE\Downloads\CRQ VIRADA REDE.xlsx"
```

## 📝 Exemplo Completo

```powershell
# Passo 1: Abrir assistente (opcional)
python download_sharepoint_helper.py

# Passo 2: Baixar arquivo manualmente do SharePoint
# (Arquivo → Salvar como → Baixar uma cópia)

# Passo 3: Executar sincronização
python sync_excel.py "$env:USERPROFILE\Downloads\CRQ VIRADA REDE.xlsx"
```

## 🔧 Por Que Não Funciona Automaticamente?

- **Navegador**: Você está logado, tem cookies de sessão
- **Script Python**: Não tem autenticação, não tem cookies
- **SharePoint**: Bloqueia downloads não autenticados por segurança

## 💡 Dica

Se você precisa fazer isso frequentemente, considere:
- Criar um atalho na área de trabalho
- Usar sempre o mesmo caminho de download
- Automatizar com PowerShell (veja Opção 3)
