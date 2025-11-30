"""
Scheduler - Instagram Automation Pro
Agendador automático de posts para 50 contas

Sistema que gerencia posts automáticos em horários específicos
"""

import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
import schedule

logger = logging.getLogger(__name__)


class Scheduler:
    """Agendador de posts automáticos"""
    
    def __init__(self, poster, humanizer, telegram_bot, db_session):
        """
        Inicializa o Scheduler
        
        Args:
            poster: Instância do Poster
            humanizer: Instância do Humanizer
            telegram_bot: Instância do TelegramBot
            db_session: Sessão do banco de dados
        """
        self.poster = poster
        self.humanizer = humanizer
        self.telegram_bot = telegram_bot
        self.db_session = db_session
        
        # Carregar configurações
        self._load_configs()
        
        # Índices de rotação (em memória)
        self.rotation_indices = {}
        
        logger.info("✓ Scheduler inicializado")
    
    def _load_configs(self):
        """Carrega arquivos de configuração"""
        # Carregar contas
        with open('config/contas.json', 'r', encoding='utf-8') as f:
            self.config_contas = json.load(f)
        
        # Carregar horários
        horarios_path = Path('config/horarios.json')
        if horarios_path.exists():
            with open('config/horarios.json', 'r', encoding='utf-8') as f:
                self.config_horarios = json.load(f)
        else:
            # Criar horários padrão
            self.config_horarios = self._criar_horarios_padrao()
        
        # Carregar legendas
        with open('config/legendas.json', 'r', encoding='utf-8') as f:
            self.legendas = json.load(f)['legendas']
        
        # Carregar hashtags
        with open('config/hashtags.json', 'r', encoding='utf-8') as f:
            self.hashtags = json.load(f)['hashtags']
        
        logger.info(f"✓ Configurações carregadas: {len(self.config_contas['contas'])} contas")
    
    def _criar_horarios_padrao(self):
        """Cria horários padrão se não existir arquivo"""
        horarios = {
            "contas": []
        }
        
        # 4 horários por dia para cada conta
        horarios_base = [
            ["09:00", "13:00", "17:00", "21:00"],
            ["09:30", "13:30", "17:30", "21:30"],
            ["10:00", "14:00", "18:00", "22:00"],
            ["10:30", "14:30", "18:30", "22:30"]
        ]
        
        for i, conta in enumerate(self.config_contas['contas']):
            horario_grupo = horarios_base[i % len(horarios_base)]
            
            horarios["contas"].append({
                "conta_id": conta['id'],
                "username": conta['username'],
                "horarios": horario_grupo,
                "variacao_minutos": 15,
                "ativo": True,
                "timezone": "America/Sao_Paulo"
            })
        
        # Salvar
        with open('config/horarios.json', 'w', encoding='utf-8') as f:
            json.dump(horarios, f, indent=2, ensure_ascii=False)
        
        logger.info("✓ Horários padrão criados em config/horarios.json")
        return horarios
    
    def _get_proximo_item_rotacao(self, conta_id, tipo, items_list):
        """
        Pega o próximo item na rotação (vídeo, legenda ou hashtag)
        
        Args:
            conta_id: ID da conta
            tipo: 'video', 'legenda', 'hashtag'
            items_list: Lista de itens para rotacionar
            
        Returns:
            Item selecionado
        """
        # Criar chave única para esta conta e tipo
        key = f"{conta_id}_{tipo}"
        
        # Se não existe índice, criar
        if key not in self.rotation_indices:
            self.rotation_indices[key] = 0
        
        # Pegar índice atual
        indice = self.rotation_indices[key]
        
        # Se acabou a lista, recomeçar
        if indice >= len(items_list):
            indice = 0
            self.rotation_indices[key] = 0
            logger.info(f"🔄 Rotação de {tipo} reiniciada para conta {conta_id}")
        
        # Pegar item
        item = items_list[indice]
        
        # Avançar índice
        self.rotation_indices[key] = indice + 1
        
        return item
    
    def _listar_fotos_disponiveis(self):
        """Lista todas as fotos disponíveis no cache"""
        fotos = []
        
        for pasta in ['cache_local/feed', 'cache_local/']:
            pasta_path = Path(pasta)
            if pasta_path.exists():
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                    fotos.extend(list(pasta_path.glob(ext)))
        
        return [str(f) for f in fotos]
    
    def _listar_videos_disponiveis(self, tipo='reel'):
        """Lista vídeos disponíveis"""
        pasta_map = {
            'reel': 'cache_local/reels',
            'story': 'cache_local/stories',
            'feed': 'cache_local/feed'
        }
        
        pasta = pasta_map.get(tipo, 'cache_local/reels')
        pasta_path = Path(pasta)
        
        if not pasta_path.exists():
            return []
        
        videos = []
        for ext in ['*.mp4', '*.mov', '*.avi']:
            videos.extend(list(pasta_path.glob(ext)))
        
        return [str(v) for v in videos]
    
    def postar_agora(self, conta_id, tipo='feed'):
        """
        Executa um post imediatamente
        
        Args:
            conta_id: ID da conta
            tipo: 'reel', 'story', 'feed'
            
        Returns:
            True se sucesso, False se falhar
        """
        try:
            # Buscar conta
            from database.models import Conta
            conta = self.db_session.query(Conta).filter_by(id=conta_id).first()
            
            if not conta:
                logger.error(f"❌ Conta {conta_id} não encontrada")
                return False
            
            # Verificar se está pausada
            if conta.status != 'ativa':
                logger.warning(f"⚠️ Conta @{conta.username} está {conta.status}")
                return False
            
            if conta.pausado_ate and conta.pausado_ate > datetime.now():
                logger.warning(f"⚠️ Conta @{conta.username} pausada até {conta.pausado_ate}")
                return False
            
            logger.info(f"📤 Iniciando post para @{conta.username} (tipo: {tipo})")
            
            # Buscar proxy se configurado
            proxy = None
            if conta.proxy_id:
                from database.models import Proxy
                proxy_obj = self.db_session.query(Proxy).filter_by(id=conta.proxy_id).first()
                if proxy_obj:
                    proxy = {
                        'host': proxy_obj.host,
                        'port': proxy_obj.port,
                        'username': proxy_obj.username,
                        'password': proxy_obj.password
                    }
            
            # Fazer login
            session_path = f"sessoes/{conta.username}_session.json"
            client = self.poster.fazer_login(
                username=conta.username,
                password=conta.password,
                proxy=proxy,
                session_path=session_path
            )
            
            if not client:
                logger.error(f"❌ Falha no login: @{conta.username}")
                conta.total_erros += 1
                self.db_session.commit()
                return False
            
            # Decidir se posta ou pula (5% de chance de pular)
            if self.humanizer.deve_pular_post():
                logger.info(f"🎲 Post pulado aleatoriamente (comportamento humano)")
                return False
            
            # Buscar mídia (foto ou vídeo)
            if tipo in ['reel', 'story']:
                # Para reels/stories, usar vídeo
                videos = self._listar_videos_disponiveis(tipo)
                if not videos:
                    logger.error(f"❌ Nenhum vídeo encontrado para {tipo}")
                    return False
                
                media_path = self._get_proximo_item_rotacao(conta.id, f'video_{tipo}', videos)
            else:
                # Para feed, usar foto
                fotos = self._listar_fotos_disponiveis()
                if not fotos:
                    logger.error(f"❌ Nenhuma foto encontrada")
                    return False
                
                media_path = self._get_proximo_item_rotacao(conta.id, 'foto_feed', fotos)
            
            # Pegar legenda e hashtags (para reel/feed)
            if tipo != 'story':
                legenda = self._get_proximo_item_rotacao(conta.id, 'legenda', self.legendas)
                hashtag = self._get_proximo_item_rotacao(conta.id, 'hashtag', self.hashtags)
                caption = f"{legenda}\n\n{hashtag}".strip()
            else:
                caption = None
            
            # POSTAR!
            resultado = None
            
            if tipo == 'reel':
                resultado = self.poster.postar_reel(client, media_path, legenda, hashtag)
            elif tipo == 'story':
                resultado = self.poster.postar_story(client, media_path)
            elif tipo == 'feed':
                # Para feed com foto
                self.humanizer.comportamento_pre_post(client)
                self.humanizer.simular_digitacao(caption)
                self.humanizer.delay_curto()
                
                media = client.photo_upload(media_path, caption)
                
                self.humanizer.comportamento_pos_post(client)
                
                resultado = {
                    'sucesso': True,
                    'media_id': media.pk,
                    'media_url': f"https://instagram.com/p/{media.code}/",
                    'timestamp': datetime.now()
                }
            
            # Verificar resultado
            if resultado and resultado.get('sucesso'):
                logger.info(f"✅ Post realizado com sucesso!")
                
                # Atualizar banco de dados
                conta.total_posts += 1
                conta.ultimo_post = datetime.now()
                self.db_session.commit()
                
                # Notificar Telegram
                if self.telegram_bot.enabled:
                    self.telegram_bot.notificar_post_sucesso(
                        conta.username,
                        tipo,
                        Path(media_path).name
                    )
                
                # Delay entre contas
                self.humanizer.delay_entre_contas()
                
                return True
            else:
                logger.error(f"❌ Falha ao postar")
                conta.total_erros += 1
                self.db_session.commit()
                
                # Verificar problema
                if resultado and resultado.get('problema'):
                    problema = resultado['problema']
                    if problema.get('pausar_ate'):
                        conta.pausado_ate = problema['pausar_ate']
                        conta.motivo_pausa = problema['mensagem']
                        self.db_session.commit()
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao postar: {e}", exc_info=True)
            return False
    
    def agendar_posts(self):
        """Agenda posts para todas as contas"""
        logger.info("📅 Agendando posts automáticos...")
        
        total_agendados = 0
        
        for conta_config in self.config_horarios['contas']:
            if not conta_config.get('ativo', True):
                continue
            
            conta_id = conta_config['conta_id']
            username = conta_config['username']
            horarios = conta_config['horarios']
            
            for horario in horarios:
                # Agendar com schedule
                schedule.every().day.at(horario).do(
                    self.postar_agora,
                    conta_id=conta_id,
                    tipo='feed'  # Pode ser 'reel', 'story', 'feed'
                ).tag(f'conta_{conta_id}', username)
                
                total_agendados += 1
                logger.info(f"  ✓ @{username}: {horario}")
        
        logger.info(f"✅ {total_agendados} posts agendados!")
    
    def run(self):
        """Loop principal do scheduler"""
        logger.info("\n" + "="*60)
        logger.info("🚀 SCHEDULER INICIADO - RODANDO 24/7")
        logger.info("="*60)
        
        # Agendar todos os posts
        self.agendar_posts()
        
        # Mostrar próximos posts
        self.mostrar_proximos_posts()
        
        # Loop infinito
        logger.info("\n⏰ Aguardando horários de post...")
        logger.info("(Pressione Ctrl+C para parar)\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Checa a cada 1 minuto
        except KeyboardInterrupt:
            logger.info("\n\n👋 Scheduler encerrado pelo usuário")
    
    def mostrar_proximos_posts(self, limite=10):
        """Mostra os próximos posts agendados"""
        jobs = schedule.get_jobs()
        
        if not jobs:
            logger.info("⚠️ Nenhum post agendado")
            return
        
        logger.info(f"\n📋 Próximos {limite} posts:")
        logger.info("-" * 60)
        
        for i, job in enumerate(jobs[:limite], 1):
            proxima_exec = job.next_run
            tags = ', '.join(job.tags)
            logger.info(f"{i}. {proxima_exec.strftime('%d/%m %H:%M')} - {tags}")
        
        logger.info("-" * 60)


# =============================================
# FUNÇÕES AUXILIARES
# =============================================

def criar_scheduler(poster, humanizer, telegram_bot, db_session):
    """Cria instância do Scheduler"""
    return Scheduler(poster, humanizer, telegram_bot, db_session)