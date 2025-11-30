"""
Humanizer - Instagram Automation Pro
Simula comportamento humano para evitar detecção e bans

CRÍTICO: Este módulo é essencial para evitar bans!
"""

import random
import time
from datetime import datetime, time as dt_time
import logging

logger = logging.getLogger(__name__)


class Humanizer:
    """Classe responsável por humanizar as ações do bot"""
    
    def __init__(self, nivel='alto'):
        """
        Inicializa o humanizador
        
        Args:
            nivel: 'baixo', 'medio', 'alto' (quanto maior, mais seguro)
        """
        self.nivel = nivel
        
        # Configurações por nível
        self.configs = {
            'baixo': {
                'delay_min': 10,
                'delay_max': 30,
                'prob_navegacao': 0.3,
                'prob_curtir': 0.2,
                'prob_stories': 0.1
            },
            'medio': {
                'delay_min': 30,
                'delay_max': 60,
                'prob_navegacao': 0.6,
                'prob_curtir': 0.4,
                'prob_stories': 0.3
            },
            'alto': {
                'delay_min': 30,
                'delay_max': 90,
                'prob_navegacao': 0.8,
                'prob_curtir': 0.6,
                'prob_stories': 0.5
            }
        }
        
        self.config = self.configs.get(nivel, self.configs['alto'])
        logger.info(f"✓ Humanizador inicializado no nível: {nivel}")
    
    # =============================================
    # DELAYS
    # =============================================
    
    def delay_natural(self, min_sec=None, max_sec=None):
        """Adiciona um delay natural e variável"""
        if min_sec is None:
            min_sec = self.config['delay_min']
        if max_sec is None:
            max_sec = self.config['delay_max']
        
        delay = random.uniform(min_sec, max_sec)
        logger.info(f"⏱️ Aguardando {delay:.1f} segundos...")
        time.sleep(delay)
        return delay
    
    def delay_curto(self):
        """Delay curto entre ações (5-15 segundos)"""
        return self.delay_natural(5, 15)
    
    def delay_medio(self):
        """Delay médio entre posts (3-5 minutos)"""
        return self.delay_natural(180, 300)
    
    def delay_longo(self):
        """Delay longo após erro (10-20 minutos)"""
        return self.delay_natural(600, 1200)
    
    # =============================================
    # COMPORTAMENTOS PRÉ-POST
    # =============================================
    
    def comportamento_pre_post(self, client):
        """
        Simula comportamento humano ANTES de postar
        
        Args:
            client: Cliente Instagram (instagrapi)
        """
        logger.info("🤖 Iniciando comportamento humano PRÉ-POST...")
        
        # 1. Navegar no feed (80% de chance)
        if random.random() < self.config['prob_navegacao']:
            logger.info("  📱 Navegando no feed...")
            self._navegar_feed(client)
            self.delay_curto()
        
        # 2. Ver stories (50% de chance)
        if random.random() < self.config['prob_stories']:
            logger.info("  📺 Assistindo stories...")
            self._ver_stories(client)
            self.delay_curto()
        
        # 3. Curtir posts (60% de chance)
        if random.random() < self.config['prob_curtir']:
            logger.info("  ❤️ Curtindo posts...")
            self._curtir_posts_aleatorios(client)
            self.delay_curto()
        
        logger.info("✓ Comportamento PRÉ-POST concluído")
    
    def _navegar_feed(self, client):
        """Simula navegação no feed"""
        try:
            # Busca timeline
            timeline = client.get_timeline_feed()
            
            # "Visualiza" 3-5 posts
            num_posts = random.randint(3, 5)
            for i in range(min(num_posts, len(timeline))):
                time.sleep(random.uniform(2, 5))  # Tempo de "visualização"
            
            logger.debug(f"  ✓ Navegou por {num_posts} posts")
        except Exception as e:
            logger.debug(f"  ⚠ Erro ao navegar feed: {e}")
    
    def _ver_stories(self, client):
        """Simula visualização de stories"""
        try:
            # Busca stories da timeline
            stories = client.get_timeline_stories()
            
            # "Assiste" 2-4 stories
            num_stories = random.randint(2, 4)
            for i in range(min(num_stories, len(stories))):
                time.sleep(random.uniform(3, 8))  # Tempo de "visualização"
            
            logger.debug(f"  ✓ Assistiu {num_stories} stories")
        except Exception as e:
            logger.debug(f"  ⚠ Erro ao ver stories: {e}")
    
    def _curtir_posts_aleatorios(self, client):
        """Curte 1-3 posts aleatórios"""
        try:
            timeline = client.get_timeline_feed()
            
            # Curte 1-3 posts
            num_likes = random.randint(1, 3)
            for i in range(min(num_likes, len(timeline))):
                media = timeline[i]
                client.media_like(media.id)
                time.sleep(random.uniform(2, 5))
            
            logger.debug(f"  ✓ Curtiu {num_likes} posts")
        except Exception as e:
            logger.debug(f"  ⚠ Erro ao curtir posts: {e}")
    
    # =============================================
    # COMPORTAMENTOS PÓS-POST
    # =============================================
    
    def comportamento_pos_post(self, client):
        """
        Simula comportamento humano DEPOIS de postar
        
        Args:
            client: Cliente Instagram
        """
        logger.info("🤖 Iniciando comportamento humano PÓS-POST...")
        
        # 1. Ver insights do próprio post (30% de chance)
        if random.random() < 0.3:
            logger.info("  📊 Verificando insights...")
            time.sleep(random.uniform(3, 8))
        
        # 2. Checar notificações (20% de chance)
        if random.random() < 0.2:
            logger.info("  🔔 Checando notificações...")
            time.sleep(random.uniform(2, 5))
        
        logger.info("✓ Comportamento PÓS-POST concluído")
    
    # =============================================
    # PADRÕES DE HORÁRIO
    # =============================================
    
    def ajustar_delay_por_horario(self, delay_base):
        """
        Ajusta delay baseado no horário do dia
        
        Humanos são mais ativos em certos horários:
        - Madrugada (00h-06h): 10% de atividade
        - Manhã (06h-12h): 60% de atividade
        - Tarde (12h-18h): 80% de atividade
        - Noite (18h-00h): 90% de atividade
        
        Args:
            delay_base: Delay base em segundos
            
        Returns:
            Delay ajustado
        """
        hora_atual = datetime.now().hour
        
        if 0 <= hora_atual < 6:  # Madrugada
            multiplicador = 2.0  # Mais delay = menos atividade
        elif 6 <= hora_atual < 12:  # Manhã
            multiplicador = 1.2
        elif 12 <= hora_atual < 18:  # Tarde
            multiplicador = 1.0
        else:  # Noite (18h-00h)
            multiplicador = 0.9
        
        delay_ajustado = delay_base * multiplicador
        logger.debug(f"Delay ajustado por horário: {delay_base:.1f}s → {delay_ajustado:.1f}s")
        
        return delay_ajustado
    
    def variacao_horario(self, horario_alvo, variacao_minutos=15):
        """
        Adiciona variação natural ao horário de post
        
        Args:
            horario_alvo: Horário planejado (datetime)
            variacao_minutos: Variação máxima em minutos
            
        Returns:
            Horário com variação natural
        """
        variacao = random.randint(-variacao_minutos, variacao_minutos)
        from datetime import timedelta
        horario_natural = horario_alvo + timedelta(minutes=variacao)
        
        logger.debug(f"Variação de horário: {horario_alvo.strftime('%H:%M')} → {horario_natural.strftime('%H:%M')}")
        
        return horario_natural
    
    # =============================================
    # DETECÇÃO DE PADRÕES SUSPEITOS
    # =============================================
    
    def deve_pular_post(self):
        """
        Decide aleatoriamente se deve pular um post (5% de chance)
        
        Humanos nem sempre postam exatamente nos horários programados
        
        Returns:
            True se deve pular, False caso contrário
        """
        pular = random.random() < 0.05
        if pular:
            logger.info("🎲 Pulando post aleatoriamente (comportamento humano)")
        return pular
    
    def delay_entre_contas(self):
        """Delay entre posts de contas diferentes (30-90 segundos)"""
        return self.delay_natural(30, 90)
    
    # =============================================
    # SIMULAÇÃO DE DIGITAÇÃO
    # =============================================
    
    def simular_digitacao(self, texto, velocidade=0.1):
        """
        Simula digitação humana de texto
        
        Args:
            texto: Texto a ser "digitado"
            velocidade: Segundos por caractere (aprox)
        """
        tempo_total = len(texto) * velocidade * random.uniform(0.8, 1.2)
        logger.debug(f"Simulando digitação de {len(texto)} caracteres ({tempo_total:.1f}s)")
        time.sleep(tempo_total)


# =============================================
# FUNÇÕES AUXILIARES
# =============================================

def criar_humanizer(nivel='alto'):
    """Cria uma instância do Humanizer"""
    return Humanizer(nivel=nivel)


def teste_humanizer():
    """Testa o módulo Humanizer"""
    print("🤖 Testando Humanizer...")
    
    humanizer = Humanizer(nivel='alto')
    
    print("\n1. Testando delay natural...")
    humanizer.delay_natural(1, 3)
    print("  ✓ Delay funcionou")
    
    print("\n2. Testando variação de horário...")
    from datetime import datetime, timedelta
    horario = datetime.now() + timedelta(hours=1)
    horario_variado = humanizer.variacao_horario(horario)
    print(f"  ✓ Original: {horario.strftime('%H:%M')}")
    print(f"  ✓ Variado: {horario_variado.strftime('%H:%M')}")
    
    print("\n3. Testando decisão de pular post...")
    for i in range(5):
        resultado = "PULA" if humanizer.deve_pular_post() else "POSTA"
        print(f"  Tentativa {i+1}: {resultado}")
    
    print("\n✅ Humanizer testado com sucesso!")


if __name__ == "__main__":
    teste_humanizer()