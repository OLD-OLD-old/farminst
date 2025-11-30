# 🚀 Guia para Subir o Projeto no GitHub

## 📋 Pré-requisitos

### 1. Instalar o Git
Se você ainda não tem o Git instalado:

1. Baixe o Git em: https://git-scm.com/download/win
2. Instale seguindo o assistente (deixe as opções padrão)
3. Reinicie o terminal/PowerShell após a instalação

### 2. Criar conta no GitHub
1. Acesse: https://github.com
2. Crie uma conta (se ainda não tiver)
3. Faça login

---

## 🔧 Passo a Passo

### Passo 1: Inicializar o repositório Git

Abra o PowerShell no diretório do projeto e execute:

```bash
git init
```

### Passo 2: Adicionar arquivos ao Git

```bash
git add .
```

⚠️ **IMPORTANTE**: O arquivo `.gitignore` já está configurado para proteger seus arquivos sensíveis (senhas, sessões, etc.)

### Passo 3: Fazer o primeiro commit

```bash
git commit -m "Primeiro commit: Instagram Automation Pro"
```

### Passo 4: Criar repositório no GitHub

1. Acesse https://github.com
2. Clique no botão **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha:
   - **Repository name**: `farminst` (ou o nome que preferir)
   - **Description**: "Sistema de automação para Instagram"
   - **Visibilidade**: Escolha **Private** (recomendado) ou **Public**
   - **NÃO marque** "Initialize with README" (já temos arquivos)
5. Clique em **"Create repository"**

### Passo 5: Conectar o repositório local ao GitHub

Após criar o repositório, o GitHub mostrará comandos. Use estes comandos:

```bash
git remote add origin https://github.com/SEU_USUARIO/farminst.git
```

⚠️ **Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub**

### Passo 6: Enviar o código para o GitHub

```bash
git branch -M main
git push -u origin main
```

Se pedir autenticação:
- **Username**: Seu usuário do GitHub
- **Password**: Use um **Personal Access Token** (não sua senha normal)

#### Como criar um Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Clique em "Generate new token"
3. Dê um nome e selecione as permissões: `repo`
4. Copie o token gerado e use como senha

---

## ✅ Verificação

Após o push, acesse seu repositório no GitHub e verifique se todos os arquivos foram enviados corretamente.

---

## 🔒 Segurança

O arquivo `.gitignore` está configurado para **NÃO** enviar:
- ✅ Arquivos de configuração com senhas (`config/contas.json`, etc.)
- ✅ Sessões do Instagram (`sessoes/`)
- ✅ Arquivos `.env` com tokens
- ✅ Logs e cache
- ✅ Banco de dados

**NUNCA** faça commit de arquivos com informações sensíveis!

---

## 📝 Comandos Úteis

### Ver status dos arquivos
```bash
git status
```

### Ver o que será enviado
```bash
git status
```

### Fazer commit de mudanças futuras
```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

### Ver histórico de commits
```bash
git log
```

---

## 🆘 Problemas Comuns

### "Git não é reconhecido"
- Instale o Git: https://git-scm.com/download/win
- Reinicie o terminal após instalar

### "Authentication failed"
- Use um Personal Access Token ao invés da senha
- Verifique se o token tem permissão `repo`

### "Repository not found"
- Verifique se o nome do repositório está correto
- Verifique se você tem permissão de escrita no repositório

---

## 📚 Recursos Adicionais

- [Documentação do Git](https://git-scm.com/doc)
- [Guia do GitHub](https://guides.github.com/)
- [GitHub Desktop](https://desktop.github.com/) - Interface gráfica (opcional)

