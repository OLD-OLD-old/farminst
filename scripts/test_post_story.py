"""
Teste de Post de Story - Instagram Automation Pro
Script para testar post de vídeo como Story
"""

import sys
import json
import random
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.humanizer import Humanizer
from app.detector import Detector
from app.telegram_bot import TelegramBot
from app.poster import Poster


def listar_videos():
    """Lista todos os vídeos disponíveis no cache"""
    videos = []
    
    # Procurar em todas as pastas
    for pasta in ['cache_local/stories', 'cache_local/reels', 'cache_local/feed', 'cache_local']:
        pasta_path = Path(pasta)
        if pasta_path.exists():
            # Formatos de vídeo suportados
            for ext in ['*.mp4', '*.mov', '*.avi']:
                videos.extend(list(pasta_path.glob(ext)))
    
    return videos


def testar_post_story():
    """Testa post de vídeo como Story"""
    print("="*60)
    print("📺 TESTE DE POST - STORY (VÍDEO)")
    print("="*60)
    
    # 1. Listar vídeos disponíveis
    print("\n🎥 Buscando vídeos no cache...")
    videos = listar_videos()
    
    if not videos:
        print("\n❌ Nenhum vídeo encontrado!")
        print("\nColoque vídeos (MP4, MOV) em:")
        print("  - cache_local/stories/")
        print("  - cache_local/")
        print("\n⚠️  Requisitos do vídeo:")
        print("  • Duração: 3-60 segundos")
        print("  • Formato: MP4, MOV")
        print("  • Tamanho: Até 100MB")
        print("  • Resolução: 1080x1920 (9:16 vertical)")
        return
    
    print(f"\n✅ {len(videos)} vídeo(s) encontrado(s):")
    
    # Remover duplicatas
    videos_unicos = {}
    for video in videos:
        nome = video.name
        if nome not in videos_unicos:
            videos_unicos[nome] = video
    
    videos = list(videos_unicos.values())
    
    for i, video in enumerate(videos, 1):
        tamanho_mb = video.stat().st_size / (1024 * 1024)
        print(f"{i}. {video.name} ({tamanho_mb:.1f} MB)")
    
    # 2. Escolher vídeo
    escolha = input("\nEscolha o número do vídeo (Enter para o primeiro): ").strip()
    
    if escolha:
        try:
            index = int(escolha) - 1
            if index < 0 or index >= len(videos):
                print("❌ Número inválido!")
                return
        except ValueError:
            print("❌ Digite um número válido!")
            return
    else:
        index = 0
    
    video_path = str(videos[index])
    print(f"\n📺 Vídeo selecionado: {videos[index].name}")
    
    # 3. Carregar conta
    with open('config/contas.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if not config['contas']:
        print("\n❌ Nenhuma conta encontrada em config/contas.json")
        return
    
    conta = config['contas'][0]  # Usa primeira conta
    print(f"👤 Usando conta: @{conta['username']}")
    
    print(f"\n💡 Stories não usam legenda/hashtags (apenas o vídeo)")
    
    # 4. Confirmar
    print("\n" + "="*60)
    print("⚠️  ATENÇÃO: Isso vai REALMENTE POSTAR na sua conta!")
    print("="*60)
    confirma = input("\nTem certeza? Digite 'SIM' para confirmar: ").strip().upper()
    
    if confirma != 'SIM':
        print("\n❌ Post cancelado!")
        return
    
    # 5. Inicializar módulos
    print("\n📦 Inicializando sistema...")
    humanizer = Humanizer(nivel='alto')
    detector = Detector()
    telegram_bot = TelegramBot()
    poster = Poster(humanizer, detector, telegram_bot)
    
    # 6. Fazer login
    print(f"\n🔐 Fazendo login em @{conta['username']}...")
    session_path = f"sessoes/{conta['username']}_session.json"
    
    try:
        client = poster.fazer_login(
            username=conta['username'],
            password=conta['password'],
            session_path=session_path
        )
        
        if not client:
            print("❌ Falha no login!")
            return
        
        print("✅ Login bem-sucedido!")
        
        # 7. POSTAR STORY!
        print("\n" + "="*60)
        print("📤 POSTANDO STORY...")
        print("="*60)
        print("\n⏳ Este processo pode levar 1-2 minutos...")
        print("   (comportamento humano para evitar ban)\n")
        
        # Usar a função do poster
        resultado = poster.postar_com_retry(
            tipo='story',
            client=client,
            video_path=video_path
        )
        
        # Verificar resultado
        if resultado and resultado.get('sucesso'):
            # SUCESSO!
            print("\n" + "="*60)
            print("✅ STORY POSTADO COM SUCESSO!")
            print("="*60)
            print(f"\n📊 Detalhes:")
            print(f"  • Media ID: {resultado['media_id']}")
            print(f"  • Horário: {resultado['timestamp']}")
            print(f"  • Duração: 24 horas")
            
            print("\n🎉 Story publicado!")
            print(f"📱 Veja no app do Instagram → Stories")
            
        else:
            print("\n" + "="*60)
            print("❌ FALHA AO POSTAR STORY")
            print("="*60)
            
            if resultado and resultado.get('erro'):
                print(f"\n⚠️  Erro: {resultado['erro']}")
            
            if resultado and resultado.get('problema'):
                problema = resultado['problema']
                print(f"\n🔍 Problema detectado: {problema['tipo']}")
                print(f"📝 Ação recomendada: {problema['acao_recomendada']}")
        
    except Exception as e:
        print(f"\n❌ Erro ao postar: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        testar_post_story()
    except KeyboardInterrupt:
        print("\n\n👋 Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()