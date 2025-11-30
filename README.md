# 🤖 Instagram Automation Pro

Sistema de automação para Instagram com recursos avançados de humanização, detecção de bloqueios e agendamento de posts.

## ✨ Funcionalidades

- 📅 Agendamento automático de posts
- 🤖 Humanização de ações para evitar detecção
- 🛡️ Detecção de bloqueios e ações suspeitas
- 📱 Integração com Telegram para notificações
- 🔄 Sistema de proxies
- 📊 Banco de dados para gerenciamento de contas

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/farminst.git
cd farminst
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Configure os arquivos de configuração:
```bash
# Copie os arquivos de exemplo
cp config/contas.json.example config/contas.json
cp config/legendas.json.example config/legendas.json
cp config/hashtags.json.example config/hashtags.json

# Edite os arquivos com suas informações
```

5. Execute o sistema:
```bash
python app/main.py
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Telegram (opcional)
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Humanização
HUMANIZE_LEVEL=alto
```

### Arquivos de Configuração

- `config/contas.json` - Contas do Instagram
- `config/legendas.json` - Legendas para posts
- `config/hashtags.json` - Grupos de hashtags
- `config/horarios.json` - Horários de postagem

⚠️ **IMPORTANTE**: Nunca commite arquivos com informações sensíveis! Use os arquivos `.example` como base.

## 📁 Estrutura do Projeto

```
farminst/
├── app/              # Código principal
│   ├── main.py      # Orquestrador principal
│   ├── poster.py    # Sistema de postagem
│   ├── scheduler.py # Agendamento
│   └── ...
├── config/          # Arquivos de configuração
├── database/        # Modelos e migrações do banco
├── scripts/         # Scripts de teste
└── logs/           # Logs do sistema
```

## 🔒 Segurança

- ⚠️ Mantenha seus arquivos de configuração privados
- ⚠️ Nunca compartilhe senhas ou tokens
- ⚠️ Use o modo privado no GitHub para repositórios com código sensível

## 📝 Licença

Este projeto é de uso pessoal. Use por sua conta e risco.

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## ⚠️ Aviso Legal

Este software é apenas para fins educacionais. O uso de automação pode violar os Termos de Serviço do Instagram. Use por sua conta e risco.

