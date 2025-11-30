"""
Teste de Post de Foto - Instagram Automation Pro
Script para testar post de foto no feed
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
from instagrapi import Client


def listar_fotos():
    """Lista todas as fotos disponíveis no cache"""
    fotos = []
    
    # Procurar em todas as pastas
    for pasta in ['cache_local/feed', 'cache_local/reels', 'cache_local/stories', 'cache_local']:
        pasta_path = Path(pasta)
        if pasta_path.exists():
            # Formatos de imagem suportados
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.avif', '*.webp']:
                fotos.extend(list(pasta_path.glob(ext)))
    
    return fotos


def testar_post_foto():
    """Testa post de foto no feed"""
    print("="*60)
    print("📸 TESTE DE POST - FOTO NO FEED")
    print("="*60)
    
    # 1. Listar fotos disponíveis
    print("\n🖼️  Buscando fotos no cache...")
    fotos = listar_fotos()
    
    if not fotos:
        print("\n❌ Nenhuma foto encontrada!")
        print("\nColoque fotos (JPG, PNG, AVIF) em:")
        print("  - cache_local/feed/")
        print("  - cache_local/")
        return
    
    print(f"\n✅ {len(fotos)} foto(s) encontrada(s):")
    for i, foto in enumerate(fotos, 1):
        print(f"{i}. {foto.name} ({foto.stat().st_size / 1024:.1f} KB)")
    
    # 2. Escolher foto
    escolha = input("\nEscolha o número da foto (Enter para a primeira): ").strip()
    
    if escolha:
        try:
            index = int(escolha) - 1
            if index < 0 or index >= len(fotos):
                print("❌ Número inválido!")
                return
        except ValueError:
            print("❌ Digite um número válido!")
            return
    else:
        index = 0
    
    foto_path = str(fotos[index])
    print(f"\n📸 Foto selecionada: {fotos[index].name}")
    
    # 3. Carregar conta
    with open('config/contas.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if not config['contas']:
        print("\n❌ Nenhuma conta encontrada em config/contas.json")
        return
    
    conta = config['contas'][0]  # Usa primeira conta
    print(f"👤 Usando conta: @{conta['username']}")
    
    # 4. Carregar legenda e hashtags
    with open('config/legendas.json', 'r', encoding='utf-8') as f:
        legendas = json.load(f)['legendas']
    
    with open('config/hashtags.json', 'r', encoding='utf-8') as f:
        hashtags = json.load(f)['hashtags']
    
    legenda = random.choice(legendas)
    hashtag = random.choice(hashtags)
    
    print(f"\n📝 Legenda: {legenda[:50]}...")
    print(f"#️⃣  Hashtags: {hashtag[:50]}...")
    
    # 5. Confirmar
    print("\n" + "="*60)
    print("⚠️  ATENÇÃO: Isso vai REALMENTE POSTAR na sua conta!")
    print("="*60)
    confirma = input("\nTem certeza? Digite 'SIM' para confirmar: ").strip().upper()
    
    if confirma != 'SIM':
        print("\n❌ Post cancelado!")
        return
    
    # 6. Inicializar módulos
    print("\n📦 Inicializando sistema...")
    humanizer = Humanizer(nivel='alto')
    detector = Detector()
    telegram_bot = TelegramBot()
    poster = Poster(humanizer, detector, telegram_bot)
    
    # 7. Fazer login
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
        
        # 8. POSTAR FOTO!
        print("\n" + "="*60)
        print("📤 POSTANDO FOTO NO FEED...")
        print("="*60)
        
        # Comportamento humano pré-post
        print("\n🤖 Simulando comportamento humano...")
        humanizer.comportamento_pre_post(client)
        
        # Combinar legenda e hashtags
        caption = f"{legenda}\n\n{hashtag}".strip()
        
        # Simular digitação
        print("⌨️  Simulando digitação...")
        humanizer.simular_digitacao(caption)
        
        # Delay antes de postar
        print("⏳ Aguardando...")
        humanizer.delay_curto()
        
        # POSTAR!
        print("\n📤 Enviando foto...")
        media = client.photo_upload(foto_path, caption)
        
        # Comportamento pós-post
        humanizer.comportamento_pos_post(client)
        
        # SUCESSO!
        print("\n" + "="*60)
        print("✅ FOTO POSTADA COM SUCESSO!")
        print("="*60)
        print(f"\n📊 Detalhes:")
        print(f"  • Media ID: {media.pk}")
        print(f"  • URL: https://instagram.com/p/{media.code}/")
        print(f"  • Legenda: {legenda[:50]}...")
        
        # Notificar Telegram
        if telegram_bot.enabled:
            telegram_bot.notificar_post_sucesso(
                conta['username'],
                'feed',
                fotos[index].name
            )
        
        print("\n🎉 Post realizado com sucesso!")
        print(f"🔗 Veja em: https://instagram.com/p/{media.code}/")
        
    except Exception as e:
        print(f"\n❌ Erro ao postar: {e}")
        import traceback
        traceback.print_exc()
        
        # Analisar erro
        problema = detector.analisar_erro(str(e))
        if problema:
            print(f"\n⚠️  Problema detectado: {problema['tipo']}")
            print(f"📝 Ação recomendada: {problema['acao_recomendada']}")


if __name__ == "__main__":
    try:
        testar_post_foto()
    except KeyboardInterrupt:
        print("\n\n👋 Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()