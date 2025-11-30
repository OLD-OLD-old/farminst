"""
Poster - Instagram Automation Pro
Sistema principal de postagem com retry e humanização

CRÍTICO: Este é o módulo que realiza os posts!
"""

import os
import logging
import time
from datetime import datetime
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, FeedbackRequired

logger = logging.getLogger(__name__)


class Poster:
    """Classe responsável por postar no Instagram"""
    
    def __init__(self, humanizer, detector, telegram_bot=None):
        """
        Inicializa o Poster
        
        Args:
            humanizer: Instância do Humanizer
            detector: Instância do Detector
            telegram_bot: Instância do TelegramBot (opcional)
        """
        self.humanizer = humanizer
        self.detector = detector
        self.telegram_bot = telegram_bot
        self.max_retries = 3
        
        logger.info("✓ Poster inicializado")
    
    # =============================================
    # LOGIN E SESSÃO
    # =============================================
    
    def fazer_login(self, username, password, proxy=None, session_path=None):
        """
        Faz login no Instagram
        
        Args:
            username: Username da conta
            password: Senha da conta
            proxy: Dicionário com configurações do proxy
            session_path: Caminho para arquivo de sessão
            
        Returns:
            Client do Instagram ou None se falhar
        """
        try:
            logger.info(f"🔐 Fazendo login: @{username}")
            
            # Criar cliente
            client = Client()
            
            # Configurar proxy se fornecido
            if proxy:
                proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
                client.set_proxy(proxy_url)
                logger.info(f"  🌐 Usando proxy: {proxy['host']}")
            
            # Carregar sessão se existir
            if session_path and Path(session_path).exists():
                try:
                    client.load_settings(session_path)
                    client.login(username, password)
                    logger.info(f"  ✓ Login com sessão salva")
                    return client
                except Exception as e:
                    logger.warning(f"  ⚠ Erro ao usar sessão: {e}")
            
            # Login normal
            client.login(username, password)
            
            # Salvar sessão
            if session_path:
                client.dump_settings(session_path)
                logger.info(f"  ✓ Sessão salva em: {session_path}")
            
            logger.info(f"  ✓ Login bem-sucedido!")
            return client
            
        except ChallengeRequired as e:
            logger.error(f"  🚨 Checkpoint requerido!")
            problema = self.detector.detectar_checkpoint({'checkpoint_required': True})
            if self.telegram_bot and problema:
                self.telegram_bot.alerta_critico(username, "Checkpoint Required", str(e))
            return None
            
        except LoginRequired as e:
            logger.error(f"  ❌ Erro de login: {e}")
            problema = self.detector.analisar_erro(str(e))
            if self.telegram_bot and problema:
                self.telegram_bot.alerta_alto(username, "Erro de Login", str(e))
            return None
            
        except Exception as e:
            logger.error(f"  ❌ Erro inesperado no login: {e}")
            return None
    
    # =============================================
    # POSTAGEM
    # =============================================
    
    def postar_reel(self, client, video_path, legenda, hashtags=""):
        """
        Posta um Reel no Instagram
        
        Args:
            client: Cliente Instagram autenticado
            video_path: Caminho do vídeo
            legenda: Legenda do post
            hashtags: Hashtags (opcional)
            
        Returns:
            dict com resultado do post ou None
        """
        try:
            logger.info(f"📤 Postando Reel: {Path(video_path).name}")
            
            # Validar arquivo
            if not Path(video_path).exists():
                logger.error(f"  ❌ Vídeo não encontrado: {video_path}")
                return None
            
            # Combinar legenda e hashtags
            caption = f"{legenda}\n\n{hashtags}".strip()
            
            # Comportamento humano PRÉ-POST
            logger.info("  🤖 Simulando comportamento humano...")
            self.humanizer.comportamento_pre_post(client)
            
            # Simular digitação da legenda
            self.humanizer.simular_digitacao(caption)
            
            # Delay antes de publicar
            self.humanizer.delay_curto()
            
            # POSTAR!
            logger.info("  📤 Enviando reel...")
            media = client.clip_upload(video_path, caption)
            
            # Comportamento humano PÓS-POST
            self.humanizer.comportamento_pos_post(client)
            
            logger.info(f"  ✅ Reel postado com sucesso! ID: {media.pk}")
            
            return {
                'sucesso': True,
                'media_id': media.pk,
                'media_url': f"https://instagram.com/p/{media.code}/",
                'timestamp': datetime.now()
            }
            
        except FeedbackRequired as e:
            logger.error(f"  ❌ Feedback required: {e}")
            problema = self.detector.analisar_erro(str(e))
            return {'sucesso': False, 'erro': str(e), 'problema': problema}
            
        except Exception as e:
            logger.error(f"  ❌ Erro ao postar reel: {e}")
            problema = self.detector.analisar_erro(str(e))
            return {'sucesso': False, 'erro': str(e), 'problema': problema}
    
    def postar_story(self, client, video_path):
        """
        Posta um Story no Instagram
        
        Args:
            client: Cliente Instagram autenticado
            video_path: Caminho do vídeo
            
        Returns:
            dict com resultado do post ou None
        """
        try:
            logger.info(f"📤 Postando Story: {Path(video_path).name}")
            
            if not Path(video_path).exists():
                logger.error(f"  ❌ Vídeo não encontrado: {video_path}")
                return None
            
            # Comportamento humano
            self.humanizer.delay_curto()
            
            # POSTAR!
            logger.info("  📤 Enviando story...")
            media = client.video_upload_to_story(video_path)
            
            logger.info(f"  ✅ Story postado com sucesso! ID: {media.pk}")
            
            return {
                'sucesso': True,
                'media_id': media.pk,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"  ❌ Erro ao postar story: {e}")
            problema = self.detector.analisar_erro(str(e))
            return {'sucesso': False, 'erro': str(e), 'problema': problema}
    
    def postar_feed(self, client, video_path, legenda, hashtags=""):
        """
        Posta um vídeo no Feed normal
        
        Args:
            client: Cliente Instagram autenticado
            video_path: Caminho do vídeo
            legenda: Legenda do post
            hashtags: Hashtags (opcional)
            
        Returns:
            dict com resultado do post ou None
        """
        try:
            logger.info(f"📤 Postando no Feed: {Path(video_path).name}")
            
            if not Path(video_path).exists():
                logger.error(f"  ❌ Vídeo não encontrado: {video_path}")
                return None
            
            caption = f"{legenda}\n\n{hashtags}".strip()
            
            # Comportamento humano
            self.humanizer.comportamento_pre_post(client)
            self.humanizer.simular_digitacao(caption)
            self.humanizer.delay_curto()
            
            # POSTAR!
            logger.info("  📤 Enviando vídeo...")
            media = client.video_upload(video_path, caption)
            
            self.humanizer.comportamento_pos_post(client)
            
            logger.info(f"  ✅ Vídeo postado com sucesso! ID: {media.pk}")
            
            return {
                'sucesso': True,
                'media_id': media.pk,
                'media_url': f"https://instagram.com/p/{media.code}/",
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"  ❌ Erro ao postar feed: {e}")
            problema = self.detector.analisar_erro(str(e))
            return {'sucesso': False, 'erro': str(e), 'problema': problema}
    
    # =============================================
    # POSTAGEM COM RETRY
    # =============================================
    
    def postar_com_retry(self, tipo, client, video_path, legenda=None, hashtags=""):
        """
        Tenta postar com retry automático
        
        Args:
            tipo: 'reel', 'story' ou 'feed'
            client: Cliente Instagram
            video_path: Caminho do vídeo
            legenda: Legenda (para reel/feed)
            hashtags: Hashtags (para reel/feed)
            
        Returns:
            dict com resultado final
        """
        for tentativa in range(1, self.max_retries + 1):
            logger.info(f"🔄 Tentativa {tentativa}/{self.max_retries}")
            
            # Escolher função de post
            if tipo == 'reel':
                resultado = self.postar_reel(client, video_path, legenda, hashtags)
            elif tipo == 'story':
                resultado = self.postar_story(client, video_path)
            elif tipo == 'feed':
                resultado = self.postar_feed(client, video_path, legenda, hashtags)
            else:
                logger.error(f"❌ Tipo inválido: {tipo}")
                return None
            
            # Se sucesso, retorna
            if resultado and resultado.get('sucesso'):
                return resultado
            
            # Se falhou, verifica problema
            problema = resultado.get('problema') if resultado else None
            
            if problema:
                # Se problema crítico, não tenta novamente
                if problema.get('severidade') == 'critica':
                    logger.error("🚨 Problema crítico detectado. Parando tentativas.")
                    return resultado
            
            # Se não é a última tentativa, aguarda antes de tentar novamente
            if tentativa < self.max_retries:
                delay = 60 * (2 ** tentativa)  # Backoff exponencial
                logger.warning(f"⏳ Aguardando {delay}s antes de tentar novamente...")
                time.sleep(delay)
        
        logger.error(f"❌ Falha após {self.max_retries} tentativas")
        return resultado


# =============================================
# FUNÇÕES AUXILIARES
# =============================================

def criar_poster(humanizer, detector, telegram_bot=None):
    """Cria uma instância do Poster"""
    return Poster(humanizer, detector, telegram_bot)


def teste_poster():
    """Testa o módulo Poster (sem fazer post real)"""
    print("📤 Testando Poster...")
    
    # Importar dependências para teste
    import sys
    sys.path.append(str(Path(__file__).parent))
    
    from humanizer import Humanizer
    from detector import Detector
    
    # Criar instâncias
    humanizer = Humanizer(nivel='alto')
    detector = Detector()
    poster = Poster(humanizer, detector)
    
    print("  ✓ Poster criado com sucesso")
    print("  ✓ Humanizer integrado")
    print("  ✓ Detector integrado")
    
    print("\n⚠️  Para testar posts reais, você precisa:")
    print("  1. Adicionar contas em config/contas.json")
    print("  2. Adicionar vídeos no cache_local/")
    print("  3. Executar o sistema principal (main.py)")
    
    print("\n✅ Poster testado com sucesso!")


if __name__ == "__main__":
    teste_poster()