"""
Telegram Bot - Instagram Automation Pro
Sistema de notificações e comandos via Telegram
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger(__name__)


class TelegramBot:
    """Gerenciador de notificações via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if self.enabled:
            logger.info("✓ Telegram Bot ativado")
        else:
            logger.warning("⚠ Telegram Bot desativado (credenciais não encontradas)")
    
    def _send_message(self, text, parse_mode='HTML'):
        """Envia mensagem via Telegram"""
        if not self.enabled:
            logger.info(f"[Telegram Desativado] {text}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.debug("✓ Mensagem Telegram enviada")
                return True
            else:
                logger.error(f"Erro ao enviar Telegram: {response.json()}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem Telegram: {e}")
            return False
    
    # =============================================
    # NOTIFICAÇÕES DE SUCESSO
    # =============================================
    
    def notificar_post_sucesso(self, conta_username, tipo, video_id):
        """Notifica post realizado com sucesso"""
        text = f"""
✅ <b>POST REALIZADO</b>

👤 Conta: @{conta_username}
📺 Tipo: {tipo.upper()}
🎬 Vídeo: {video_id}
⏰ Horário: {datetime.now().strftime('%H:%M:%S')}
"""
        return self._send_message(text)
    
    # =============================================
    # ALERTAS DE PROBLEMAS
    # =============================================
    
    def alerta_critico(self, conta_username, problema, detalhes=""):
        """Alerta crítico (conta banida, desativada)"""
        text = f"""
🚨 <b>ALERTA CRÍTICO</b>

👤 Conta: @{conta_username}
⚠️ Problema: {problema}
📝 Detalhes: {detalhes}

⚡ <b>Ação Necessária: URGENTE!</b>
"""
        return self._send_message(text)
    
    def alerta_alto(self, conta_username, problema, acao_tomada):
        """Alerta alto (checkpoint, action block)"""
        text = f"""
⚠️ <b>ALERTA ALTO</b>

👤 Conta: @{conta_username}
⚠️ Problema: {problema}
✅ Ação Tomada: {acao_tomada}
"""
        return self._send_message(text)
    
    def alerta_medio(self, conta_username, problema, observacao):
        """Alerta médio (shadowban, queda de engajamento)"""
        text = f"""
🟡 <b>ALERTA MÉDIO</b>

👤 Conta: @{conta_username}
⚠️ Problema: {problema}
📝 Observação: {observacao}
"""
        return self._send_message(text)
    
    def alerta_proxy(self, proxy_id, problema):
        """Alerta de problema com proxy"""
        text = f"""
🌐 <b>ALERTA: PROXY</b>

🆔 Proxy ID: {proxy_id}
⚠️ Problema: {problema}
"""
        return self._send_message(text)
    
    # =============================================
    # RELATÓRIOS
    # =============================================
    
    def relatorio_diario(self, data):
        """Envia relatório diário completo"""
        text = f"""
📊 <b>RELATÓRIO DIÁRIO - {data['data']}</b>

<b>📈 POSTS:</b>
✅ Realizados: {data['posts_sucesso']}/{data['posts_total']} ({data['taxa_sucesso']}%)
❌ Falhas: {data['posts_falha']}

<b>👥 CONTAS:</b>
✅ Ativas: {data['contas_ativas']}/{data['contas_total']} ({data['percentual_ativas']}%)
⚠️ Com problemas: {data['contas_problemas']}

<b>🌐 PROXIES:</b>
✅ Funcionando: {data['proxies_ok']}/{data['proxies_total']}
❌ Offline: {data['proxies_falha']}

<b>⚡ PERFORMANCE:</b>
Tempo médio/post: {data['tempo_medio']}s
Uptime: {data['uptime']}%
"""
        return self._send_message(text)
    
    # =============================================
    # UTILITÁRIOS
    # =============================================
    
    def teste_conexao(self):
        """Testa conexão com Telegram"""
        text = """
🎉 <b>Teste de Conexão</b>

✅ Instagram Bot conectado!
✅ Notificações funcionando!

Você receberá alertas aqui.
"""
        return self._send_message(text)


# =============================================
# FUNÇÕES AUXILIARES
# =============================================

def enviar_mensagem_simples(mensagem):
    """Função helper para enviar mensagem rápida"""
    bot = TelegramBot()
    return bot._send_message(mensagem)


def testar_telegram():
    """Testa configuração do Telegram"""
    print("🔍 Testando Telegram Bot...")
    
    bot = TelegramBot()
    
    if not bot.enabled:
        print("❌ Telegram não configurado no .env")
        return False
    
    print(f"✓ Token: {bot.bot_token[:15]}...")
    print(f"✓ Chat ID: {bot.chat_id}")
    
    if bot.teste_conexao():
        print("✅ Mensagem de teste enviada!")
        print("✅ Verifique seu Telegram!")
        return True
    else:
        print("❌ Falha ao enviar mensagem")
        return False


if __name__ == "__main__":
    # Testa o bot quando executado diretamente
    testar_telegram()