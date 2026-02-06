# 📥 Como Obter URL de Download do SharePoint

## Problema
O SharePoint requer autenticação para downloads. A URL de visualização não funciona para download direto via script.

## Solução: Obter URL de Download Direto

### Método 1: Via Navegador (Mais Fácil)

1. **Abra o arquivo no SharePoint** usando a URL que você tem
2. **Clique com botão direito** no arquivo na lista de arquivos (não dentro do Excel Online)
3. **Selecione "Download"** ou **"Copiar link"**
4. **Se aparecer "Copiar link"**, cole o link e adicione `?download=1` no final
5. **Use essa URL** no script ou salve em um arquivo

### Método 2: Via Excel Online

1. **Abra o arquivo** no Excel Online (usando sua URL atual)
2. **Clique em "Arquivo"** (File) no canto superior esquerdo
3. **Selecione "Salvar como"** → **"Baixar uma cópia"**
4. **O arquivo será baixado** para sua pasta de Downloads
5. **Use o caminho local** ao executar o script:
   ```powershell
   python sync_excel.py "$env:USERPROFILE\Downloads\CRQ VIRADA REDE.xlsx"
   ```

### Método 3: Extrair URL de Download da Página

1. **Abra o arquivo** no SharePoint no navegador
2. **Pressione F12** para abrir as ferramentas de desenvolvedor
3. **Vá para a aba "Network"** (Rede)
4. **Clique em "Download"** no SharePoint
5. **Procure por uma requisição** que comece com o nome do arquivo
6. **Clique nela** e copie a URL completa da requisição
7. **Use essa URL** no script

### Método 4: Usar Caminho Local (Recomendado)

A forma mais simples e confiável:

1. **Baixe o arquivo manualmente** do SharePoint
2. **Salve em uma pasta conhecida** (ex: Downloads ou uma pasta do projeto)
3. **Execute o script com o caminho completo**:
   ```powershell
   python sync_excel.py "C:\Users\SeuUsuario\Downloads\CRQ VIRADA REDE.xlsx"
   ```

   Ou use variável de ambiente:
   ```powershell
   python sync_excel.py "$env:USERPROFILE\Downloads\CRQ VIRADA REDE.xlsx"
   ```

## Exemplo Prático

```powershell
# 1. Baixe o arquivo manualmente do SharePoint
# 2. Salve em: C:\Users\vt422276\Downloads\CRQ VIRADA REDE.xlsx

# 3. Execute:
python sync_excel.py "C:\Users\vt422276\Downloads\CRQ VIRADA REDE.xlsx"
```

## Dica: Automatizar Download

Se você precisa fazer isso frequentemente, considere:

1. **Criar uma pasta fixa** para o arquivo (ex: `C:\CRQMinAMin\excel\`)
2. **Baixar sempre para essa pasta**
3. **Usar caminho fixo no script** ou criar um atalho
