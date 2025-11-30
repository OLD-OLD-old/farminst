"""
Detector - Instagram Automation Pro
Detecta bans, shadowbans, checkpoints e outros problemas

CRÍTICO: Detectar problemas cedo evita piora da situação!
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Detector:
    """Classe responsável por detectar problemas nas contas"""
    
    def __init__(self, telegram_bot=None):
        """
        Inicializa o detector
        
        Args:
            telegram_bot: Instância do TelegramBot para notificações
        """
        self.telegram_bot = telegram_bot
        logger.info("✓ Detector de problemas inicializado")
    
    # =============================================
    # DETECÇÃO DE ACTION BLOCK
    # =============================================
    
    def detectar_action_block(self, erro_mensagem):
        """
        Detecta se a conta recebeu Action Block
        
        Mensagens típicas:
        - "Try again later"
        - "Action Blocked"
        - "We restrict certain content and actions"
        
        Args:
            erro_mensagem: Mensagem de erro retornada pela API
            
        Returns:
            dict com informações do problema ou None
        """
        if not erro_mensagem:
            return None
        
        # Palavras-chave que indicam action block
        keywords_action_block = [
            'try again later',
            'action blocked',
            'action block',
            'temporarily blocked',
            'temporarily restricted',
            'we restrict certain',
            'spam'
        ]
        
        erro_lower = erro_mensagem.lower()
        
        for keyword in keywords_action_block:
            if keyword in erro_lower:
                logger.warning(f"⚠️ ACTION BLOCK detectado: {erro_mensagem}")
                
                return {
                    'tipo': 'action_block',
                    'severidade': 'alta',
                    'mensagem': 'Action Block detectado',
                    'detalhes': erro_mensagem,
                    'acao_recomendada': 'Pausar conta por 24-48 horas',
                    'pausar_ate': datetime.now() + timedelta(hours=24)
                }
        
        return None
    
    # =============================================
    # DETECÇÃO DE CHECKPOINT
    # =============================================
    
    def detectar_checkpoint(self, response_data):
        """
        Detecta se a conta precisa passar por checkpoint
        
        Checkpoint = Instagram pede verificação adicional (confirmar email, SMS, etc)
        
        Args:
            response_data: Dados da resposta da API
            
        Returns:
            dict com informações do problema ou None
        """
        if not response_data:
            return None
        
        # Verifica se há indicação de checkpoint
        if isinstance(response_data, dict):
            if response_data.get('checkpoint_required'):
                logger.error(f"🚨 CHECKPOINT detectado!")
                
                checkpoint_url = response_data.get('checkpoint_url', '')
                
                return {
                    'tipo': 'checkpoint',
                    'severidade': 'critica',
                    'mensagem': 'Checkpoint Required',
                    'detalhes': f'Acesse: {checkpoint_url}',
                    'acao_recomendada': 'Resolver checkpoint manualmente',
                    'checkpoint_url': checkpoint_url,
                    'pausar_ate': None  # Pausa indefinida até resolver
                }
        
        return None
    
    # =============================================
    # DETECÇÃO DE SHADOWBAN
    # =============================================
    
    def detectar_shadowban(self, client, ultima_hashtag_usada):
        """
        Detecta se a conta está em shadowban
        
        Shadowban = Posts não aparecem em hashtags
        
        Método: Posta com hashtag única e verifica se aparece na busca
        
        Args:
            client: Cliente Instagram
            ultima_hashtag_usada: Última hashtag usada no post
            
        Returns:
            dict com informações do problema ou None
        """
        try:
            if not ultima_hashtag_usada:
                return None
            
            logger.info(f"🔍 Verificando shadowban com hashtag: {ultima_hashtag_usada}")
            
            # Busca pela hashtag
            # (Implementação real seria buscar posts recentes com essa hashtag)
            # Por enquanto, retornamos None (não detectado)
            
            # TODO: Implementar busca real quando tiver acesso ao Instagram
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao detectar shadowban: {e}")
            return None
    
    # =============================================
    # DETECÇÃO DE CONTA DESATIVADA
    # =============================================
    
    def detectar_conta_desativada(self, erro_mensagem):
        """
        Detecta se a conta foi desativada/banida permanentemente
        
        Args:
            erro_mensagem: Mensagem de erro
            
        Returns:
            dict com informações do problema ou None
        """
        if not erro_mensagem:
            return None
        
        keywords_desativada = [
            'account disabled',
            'account has been disabled',
            'your account has been suspended',
            'permanently banned'
        ]
        
        erro_lower = erro_mensagem.lower()
        
        for keyword in keywords_desativada:
            if keyword in erro_lower:
                logger.critical(f"🚨🚨 CONTA DESATIVADA: {erro_mensagem}")
                
                return {
                    'tipo': 'conta_desativada',
                    'severidade': 'critica',
                    'mensagem': 'Conta desativada/banida',
                    'detalhes': erro_mensagem,
                    'acao_recomendada': 'Remover conta da rotação',
                    'pausar_ate': None  # Pausa permanente
                }
        
        return None
    
    # =============================================
    # DETECÇÃO DE LOGIN SUSPEITO
    # =============================================
    
    def detectar_login_suspeito(self, erro_mensagem):
        """
        Detecta tentativa de login suspeita
        
        Args:
            erro_mensagem: Mensagem de erro
            
        Returns:
            dict com informações do problema ou None
        """
        if not erro_mensagem:
            return None
        
        keywords_login_suspeito = [
            'suspicious login',
            'we detected',
            'unusual login',
            'verify your identity'
        ]
        
        erro_lower = erro_mensagem.lower()
        
        for keyword in keywords_login_suspeito:
            if keyword in erro_lower:
                logger.warning(f"⚠️ Login suspeito detectado: {erro_mensagem}")
                
                return {
                    'tipo': 'login_suspeito',
                    'severidade': 'media',
                    'mensagem': 'Login suspeito detectado',
                    'detalhes': erro_mensagem,
                    'acao_recomendada': 'Pausar por 6 horas e tentar novamente',
                    'pausar_ate': datetime.now() + timedelta(hours=6)
                }
        
        return None
    
    # =============================================
    # DETECÇÃO DE QUEDA DE ENGAJAMENTO
    # =============================================
    
    def detectar_queda_engajamento(self, posts_recentes):
        """
        Detecta queda significativa de engajamento
        
        Args:
            posts_recentes: Lista dos últimos posts com métricas
                           [{'likes': 100, 'views': 500}, ...]
            
        Returns:
            dict com informações ou None
        """
        if not posts_recentes or len(posts_recentes) < 3:
            return None
        
        try:
            # Calcula média de engajamento dos posts antigos
            posts_antigos = posts_recentes[:-3]  # Todos menos os 3 últimos
            posts_novos = posts_recentes[-3:]     # Últimos 3
            
            if not posts_antigos:
                return None
            
            # Média de likes dos posts antigos
            media_antiga = sum(p.get('likes', 0) for p in posts_antigos) / len(posts_antigos)
            
            # Média de likes dos posts novos
            media_nova = sum(p.get('likes', 0) for p in posts_novos) / len(posts_novos)
            
            # Se queda > 50%
            if media_nova < (media_antiga * 0.5):
                queda_percentual = ((media_antiga - media_nova) / media_antiga) * 100
                
                logger.warning(f"⚠️ Queda de engajamento detectada: {queda_percentual:.1f}%")
                
                return {
                    'tipo': 'queda_engajamento',
                    'severidade': 'media',
                    'mensagem': 'Queda de engajamento detectada',
                    'detalhes': f'Queda de {queda_percentual:.1f}% nos últimos 3 posts',
                    'acao_recomendada': 'Revisar conteúdo ou pausar temporariamente'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao detectar queda de engajamento: {e}")
            return None
    
    # =============================================
    # ANÁLISE COMPLETA
    # =============================================
    
    def analisar_erro(self, erro_mensagem, response_data=None):
        """
        Analisa um erro e retorna o problema detectado
        
        Args:
            erro_mensagem: Mensagem de erro
            response_data: Dados da resposta (opcional)
            
        Returns:
            dict com informações do problema ou None
        """
        # Verifica na ordem de severidade
        
        # 1. Conta desativada (CRÍTICO)
        problema = self.detectar_conta_desativada(erro_mensagem)
        if problema:
            self._notificar_problema(problema, erro_mensagem)
            return problema
        
        # 2. Checkpoint (CRÍTICO)
        problema = self.detectar_checkpoint(response_data)
        if problema:
            self._notificar_problema(problema)
            return problema
        
        # 3. Action Block (ALTO)
        problema = self.detectar_action_block(erro_mensagem)
        if problema:
            self._notificar_problema(problema, erro_mensagem)
            return problema
        
        # 4. Login Suspeito (MÉDIO)
        problema = self.detectar_login_suspeito(erro_mensagem)
        if problema:
            self._notificar_problema(problema, erro_mensagem)
            return problema
        
        return None
    
    def _notificar_problema(self, problema, conta_username="Desconhecida"):
        """Notifica problema via Telegram"""
        if not self.telegram_bot:
            return
        
        severidade = problema.get('severidade', 'media')
        tipo = problema.get('tipo', 'desconhecido')
        mensagem = problema.get('mensagem', 'Problema detectado')
        detalhes = problema.get('detalhes', '')
        acao = problema.get('acao_recomendada', 'Verificar manualmente')
        
        if severidade == 'critica':
            self.telegram_bot.alerta_critico(conta_username, mensagem, detalhes)
        elif severidade == 'alta':
            self.telegram_bot.alerta_alto(conta_username, mensagem, acao)
        else:
            self.telegram_bot.alerta_medio(conta_username, mensagem, detalhes)


# =============================================
# FUNÇÕES AUXILIARES
# =============================================

def criar_detector(telegram_bot=None):
    """Cria uma instância do Detector"""
    return Detector(telegram_bot=telegram_bot)


def teste_detector():
    """Testa o módulo Detector"""
    print("🔍 Testando Detector...")
    
    detector = Detector()
    
    print("\n1. Testando detecção de Action Block...")
    problema = detector.detectar_action_block("Action blocked. Try again later.")
    if problema:
        print(f"  ✓ Detectado: {problema['tipo']}")
        print(f"  ✓ Severidade: {problema['severidade']}")
        print(f"  ✓ Ação: {problema['acao_recomendada']}")
    
    print("\n2. Testando detecção de Checkpoint...")
    response = {'checkpoint_required': True, 'checkpoint_url': 'https://instagram.com/challenge/'}
    problema = detector.detectar_checkpoint(response)
    if problema:
        print(f"  ✓ Detectado: {problema['tipo']}")
        print(f"  ✓ URL: {problema['checkpoint_url']}")
    
    print("\n3. Testando detecção de Conta Desativada...")
    problema = detector.detectar_conta_desativada("Your account has been disabled")
    if problema:
        print(f"  ✓ Detectado: {problema['tipo']}")
        print(f"  ✓ Severidade: {problema['severidade']}")
    
    print("\n4. Testando análise completa de erro...")
    problema = detector.analisar_erro("Spam behavior detected. Try again later.")
    if problema:
        print(f"  ✓ Problema: {problema['mensagem']}")
    
    print("\n✅ Detector testado com sucesso!")


if __name__ == "__main__":
    teste_detector()