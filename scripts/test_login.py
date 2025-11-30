"""
Teste de Login - Instagram Automation Pro
Script para testar login de uma conta específica
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.humanizer import Humanizer
from app.detector import Detector
from app.telegram_bot import TelegramBot
from app.poster import Poster


def testar_login():
    """Testa login de uma conta"""
    print("="*60)
    print("🔐 TESTE DE LOGIN - INSTAGRAM")
    print("="*60)
    
    # Carregar contas
    with open('config/contas.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if not config['contas']:
        print("\n❌ Nenhuma conta encontrada em config/contas.json")
        return
    
    # Mostrar contas disponíveis
    print("\n📋 Contas disponíveis:")
    for i, conta in enumerate(config['contas'], 1):
        print(f"{i}. @{conta['username']} (ID: {conta['id']})")
    
    # Escolher conta
    escolha = input("\nEscolha o número da conta (Enter para testar a primeira): ").strip()
    
    if escolha:
        try:
            index = int(escolha) - 1
            if index < 0 or index >= len(config['contas']):
                print("❌ Número inválido!")
                return
        except ValueError:
            print("❌ Digite um número válido!")
            return
    else:
        index = 0
    
    conta = config['contas'][index]
    
    print(f"\n🔍 Testando conta: @{conta['username']}")
    print("-" * 60)
    
    # Criar módulos necessários
    print("\n📦 Inicializando módulos...")
    humanizer = Humanizer(nivel='alto')
    detector = Detector()
    telegram_bot = TelegramBot()
    poster = Poster(humanizer, detector, telegram_bot)
    
    # Preparar dados da conta
    username = conta['username']
    password = conta['password']
    
    # Proxy (se configurado)
    proxy = None
    if conta.get('proxy_id'):
        try:
            with open('config/proxies.json', 'r', encoding='utf-8') as f:
                proxies_config = json.load(f)
                for p in proxies_config.get('proxies', []):
                    if p['id'] == conta['proxy_id']:
                        proxy = p
                        break
        except FileNotFoundError:
            print("⚠️  Arquivo de proxies não encontrado (sem proxy)")
    
    # Caminho da sessão
    session_path = f"sessoes/{username}_session.json"
    
    # Fazer login
    print(f"\n🔐 Fazendo login em @{username}...")
    print("⏳ Aguarde...")
    
    try:
        client = poster.fazer_login(
            username=username,
            password=password,
            proxy=proxy,
            session_path=session_path
        )
        
        if client:
            print("\n" + "="*60)
            print("✅ LOGIN BEM-SUCEDIDO!")
            print("="*60)
            
            # Informações da conta
            user_info = client.user_info(client.user_id)
            print(f"\n📊 Informações da conta:")
            print(f"  • Username: @{user_info.username}")
            print(f"  • Nome: {user_info.full_name}")
            print(f"  • Seguidores: {user_info.follower_count}")
            print(f"  • Seguindo: {user_info.following_count}")
            print(f"  • Posts: {user_info.media_count}")
            print(f"  • Biografia: {user_info.biography[:50]}..." if user_info.biography else "  • Biografia: (vazia)")
            
            # Salvar sessão
            if Path(session_path).exists():
                print(f"\n💾 Sessão salva em: {session_path}")
            
            # Notificar Telegram
            if telegram_bot.enabled:
                telegram_bot._send_message(
                    f"✅ <b>Login Testado</b>\n\n"
                    f"👤 @{username}\n"
                    f"📊 {user_info.follower_count} seguidores\n"
                    f"✅ Pronto para postar!"
                )
            
            print("\n✅ Conta validada e pronta para uso!")
            return True
            
        else:
            print("\n" + "="*60)
            print("❌ FALHA NO LOGIN")
            print("="*60)
            print("\nPossíveis causas:")
            print("  • Usuário ou senha incorretos")
            print("  • Conta requer checkpoint")
            print("  • Conta desativada")
            print("  • Proxy não está funcionando")
            
            # Notificar Telegram
            if telegram_bot.enabled:
                telegram_bot.alerta_critico(
                    username,
                    "Falha no Login",
                    "Verifique as credenciais"
                )
            
            return False
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        testar_login()
    except KeyboardInterrupt:
        print("\n\n👋 Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()