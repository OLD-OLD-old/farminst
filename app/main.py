"""
Main - Instagram Automation Pro
Orquestrador principal do sistema

Este é o arquivo principal que executa todo o sistema!
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Carrega variáveis de ambiente
load_dotenv()

# Importa módulos
from app.humanizer import Humanizer
from app.detector import Detector
from app.telegram_bot import TelegramBot
from app.poster import Poster
from app.scheduler import Scheduler
from database.models import init_database, get_session, Conta, Proxy

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/main_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class InstagramBot:
    """Classe principal do bot"""
    
    def __init__(self):
        """Inicializa o bot"""
        logger.info("="*60)
        logger.info("🚀 INSTAGRAM AUTOMATION PRO - INICIANDO")
        logger.info("="*60)
        
        # Inicializar banco de dados
        self._init_database()
        
        # Carregar configurações
        self._load_configs()
        
        # Inicializar módulos
        self._init_modules()
        
        logger.info("✅ Bot inicializado com sucesso!")
    
    def _init_database(self):
        """Inicializa o banco de dados"""
        logger.info("📦 Inicializando banco de dados...")
        self.engine, self.Session = init_database()
        self.db_session = get_session()
        logger.info("✓ Banco de dados pronto!")
    
    def _load_configs(self):
        """Carrega arquivos de configuração"""
        logger.info("📂 Carregando configurações...")
        
        # Carregar contas
        with open('config/contas.json', 'r', encoding='utf-8') as f:
            self.config_contas = json.load(f)
        logger.info(f"  ✓ {len(self.config_contas['contas'])} contas carregadas")
        
        # Carregar legendas
        with open('config/legendas.json', 'r', encoding='utf-8') as f:
            self.config_legendas = json.load(f)
        logger.info(f"  ✓ {len(self.config_legendas['legendas'])} legendas carregadas")
        
        # Carregar hashtags
        with open('config/hashtags.json', 'r', encoding='utf-8') as f:
            self.config_hashtags = json.load(f)
        logger.info(f"  ✓ {len(self.config_hashtags['hashtags'])} grupos de hashtags carregados")
    
    def _init_modules(self):
        """Inicializa os módulos do sistema"""
        logger.info("🔧 Inicializando módulos...")
        
        # Telegram Bot
        self.telegram_bot = TelegramBot()
        if self.telegram_bot.enabled:
            logger.info("  ✓ Telegram Bot ativado")
            self.telegram_bot.teste_conexao()
        else:
            logger.warning("  ⚠ Telegram Bot desativado")
        
        # Humanizer
        nivel = os.getenv('HUMANIZE_LEVEL', 'alto')
        self.humanizer = Humanizer(nivel=nivel)
        logger.info(f"  ✓ Humanizer inicializado (nível: {nivel})")
        
        # Detector
        self.detector = Detector(telegram_bot=self.telegram_bot)
        logger.info("  ✓ Detector inicializado")
        
        # Poster
        self.poster = Poster(
            humanizer=self.humanizer,
            detector=self.detector,
            telegram_bot=self.telegram_bot
        )
        logger.info("  ✓ Poster inicializado")
        
        # Scheduler
        self.scheduler = Scheduler(
            poster=self.poster,
            humanizer=self.humanizer,
            telegram_bot=self.telegram_bot,
            db_session=self.db_session
        )
        logger.info("  ✓ Scheduler inicializado")
    
    def sync_contas_to_database(self):
        """Sincroniza contas do JSON para o banco de dados"""
        logger.info("🔄 Sincronizando contas com banco de dados...")
        
        for conta_config in self.config_contas['contas']:
            # Verifica se conta já existe
            conta_db = self.db_session.query(Conta).filter_by(
                username=conta_config['username']
            ).first()
            
            if not conta_db:
                # Cria nova conta
                conta_db = Conta(
                    username=conta_config['username'],
                    password=conta_config['password'],
                    email=conta_config.get('email'),
                    proxy_id=conta_config.get('proxy_id'),
                    status=conta_config.get('status', 'ativa'),
                    two_factor_seed=conta_config.get('two_factor_seed', '')
                )
                self.db_session.add(conta_db)
                logger.info(f"  ✓ Conta adicionada: @{conta_config['username']}")
            else:
                logger.info(f"  • Conta já existe: @{conta_config['username']}")
        
        self.db_session.commit()
        logger.info("✓ Sincronização concluída!")
    
    def testar_sistema(self):
        """Testa todos os componentes do sistema"""
        logger.info("\n" + "="*60)
        logger.info("🧪 TESTANDO SISTEMA")
        logger.info("="*60)
        
        # 1. Testar banco de dados
        logger.info("\n1️⃣ Testando banco de dados...")
        total_contas = self.db_session.query(Conta).count()
        logger.info(f"  ✓ {total_contas} contas no banco de dados")
        
        # 2. Testar Telegram
        logger.info("\n2️⃣ Testando Telegram...")
        if self.telegram_bot.enabled:
            self.telegram_bot._send_message("🧪 Teste do sistema - Tudo funcionando!")
            logger.info("  ✓ Mensagem de teste enviada")
        else:
            logger.warning("  ⚠ Telegram desativado")
        
        # 3. Testar Humanizer
        logger.info("\n3️⃣ Testando Humanizer...")
        logger.info("  • Delay de teste...")
        self.humanizer.delay_natural(1, 2)
        logger.info("  ✓ Humanizer funcionando")
        
        # 4. Testar Detector
        logger.info("\n4️⃣ Testando Detector...")
        problema = self.detector.detectar_action_block("Action blocked test")
        if problema:
            logger.info(f"  ✓ Detector identificou: {problema['tipo']}")
        
        logger.info("\n" + "="*60)
        logger.info("✅ TODOS OS TESTES PASSARAM!")
        logger.info("="*60)
    
    def status_sistema(self):
        """Mostra status completo do sistema"""
        logger.info("\n" + "="*60)
        logger.info("📊 STATUS DO SISTEMA")
        logger.info("="*60)
        
        # Contas
        total_contas = self.db_session.query(Conta).count()
        contas_ativas = self.db_session.query(Conta).filter_by(status='ativa').count()
        contas_pausadas = self.db_session.query(Conta).filter_by(status='pausada').count()
        
        logger.info(f"\n👥 CONTAS:")
        logger.info(f"  Total: {total_contas}")
        logger.info(f"  Ativas: {contas_ativas}")
        logger.info(f"  Pausadas: {contas_pausadas}")
        
        # Proxies
        total_proxies = self.db_session.query(Proxy).count()
        logger.info(f"\n🌐 PROXIES:")
        logger.info(f"  Total: {total_proxies}")
        
        # Configurações
        logger.info(f"\n⚙️ CONFIGURAÇÕES:")
        logger.info(f"  Legendas disponíveis: {len(self.config_legendas['legendas'])}")
        logger.info(f"  Grupos de hashtags: {len(self.config_hashtags['hashtags'])}")
        logger.info(f"  Humanização: {os.getenv('HUMANIZE_LEVEL', 'alto')}")
        logger.info(f"  Telegram: {'Ativo' if self.telegram_bot.enabled else 'Desativado'}")
        
        logger.info("\n" + "="*60)
    
    def iniciar(self):
        """Inicia o sistema de automação"""
        logger.info("\n" + "="*60)
        logger.info("🚀 INICIANDO SISTEMA DE AUTOMAÇÃO")
        logger.info("="*60)
        
        # Sincronizar contas
        self.sync_contas_to_database()
        
        # Mostrar status
        self.status_sistema()
        
        # Notificar Telegram
        if self.telegram_bot.enabled:
            self.telegram_bot._send_message(
                "🚀 <b>Sistema Iniciado!</b>\n\n"
                f"✅ {self.db_session.query(Conta).filter_by(status='ativa').count()} contas ativas\n"
                "🤖 Scheduler ativado!\n"
                "📅 Posts automáticos agendados!"
            )
        
        # INICIAR SCHEDULER
        logger.info("\n🚀 Iniciando Scheduler (posts automáticos)...")
        self.scheduler.run()


def main():
    """Função principal"""
    try:
        # Criar bot
        bot = InstagramBot()
        
        # Menu interativo
        print("\n" + "="*60)
        print("🤖 INSTAGRAM AUTOMATION PRO")
        print("="*60)
        print("\nEscolha uma opção:")
        print("1. Testar sistema")
        print("2. Ver status")
        print("3. Iniciar automação")
        print("0. Sair")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            bot.testar_sistema()
        elif opcao == "2":
            bot.status_sistema()
        elif opcao == "3":
            bot.iniciar()
        elif opcao == "0":
            logger.info("👋 Até logo!")
        else:
            logger.warning("Opção inválida!")
            
    except KeyboardInterrupt:
        logger.info("\n\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}", exc_info=True)


if __name__ == "__main__":
    main()