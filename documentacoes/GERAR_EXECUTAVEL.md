# 📦 Gerar Executável do Sincronizador

Este guia explica como gerar um executável standalone (onefile) do script `sync_excel.py`.

## 🚀 Método Automático (Recomendado)

### Windows PowerShell

Execute o script fornecido:

```powershell
.\gerar_executavel.ps1
```

O script irá:
1. ✅ Verificar se Python está instalado
2. ✅ Instalar PyInstaller se necessário
3. ✅ Instalar dependências do projeto
4. ✅ Limpar builds anteriores
5. ✅ Gerar o executável `sync_excel.exe` na pasta `dist/`

## 🔧 Método Manual

### 1. Instalar Dependências

```bash
pip install -r requirements_sync.txt
pip install pyinstaller
```

### 2. Gerar Executável

```bash
pyinstaller --onefile --name sync_excel --console sync_excel.py
```

### 3. Executável Gerado

O arquivo `sync_excel.exe` estará em `dist/sync_excel.exe`

## 📋 Opções do PyInstaller

### Comando Completo (Recomendado)

```bash
pyinstaller --onefile --name sync_excel --console --clean --noconfirm sync_excel.py
```

**Parâmetros:**
- `--onefile`: Gera um único arquivo executável
- `--name sync_excel`: Nome do executável
- `--console`: Mantém o console visível (para logs)
- `--clean`: Limpa arquivos temporários antes de gerar
- `--noconfirm`: Não pede confirmação para sobrescrever

### Com Ícone (Opcional)

Se você tiver um arquivo `.ico`, adicione:

```bash
pyinstaller --onefile --name sync_excel --console --icon=icone.ico sync_excel.py
```

## 🎯 Como Usar o Executável

O executável funciona exatamente como o script Python:

```bash
# Modo individual (padrão)
.\dist\sync_excel.exe

# Modo bulk
.\dist\sync_excel.exe --mode bulk

# Com arquivo específico
.\dist\sync_excel.exe "C:\caminho\arquivo.xlsx"

# Modo bulk com arquivo
.\dist\sync_excel.exe --mode bulk "C:\caminho\arquivo.xlsx"
```

## ⚙️ Configuração da URL da API

O executável usa a URL padrão do backend no Netlify. Para alterar:

### Windows PowerShell

```powershell
$env:API_BASE_URL="http://localhost:3000"
.\dist\sync_excel.exe
```

### Windows CMD

```cmd
set API_BASE_URL=http://localhost:3000
dist\sync_excel.exe
```

## 📝 Notas Importantes

1. **Tamanho do Executável**: O executável pode ter entre 30-50 MB (inclui Python e todas as dependências)

2. **Primeira Execução**: A primeira execução pode ser mais lenta (descompactação interna)

3. **Antivírus**: Alguns antivírus podem marcar executáveis gerados por PyInstaller como suspeitos. Isso é um falso positivo comum.

4. **Dependências**: O executável é standalone e não requer Python instalado no computador de destino

5. **Logs**: Os logs continuam sendo salvos em `sync_excel.log` na mesma pasta do executável

## 🐛 Solução de Problemas

### Erro: "PyInstaller não encontrado"

```bash
pip install pyinstaller
```

### Erro: "Módulo não encontrado"

Adicione o módulo faltante com `--hidden-import`:

```bash
pyinstaller --onefile --hidden-import nome_do_modulo sync_excel.py
```

### Executável muito grande

Use `--exclude-module` para remover módulos desnecessários:

```bash
pyinstaller --onefile --exclude-module matplotlib --exclude-module numpy sync_excel.py
```

### Executável não funciona em outro computador

- Certifique-se de usar `--onefile`
- Teste em um computador limpo (sem Python instalado)
- Verifique se todas as dependências estão incluídas

## 📦 Distribuição

Para distribuir o executável:

1. Copie apenas o arquivo `dist/sync_excel.exe`
2. O usuário não precisa ter Python instalado
3. O executável funciona em qualquer Windows 10/11 (64-bit)

## 🔗 Referências

- [PyInstaller Documentation](https://pyinstaller.org/)
- [PyInstaller GitHub](https://github.com/pyinstaller/pyinstaller)
