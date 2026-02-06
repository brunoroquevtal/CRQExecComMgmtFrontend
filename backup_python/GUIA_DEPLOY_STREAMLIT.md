# 🚀 Guia de Deploy no Streamlit Cloud
## Passo a Passo Completo

Este guia vai te ajudar a publicar sua aplicação no Streamlit Cloud de forma gratuita e acessível de qualquer lugar!

---

## 📋 O QUE VOCÊ VAI PRECISAR

Antes de começar, você precisa ter:

- ✅ Uma conta no **GitHub** (gratuita)
- ✅ Uma conta no **Streamlit Cloud** (gratuita)
- ✅ Todos os arquivos do projeto na sua máquina
- ✅ Conexão com a internet

---

## 🔧 PASSO 1: Criar Conta no GitHub (SE AINDA NÃO TEM)

### O que é GitHub?
GitHub é um site onde você pode guardar seu código na "nuvem" (internet). O Streamlit Cloud precisa que seu código esteja lá.

### Como criar conta:

1. **Acesse**: https://github.com
2. **Clique em "Sign up"** (Cadastrar) no canto superior direito
3. **Preencha os dados**:
   - Email
   - Senha
   - Nome de usuário (escolha um nome único)
4. **Verifique seu email** (GitHub vai enviar um email de confirmação)
5. **Pronto!** Sua conta está criada

---

## 📁 PASSO 2: Criar um Repositório no GitHub

### O que é um repositório?
É como uma "pasta" no GitHub onde você vai guardar todos os arquivos do seu projeto.

### Como criar:

1. **Faça login no GitHub** (https://github.com)

2. **No canto superior direito**, clique no ícone **"+"** e escolha **"New repository"** (Novo repositório)

3. **Preencha as informações**:
   - **Repository name** (Nome do repositório): 
     - Digite: `CRQMinAMin` (ou outro nome que você preferir)
   - **Description** (Descrição - opcional):
     - Digite: "Aplicação para gerenciamento de janelas de mudança de TI"
   - **Público ou Privado**:
     - Escolha **"Public"** (público) - é gratuito e funciona melhor com Streamlit Cloud
     - Ou **"Private"** (privado) - se quiser manter o código secreto
   - **NÃO marque** "Add a README file" (vamos fazer isso depois)
   - **NÃO marque** "Add .gitignore" 
   - **NÃO marque** "Choose a license"

4. **Clique no botão verde** **"Create repository"** (Criar repositório)

5. **Pronto!** Seu repositório foi criado! 🎉

---

## 💻 PASSO 3: Instalar o Git na Sua Máquina

### O que é Git?
Git é um programa que permite enviar seus arquivos para o GitHub.

### Como instalar:

1. **Acesse**: https://git-scm.com/download/win

2. **O download vai começar automaticamente** (arquivo .exe)

3. **Abra o arquivo baixado** e instale:
   - Clique em **"Next"** várias vezes
   - Use as opções padrão (não precisa mudar nada)
   - Clique em **"Install"**
   - Aguarde a instalação terminar

4. **Clique em "Finish"**

5. **Pronto!** O Git está instalado

---

## 📤 PASSO 4: Enviar Seus Arquivos para o GitHub

### Agora vamos enviar todos os arquivos do projeto para o GitHub:

### 4.1. Abrir o Git Bash ou Prompt de Comando

**Opção A - Git Bash (Recomendado):**
- Clique com botão direito na pasta do projeto
- Escolha **"Git Bash Here"**

**Opção B - Prompt de Comando:**
- Abra o Prompt de Comando (cmd)
- Navegue até a pasta do projeto usando `cd`

### 4.2. Configurar o Git (SE FOR A PRIMEIRA VEZ)

Digite estes comandos (substitua com seus dados):

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

Pressione ENTER após cada comando.

### 4.3. Inicializar o Repositório Git

Na pasta do projeto, digite:

```bash
git init
```

Pressione ENTER.

### 4.4. Adicionar Todos os Arquivos

Digite:

```bash
git add .
```

Pressione ENTER.

**⚠️ IMPORTANTE**: Antes de continuar, vamos criar um arquivo `.gitignore` para não enviar arquivos desnecessários:

Crie um arquivo chamado `.gitignore` na pasta do projeto com este conteúdo:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.db
*.db-journal
*.sqlite
*.sqlite3
.env
.venv
venv/
ENV/
env/
.DS_Store
*.log
data/
db/
```

**Depois de criar o .gitignore**, execute novamente:

```bash
git add .
```

### 4.5. Fazer o Primeiro Commit

Digite:

```bash
git commit -m "Primeira versão da aplicação"
```

Pressione ENTER.

### 4.6. Conectar ao Repositório do GitHub

**Primeiro, pegue a URL do seu repositório:**
1. Vá para a página do seu repositório no GitHub
2. Clique no botão verde **"Code"**
3. Copie a URL que aparece (algo como: `https://github.com/seu-usuario/CRQMinAMin.git`)

**Agora, no terminal, digite** (substitua pela URL que você copiou):

```bash
git remote add origin https://github.com/seu-usuario/CRQMinAMin.git
```

Pressione ENTER.

### 4.7. Enviar os Arquivos

Digite:

```bash
git branch -M main
git push -u origin main
```

Pressione ENTER.

**Se pedir login:**
- Digite seu **nome de usuário** do GitHub
- Digite sua **senha** (ou um **Personal Access Token** - veja abaixo)

### 4.8. Criar Personal Access Token (SE PEDIR AUTENTICAÇÃO)

Se o GitHub pedir autenticação:

1. **Acesse**: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. **Dê um nome**: "Streamlit Deploy"
4. **Marque a opção**: `repo` (todas as sub-opções)
5. **Clique em "Generate token"** (gerar token)
6. **COPIE O TOKEN** (você só verá ele uma vez!)
7. **Use esse token como senha** quando o Git pedir

### 4.9. Verificar se Funcionou

1. **Atualize a página do seu repositório no GitHub**
2. **Você deve ver todos os arquivos** aparecendo lá!
3. **Se aparecer, está funcionando!** ✅

---

## ☁️ PASSO 5: Criar Conta no Streamlit Cloud

### O que é Streamlit Cloud?
É um serviço gratuito que hospeda sua aplicação Streamlit na internet, permitindo acesso de qualquer lugar.

### Como criar conta:

1. **Acesse**: https://streamlit.io/cloud

2. **Clique em "Get started"** ou **"Sign up"**

3. **Escolha "Sign in with GitHub"** (Entrar com GitHub)
   - Isso conecta sua conta do GitHub ao Streamlit Cloud

4. **Autorize o Streamlit** a acessar seus repositórios
   - Clique em **"Authorize streamlit"** ou similar

5. **Pronto!** Você está logado no Streamlit Cloud! 🎉

---

## 🚀 PASSO 6: Fazer o Deploy da Aplicação

### Agora vamos publicar sua aplicação:

1. **No Streamlit Cloud**, você verá uma tela com opções

2. **Clique em "New app"** (Nova aplicação) ou **"Deploy an app"**

3. **Preencha os campos**:

   **a) Repository (Repositório):**
   - Clique no campo
   - Escolha seu repositório: `seu-usuario/CRQMinAMin`
   - Ou digite: `seu-usuario/CRQMinAMin`

   **b) Branch (Ramo):**
   - Deixe como está: `main` (ou `master`)

   **c) Main file path (Caminho do arquivo principal):**
   - **MUITO IMPORTANTE**: Digite exatamente: `app.py`
   - Este é o arquivo principal da sua aplicação

   **d) App URL (URL da aplicação - opcional):**
   - Você pode deixar em branco ou escolher um nome
   - Exemplo: `crq-min-a-min` (sem espaços ou caracteres especiais)
   - A URL final será: `https://crq-min-a-min.streamlit.app`

4. **Clique em "Deploy"** (Publicar)

5. **Aguarde alguns minutos** (2-5 minutos)
   - Você verá uma barra de progresso
   - O Streamlit está instalando tudo e preparando sua aplicação

6. **Quando terminar**, você verá:
   - ✅ "Your app is live!" (Sua aplicação está no ar!)
   - Um link para acessar sua aplicação

7. **Clique no link** ou no botão **"View app"** (Ver aplicação)

8. **Pronto!** Sua aplicação está publicada! 🎉🎉🎉

---

## ✅ VERIFICAÇÃO: Está Funcionando?

Depois do deploy, verifique:

- ✅ A aplicação abre no navegador quando você clica no link
- ✅ Você vê a tela de login
- ✅ Você consegue fazer login com `admin` / `admin`
- ✅ O Dashboard aparece corretamente

**Se tudo isso funcionar, está tudo certo!** 🎉

---

## 🔄 ATUALIZAR A APLICAÇÃO (Quando Fizer Mudanças)

Sempre que você fizer mudanças no código e quiser atualizar a aplicação publicada:

### 1. Fazer as mudanças nos arquivos locais

### 2. No terminal (Git Bash ou Prompt de Comando), na pasta do projeto:

```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

### 3. O Streamlit Cloud detecta automaticamente as mudanças

- Aguarde 1-2 minutos
- A aplicação será atualizada automaticamente!

---

## ⚙️ CONFIGURAÇÕES IMPORTANTES

### Arquivo Principal

O Streamlit Cloud precisa saber qual arquivo é o principal. No campo **"Main file path"**, sempre use:

```
app.py
```

### Requirements.txt

Certifique-se de que o arquivo `requirements.txt` está na raiz do projeto e contém todas as dependências:

```
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.0.0
plotly>=5.17.0
python-dateutil>=2.8.2
pyperclip>=1.8.2
```

### Banco de Dados

⚠️ **ATENÇÃO**: O banco de dados SQLite funciona no Streamlit Cloud, mas os dados são **temporários** e podem ser perdidos quando a aplicação reiniciar.

**Soluções:**
- Use a funcionalidade de **Exportar/Importar** dados regularmente
- Ou considere usar um banco de dados na nuvem (mais avançado)

---

## 🛠️ PROBLEMAS COMUNS E SOLUÇÕES

### ❌ Problema: "Repository not found"

**O que significa?** O Streamlit não conseguiu encontrar seu repositório.

**Soluções:**
1. Verifique se o repositório está **público** (ou você deu permissão ao Streamlit)
2. Verifique se digitou o nome corretamente: `usuario/repositorio`
3. Certifique-se de que fez push dos arquivos para o GitHub

---

### ❌ Problema: "Main file path not found"

**O que significa?** O arquivo `app.py` não foi encontrado.

**Soluções:**
1. Verifique se o arquivo `app.py` está na **raiz** do repositório (não dentro de uma pasta)
2. Verifique se o nome está correto: `app.py` (com letras minúsculas)
3. Certifique-se de que fez commit e push do arquivo

---

### ❌ Problema: "Failed to install dependencies"

**O que significa?** Alguma dependência não foi instalada corretamente.

**Soluções:**
1. Verifique se o arquivo `requirements.txt` está na raiz do projeto
2. Verifique se todas as dependências estão listadas
3. Tente fazer deploy novamente

---

### ❌ Problema: "App crashed" ou "Error"

**O que significa?** A aplicação encontrou um erro ao iniciar.

**Soluções:**
1. **Veja os logs de erro**:
   - No Streamlit Cloud, clique em **"Manage app"** (Gerenciar aplicação)
   - Clique em **"Logs"** para ver o erro
2. **Verifique se todos os módulos estão presentes**:
   - Certifique-se de que a pasta `modules/` foi enviada para o GitHub
   - Verifique se o arquivo `config.py` está presente
3. **Teste localmente primeiro**:
   - Execute `streamlit run app.py` na sua máquina
   - Se funcionar localmente, deve funcionar no Streamlit Cloud

---

### ❌ Problema: "Permission denied" ao fazer push

**O que significa?** Você não tem permissão para enviar arquivos.

**Soluções:**
1. Verifique se está usando o **Personal Access Token** correto
2. Verifique se o token tem permissão `repo`
3. Tente criar um novo token

---

## 💡 DICAS IMPORTANTES

1. **Sempre teste localmente primeiro**
   - Execute `streamlit run app.py` na sua máquina
   - Se funcionar localmente, deve funcionar no Streamlit Cloud

2. **Mantenha o repositório organizado**
   - Não envie arquivos desnecessários (use `.gitignore`)
   - Mantenha a estrutura de pastas limpa

3. **Faça commits frequentes**
   - Sempre que fizer uma mudança importante, faça commit e push
   - Use mensagens descritivas: "Adiciona funcionalidade X"

4. **Monitore os logs**
   - Se algo der errado, veja os logs no Streamlit Cloud
   - Eles mostram exatamente o que aconteceu

5. **Backup dos dados**
   - Lembre-se que o banco de dados no Streamlit Cloud é temporário
   - Use a funcionalidade de Exportar regularmente

---

## 📞 PRECISA DE AJUDA?

Se você seguiu todos os passos e ainda está com problemas:

1. **Veja os logs de erro** no Streamlit Cloud
2. **Verifique se todos os arquivos foram enviados** para o GitHub
3. **Teste localmente** para garantir que funciona
4. **Peça ajuda** para alguém com mais conhecimento técnico
5. **Consulte a documentação oficial**:
   - Streamlit Cloud: https://docs.streamlit.io/streamlit-community-cloud
   - GitHub: https://docs.github.com

---

## 🎉 PARABÉNS!

Se você chegou até aqui e sua aplicação está funcionando no Streamlit Cloud, você conseguiu! 🎊

Agora sua aplicação está:
- ✅ Acessível de qualquer lugar
- ✅ Sempre disponível (24/7)
- ✅ Gratuita
- ✅ Fácil de atualizar

**Bom trabalho!** 😊

---

**Última atualização**: Janeiro 2026
