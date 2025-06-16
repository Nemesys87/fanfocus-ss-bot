#!/usr/bin/env python3
"""
Test script per verificare che tutto funzioni correttamente
"""

import sys
import os

def test_imports():
    """Test che tutti i moduli si importino correttamente"""
    try:
        from models import FanProfile, CREATOR_PROFILES, SessionManager
        from prompts import PromptGenerator, SSFrameworkEngine
        from config import Config
        print("✅ Tutti i moduli importati correttamente")
        return True
    except ImportError as e:
        print(f"❌ Errore import: {e}")
        return False

def test_config():
    """Test configurazione"""
    try:
        from config import Config
        api_key = Config.GOOGLE_AI_API_KEY
        if api_key and len(api_key) > 20:
            print(f"✅ API Key configurata correttamente (***{api_key[-5:]})")
        else:
            print("❌ API Key non configurata correttamente")
            return False

        print(f"✅ Model: {Config.GOOGLE_AI_MODEL}")
        print(f"✅ Creator models: {len(Config.CREATOR_MODELS)}")
        return True
    except Exception as e:
        print(f"❌ Errore configurazione: {e}")
        return False

def test_creator_profiles():
    """Test profili creator"""
    try:
        from models import CREATOR_PROFILES

        expected_creators = ['ella', 'vanp', 'yana', 'venessa']
        for creator_key in expected_creators:
            if creator_key in CREATOR_PROFILES:
                creator = CREATOR_PROFILES[creator_key]
                print(f"✅ {creator.name} - {len(creator.personality_traits)} traits, {len(creator.restrictions)} restrictions")
            else:
                print(f"❌ Creator {creator_key} mancante")
                return False
        return True
    except Exception as e:
        print(f"❌ Errore profili creator: {e}")
        return False

def test_prompt_generator():
    """Test generatore prompt"""
    try:
        from models import FanProfile, FanStatus
        from prompts import PromptGenerator

        # Crea fan profile di test
        fan = FanProfile(fan_id="test123", status=FanStatus.NEW)

        # Test generatore
        generator = PromptGenerator()
        system_prompt = generator.generate_system_prompt("ella", fan)
        user_prompt = generator.generate_user_prompt("Hello there!", "ella", fan)

        if len(system_prompt) > 100 and len(user_prompt) > 10:
            print("✅ Prompt generator funziona correttamente")
            print(f"  - System prompt: {len(system_prompt)} caratteri")
            print(f"  - User prompt: {len(user_prompt)} caratteri")
            return True
        else:
            print("❌ Prompt troppo corti")
            return False
    except Exception as e:
        print(f"❌ Errore prompt generator: {e}")
        return False

def test_session_manager():
    """Test session manager"""
    try:
        from models import SessionManager, FanStatus

        manager = SessionManager()
        fan = manager.create_or_get_fan("test456", FanStatus.NEW)

        if fan.fan_id == "test456" and fan.status == FanStatus.NEW:
            print("✅ Session manager funziona correttamente")
            return True
        else:
            print("❌ Session manager non funziona")
            return False
    except Exception as e:
        print(f"❌ Errore session manager: {e}")
        return False

def test_file_structure():
    """Test struttura file"""
    required_files = [
        'app.py',
        'models.py', 
        'prompts.py',
        'config.py',
        'requirements.txt',
        'README.md',
        'templates/base.html',
        'templates/index.html',
        'static/css/style.css',
        'static/js/main.js'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if not missing_files:
        print("✅ Tutti i file richiesti sono presenti")
        return True
    else:
        print(f"❌ File mancanti: {missing_files}")
        return False

def main():
    """Esegui tutti i test"""
    print("🧪 Avvio test FanFocusGPT...\n")

    tests = [
        ("Struttura File", test_file_structure),
        ("Import Moduli", test_imports),
        ("Configurazione", test_config),
        ("Profili Creator", test_creator_profiles),
        ("Prompt Generator", test_prompt_generator),
        ("Session Manager", test_session_manager)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Errore inaspettato in {test_name}: {e}")
            failed += 1

    print(f"\n📊 Risultati Test:")
    print(f"✅ Passati: {passed}")
    print(f"❌ Falliti: {failed}")

    if failed == 0:
        print("\n🎉 Tutti i test passati! FanFocusGPT è pronto per il deploy!")
        print("\nPer avviare l'applicazione:")
        print("python app.py")
    else:
        print(f"\n⚠️  {failed} test falliti. Controlla gli errori sopra.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
