# 🔒 Solução para Erro de Certificado SSL

## 🔴 Problema

Ao executar o sincronizador, você pode encontrar o seguinte erro:

```
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: self-signed certificate in certificate chain'))
```

## 🔍 Causa

Este erro geralmente ocorre em ambientes corporativos onde:
- Há um proxy ou firewall interceptando conexões HTTPS
- Certificados SSL autoassinados são usados pela infraestrutura corporativa
- O certificado do Netlify não é confiável pela cadeia de certificados do sistema

## ✅ Solução

### Opção 1: Desabilitar Verificação SSL (Recomendado para Ambientes Corporativos)

**PowerShell:**
```powershell
$env:DISABLE_SSL_VERIFY='true'
python sync_excel.py
```

**Windows CMD:**
```cmd
set DISABLE_SSL_VERIFY=true
python sync_excel.py
```

**Linux/Mac:**
```bash
export DISABLE_SSL_VERIFY=true
python sync_excel.py
```

### Opção 2: Usar Variável SSL_VERIFY

**PowerShell:**
```powershell
$env:SSL_VERIFY='false'
python sync_excel.py
```

**Windows CMD:**
```cmd
set SSL_VERIFY=false
python sync_excel.py
```

**Linux/Mac:**
```bash
export SSL_VERIFY=false
python sync_excel.py
```

### Opção 3: Configurar Permanente (PowerShell Profile)

Para não precisar definir toda vez, adicione ao seu perfil do PowerShell:

```powershell
# Editar perfil
notepad $PROFILE

# Adicionar linha:
$env:DISABLE_SSL_VERIFY='true'
```

## ⚠️ Avisos de Segurança

- **Desabilitar verificação SSL reduz a segurança da conexão**
- Use apenas em ambientes confiáveis (rede corporativa)
- O script mostrará um aviso quando SSL estiver desabilitado
- Em produção pública, mantenha SSL habilitado

## 🔧 Verificação

Após definir a variável, o script deve:
1. Mostrar aviso: `AVISO: Verificação SSL desabilitada`
2. Conectar com sucesso ao backend
3. Processar o arquivo Excel normalmente

## 📝 Notas

- A variável de ambiente é válida apenas para a sessão atual do terminal
- Para o executável (.exe), defina a variável antes de executar
- O log mostrará quando SSL está desabilitado

## 🐛 Ainda com Problemas?

Se o erro persistir mesmo com SSL desabilitado:

1. **Verifique a URL do backend:**
   ```powershell
   echo $env:API_BASE_URL
   ```

2. **Teste a conexão manualmente:**
   ```powershell
   Invoke-WebRequest -Uri "https://crqcommunidationbackend.netlify.app/.netlify/functions/api/health" -SkipCertificateCheck
   ```

3. **Verifique firewall/proxy corporativo:**
   - Contate o suporte de TI
   - Pode ser necessário configurar proxy no Python
