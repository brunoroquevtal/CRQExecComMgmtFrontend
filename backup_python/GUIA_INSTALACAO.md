# 🚀 Guia de Instalação - Janela de Mudança TI
## Para Pessoas com Pouco Conhecimento Técnico

Este guia foi feito de forma bem simples, passo a passo, para você conseguir instalar a aplicação mesmo sem conhecimento técnico avançado.

**Não se preocupe!** Siga os passos na ordem e você conseguirá! 😊

---

## 📋 O QUE VOCÊ VAI PRECISAR

Antes de começar, verifique se você tem:

- ✅ Um computador com Windows
- ✅ Conexão com a internet
- ✅ Um arquivo de backup (se você está recebendo dados de outra pessoa)

---

## 🔧 PASSO 1: Verificar se o Python está instalado

### O que é Python?
Python é um programa que precisa estar instalado no seu computador para a aplicação funcionar.

### Como verificar:

1. **Abra o Menu Iniciar** (botão do Windows no canto inferior esquerdo)

2. **Digite "cmd"** na busca e clique em "Prompt de Comando" ou "CMD"

3. **Uma janela preta vai abrir** (isso é normal!)

4. **Digite exatamente isso** (copie e cole):
   ```
   python --version
   ```
   Pressione ENTER

5. **Veja o que aparece:**
   - ✅ **Se aparecer algo como "Python 3.8" ou "Python 3.9"**: Ótimo! O Python já está instalado. Pule para o Passo 2.
   - ❌ **Se aparecer "não é reconhecido" ou "não encontrado"**: Você precisa instalar o Python. Continue lendo abaixo.

---

## 📥 PASSO 1.1: Instalar o Python (SE NÃO ESTIVER INSTALADO)

### Como instalar:

1. **Abra seu navegador** (Chrome, Edge, Firefox, etc.)

2. **Acesse este site**: https://www.python.org/downloads/

3. **Clique no botão grande amarelo** que diz "Download Python 3.x.x" (o número pode variar)

4. **O arquivo vai baixar** (pode levar alguns minutos)

5. **Abra o arquivo baixado** (geralmente fica na pasta "Downloads")

6. **Uma janela de instalação vai abrir**:
   - ⚠️ **MUITO IMPORTANTE**: Marque a caixinha que diz **"Add Python to PATH"** ou **"Adicionar Python ao PATH"**
   - Clique em **"Install Now"** ou **"Instalar Agora"**
   - Aguarde a instalação terminar (pode levar alguns minutos)

7. **Quando terminar, clique em "Close"** ou "Fechar"

8. **Feche e abra novamente o Prompt de Comando** (a janela preta) e teste novamente o comando do Passo 1

---

## 📁 PASSO 2: Obter os Arquivos da Aplicação

### O que você precisa fazer:

Você precisa ter uma pasta com todos os arquivos da aplicação. Isso pode vir de duas formas:

**Opção A: Você recebeu uma pasta completa**
- Alguém te passou uma pasta chamada "CRQMinAMin" ou similar
- Copie essa pasta para um local fácil de encontrar, como:
  - Área de Trabalho (Desktop)
  - Ou dentro de "Documentos"

**Opção B: Você tem um arquivo ZIP**
- Se você recebeu um arquivo ZIP (compactado):
  - Clique com o botão direito no arquivo
  - Escolha "Extrair Tudo" ou "Extract All"
  - Escolha onde extrair (sugestão: Área de Trabalho)
  - Clique em "Extrair"

### Onde colocar a pasta?
- Sugestão: Coloque na **Área de Trabalho** ou em **Documentos**
- Exemplo: `C:\Users\SeuNome\Desktop\CRQMinAMin`

---

## 📦 PASSO 3: Instalar os Programas Necessários

### O que vamos fazer?
Vamos instalar os programas adicionais que a aplicação precisa para funcionar.

### Passo a passo:

1. **Abra o Prompt de Comando novamente** (como no Passo 1)

2. **Vamos navegar até a pasta da aplicação**:
   
   Digite o comando abaixo, mas **SUBSTITUA** o caminho pelo local onde você colocou a pasta:
   ```
   cd C:\Users\SeuNome\Desktop\CRQMinAMin
   ```
   
   **Exemplo real** (se seu nome de usuário for "João" e a pasta estiver na Área de Trabalho):
   ```
   cd C:\Users\João\Desktop\CRQMinAMin
   ```
   
   Pressione ENTER

3. **Se você não souber o caminho exato**, faça assim:
   - Abra a pasta da aplicação no Windows Explorer
   - Clique na barra de endereço (onde mostra o caminho)
   - Copie o caminho completo
   - No Prompt de Comando, digite `cd ` (com espaço no final)
   - Cole o caminho que você copiou
   - Pressione ENTER

4. **Agora vamos instalar os programas necessários**:
   
   Digite exatamente isso:
   ```
   pip install -r requirements.txt
   ```
   
   Pressione ENTER

5. **Aguarde a instalação** (pode levar de 2 a 10 minutos, dependendo da sua internet)
   - Você verá várias linhas aparecendo na tela
   - Isso é normal! Significa que está instalando
   - **Não feche a janela!**

6. **Quando terminar**, você verá algo como "Successfully installed" ou mensagens de sucesso
   - Se aparecer algum erro, veja a seção "Problemas Comuns" no final deste guia

---

## 🚀 PASSO 4: Abrir a Aplicação

### Agora vamos iniciar a aplicação:

1. **No Prompt de Comando** (a janela preta), certifique-se de estar na pasta da aplicação
   - Se não estiver, repita o Passo 3.2 (navegar até a pasta)

2. **Digite este comando**:
   ```
   streamlit run app.py
   ```
   
   Pressione ENTER

3. **Aguarde alguns segundos** (10-30 segundos)

4. **Você verá uma mensagem** como esta:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   ```

5. **Automaticamente, seu navegador vai abrir** com a aplicação
   - Se não abrir automaticamente:
     - Abra seu navegador (Chrome, Edge, etc.)
     - Digite na barra de endereço: `http://localhost:8501`
     - Pressione ENTER

6. **A aplicação está funcionando!** 🎉
   - Você verá uma tela de login
   - **NÃO FECHE a janela preta do Prompt de Comando!** Ela precisa ficar aberta enquanto você usa a aplicação

---

## 🔐 PASSO 5: Fazer o Primeiro Login

1. **Na tela de login que abriu no navegador**, você verá campos para:
   - **Usuário**
   - **Senha**

2. **Digite as informações padrão**:
   - **Usuário**: `admin`
   - **Senha**: `admin`

3. **Clique no botão de Login** ou pressione ENTER

4. **Você entrará na aplicação!**

5. ⚠️ **IMPORTANTE**: Depois de entrar, vá em **Configurações** e altere a senha padrão!

---

## 📥 PASSO 6: Importar Dados de Outra Máquina (SE VOCÊ TEM UM ARQUIVO DE BACKUP)

### O que é um arquivo de backup?
É um arquivo que contém todos os dados que foram salvos na máquina anterior. Geralmente tem um nome como:
- `backup_janela_mudanca_20240130_143000.json`
- Ou algo similar com `.json` no final

### Como importar:

1. **Faça login na aplicação** (Passo 5)

2. **No menu lateral esquerdo**, clique em **"Configurações"**

3. **Role a página para baixo** até encontrar a seção:
   - **"🔄 Transferência de Dados entre Máquinas"**

4. **No lado direito** (onde diz "📥 Importar Dados"):
   - Clique em **"Selecione o arquivo de backup (.json)"**
   - Uma janela vai abrir para você escolher o arquivo
   - Navegue até onde está o arquivo de backup
   - Clique no arquivo
   - Clique em "Abrir"

5. **Depois de escolher o arquivo**:
   - Clique no botão **"📥 Importar Dados do Backup"**

6. **Aguarde alguns segundos** (pode levar 10-30 segundos dependendo do tamanho)

7. **Você verá uma mensagem de sucesso**:
   - "✅ Dados importados com sucesso!"
   - A página vai recarregar automaticamente

8. **Pronto!** Os dados foram importados e você pode começar a trabalhar! 🎉

---

## ✅ VERIFICAÇÃO: Está Tudo Funcionando?

Depois de instalar, verifique se:

- ✅ A aplicação abre no navegador quando você digita `streamlit run app.py`
- ✅ Você consegue fazer login com `admin` / `admin`
- ✅ Você vê o Dashboard (tela principal com gráficos e informações)
- ✅ Se importou dados, eles aparecem corretamente

**Se tudo isso funcionar, está tudo certo!** 🎉

---

## 🔄 COMO TRANSFERIR DADOS ENTRE MÁQUINAS

### Quando você terminar seu turno (Máquina 1):

1. **Faça login na aplicação**

2. **Vá em Configurações** (menu lateral)

3. **Na seção "🔄 Transferência de Dados entre Máquinas"**:
   - Clique em **"💾 Exportar Todos os Dados"**
   - Aguarde alguns segundos
   - Clique em **"📥 Baixar Arquivo de Backup"**
   - O arquivo será baixado (geralmente na pasta "Downloads")

4. **Salve o arquivo em um lugar seguro**:
   - Pendrive
   - Email para você mesmo
   - Rede compartilhada
   - Qualquer lugar onde a próxima pessoa possa acessar

### Quando outra pessoa começar o turno (Máquina 2):

1. **Siga os Passos 1 a 5** deste guia (se ainda não instalou)

2. **Siga o Passo 6** para importar o arquivo de backup que você salvou

3. **Pronto!** A pessoa pode continuar trabalhando normalmente

---

## 🛠️ PROBLEMAS COMUNS E SOLUÇÕES

### ❌ Problema: "Python não é reconhecido"

**O que significa?** O computador não encontrou o Python instalado.

**Solução:**
1. Volte ao **Passo 1.1** e instale o Python
2. **MUITO IMPORTANTE**: Marque a caixinha "Add Python to PATH" durante a instalação
3. Depois de instalar, **feche e abra novamente** o Prompt de Comando
4. Teste novamente

---

### ❌ Problema: "pip não é reconhecido"

**O que significa?** O pip (instalador de programas Python) não foi encontrado.

**Solução:**
No Prompt de Comando, tente este comando em vez do outro:
```
python -m pip install -r requirements.txt
```

---

### ❌ Problema: "Erro ao instalar dependências"

**O que significa?** Algum programa não conseguiu ser instalado.

**Soluções:**
1. **Verifique sua internet** - precisa estar conectado
2. **Tente novamente** - às vezes é só um problema temporário
3. **Se continuar dando erro**, copie a mensagem de erro completa e peça ajuda para alguém técnico

---

### ❌ Problema: "Porta 8501 já está em uso"

**O que significa?** A aplicação já está rodando em outra janela.

**Solução:**
1. **Feche todas as janelas do Prompt de Comando** que estão rodando a aplicação
2. **Feche o navegador** onde a aplicação estava aberta
3. **Aguarde 10 segundos**
4. **Tente abrir novamente** (Passo 4)

---

### ❌ Problema: "A aplicação não abre no navegador"

**Solução:**
1. **Não feche a janela preta** do Prompt de Comando
2. **Abra seu navegador manualmente** (Chrome, Edge, etc.)
3. **Digite na barra de endereço**: `http://localhost:8501`
4. Pressione ENTER

---

### ❌ Problema: "Erro ao importar dados"

**O que significa?** O arquivo de backup pode estar corrompido ou incompleto.

**Soluções:**
1. **Verifique se o arquivo está completo** - não foi cortado durante o download
2. **Tente exportar novamente** da máquina original
3. **Certifique-se de que o arquivo termina com `.json`**

---

### ❌ Problema: "Não consigo encontrar a pasta"

**Solução:**
1. **No Windows Explorer**, use a busca (barra de pesquisa no canto superior direito)
2. **Digite**: `CRQMinAMin`
3. O Windows vai encontrar a pasta para você

---

## 💡 DICAS IMPORTANTES

1. **Não feche a janela preta** (Prompt de Comando) enquanto estiver usando a aplicação
   - Ela precisa ficar aberta para a aplicação funcionar
   - Se fechar, a aplicação para de funcionar

2. **Sempre exporte os dados** antes de encerrar seu turno
   - Isso garante que a próxima pessoa tenha todos os dados atualizados

3. **Altere a senha padrão** após o primeiro login
   - Vá em Configurações e mude a senha

4. **Se tiver dúvidas**, anote o erro exato que apareceu e peça ajuda

5. **Mantenha o arquivo de backup em segurança**
   - É sua cópia de segurança de todos os dados

---

## 📞 PRECISA DE AJUDA?

Se você seguiu todos os passos e ainda está com problemas:

1. **Anote exatamente** qual erro apareceu
2. **Copie a mensagem de erro** completa
3. **Peça ajuda** para alguém com mais conhecimento técnico
4. **Mostre este guia** para a pessoa que vai te ajudar

---

## 🎉 PARABÉNS!

Se você chegou até aqui e a aplicação está funcionando, você conseguiu! 🎊

Agora você pode usar a aplicação normalmente. Lembre-se:
- ✅ Sempre exporte os dados no final do turno
- ✅ Mantenha a janela preta aberta enquanto usa a aplicação
- ✅ Altere a senha padrão

**Bom trabalho!** 😊

---

**Última atualização**: Janeiro 2026
