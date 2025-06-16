# FanFocusGPT - Saints & Sinners Chatter Assistant

Un assistente AI avanzato per i chatters che integra il framework S&S (Saints & Sinners) con profili creator personalizzati e sistema KYC strutturato.

## 🎯 Caratteristiche Principali

### Framework Integrato
- **FanFocusGPT**: Sistema KYC a fasi (Phase 0: 9 step + Phase 1 avanzata)
- **S&S Framework**: Segmentazione fan (BS/BO/FT/TW/LK) e strategie conversion
- **Creator Profiles**: 4 profili dettagliati (Ella Blair, Vanp, Yana Sinner, Venessa)

### Funzionalità AI
- **Google AI Integration**: Utilizzo di Gemini 1.5 Flash
- **Profilazione Automatica**: Classificazione automatica fan type
- **KYC Tracking**: Progressione automatica attraverso le fasi KYC
- **Upselling Intelligente**: Suggerimenti contestuali basati su fan type

### Interface Web
- **Interfaccia User-Friendly**: Design moderno e responsivo
- **Real-time Tracking**: Monitoraggio progression KYC e profilo fan
- **Session Management**: Tracking multipli fan simultanei
- **Copy-Paste Ready**: Risposte pronte per l'uso immediato

## 📁 Struttura del Progetto

```
fanfocus-gpt/
├── app.py                 # Applicazione Flask principale
├── models.py              # Modelli dati e strutture
├── prompts.py            # Template prompt e AI integration
├── config.py             # Configurazioni e API settings
├── requirements.txt      # Dipendenze Python
├── README.md            # Questa documentazione
├── templates/
│   ├── base.html        # Template base
│   └── index.html       # Interface principale
└── static/
    ├── css/
    │   └── style.css    # Stili personalizzati
    └── js/
        └── main.js      # JavaScript principale
```

## 🚀 Installazione e Setup

### 1. Preparazione Ambiente

```bash
# Clona o scarica il progetto
cd fanfocus-gpt

# Crea virtual environment (raccomandato)
python -m venv venv

# Attiva virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione

La configurazione è già pronta con la tua API key Google AI. Se necessario, modifica `config.py`:

```python
GOOGLE_AI_API_KEY = "AIzaSyB-eQdOarmEG7xoH3c5p8ottrXdD-I1DVY"
```

### 3. Avvio Locale

```bash
# Avvio development server
python app.py

# L'applicazione sarà disponibile su:
# http://localhost:5000
```

## 🌐 Deploy in Produzione

### Opzione 1: Heroku (Raccomandato per principianti)

1. **Crea account Heroku**: [heroku.com](https://heroku.com)
2. **Installa Heroku CLI**: [Scarica qui](https://devcenter.heroku.com/articles/heroku-cli)

```bash
# Login Heroku
heroku login

# Crea app Heroku
heroku create fanfocus-gpt-[tuo-nome]

# Configura variabili ambiente
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DEBUG=False

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Apri l'app
heroku open
```

### Opzione 2: Railway

1. **Crea account**: [railway.app](https://railway.app)
2. **Connetti GitHub**: Fai upload del codice su GitHub
3. **Deploy automatico**: Railway rileverà automaticamente Flask

### Opzione 3: DigitalOcean App Platform

1. **Crea account**: [digitalocean.com](https://digitalocean.com)
2. **Crea App**: Connetti repository GitHub
3. **Auto-deploy**: Configurazione automatica Flask

### Opzione 4: VPS/Server Dedicato

```bash
# Su server Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nginx

# Clone progetto
git clone [your-repo-url]
cd fanfocus-gpt

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install gunicorn
pip install gunicorn

# Avvia con gunicorn
gunicorn --bind 0.0.0.0:5000 app:app

# Setup Nginx (opzionale)
# Configura Nginx per proxy reverse su porta 80/443
```

## 🔧 Configurazione Avanzata

### Environment Variables

```bash
# Produzione
export SECRET_KEY=your-very-secret-key
export DEBUG=False
export GOOGLE_AI_API_KEY=your-api-key

# Opzionali
export MAX_RESPONSE_LENGTH=250
export KYC_PHASE1_THRESHOLD=70
```

### Personalizzazioni

#### Aggiungere Nuovi Creator
1. Modifica `models.py` in `CREATOR_PROFILES`
2. Aggiungi nuovo profilo creator con tutti i dettagli
3. Aggiorna `config.py` in `CREATOR_MODELS`

#### Modificare KYC Steps
1. Modifica `models.py` nella classe `FanProfile`
2. Aggiorna `kyc_phase0_steps` con nuove domande
3. Modifica `prompts.py` per nuove logiche

#### Personalizzare AI Prompts
1. Modifica `prompts.py` classe `PromptGenerator`
2. Personalizza `fanfocus_system_prompt`
3. Aggiorna logic generation prompts

## 🎮 Utilizzo

### 1. Selezione Creator
- Scegli tra Ella Blair, Vanp, Yana Sinner, Venessa
- Visualizza automaticamente profilo creator con restrizioni

### 2. Tipo Fan
- **New Fan**: Inizia KYC da step 1
- **Existing Fan**: Continua da dati esistenti

### 3. Input Messaggio
- Incolla messaggio fan
- Per fan esistenti: aggiungi note/KYC precedenti

### 4. Generazione Risposta
- AI genera risposta ottimale seguendo:
  - Personalità creator specifica
  - Framework S&S per fan type
  - Progressione KYC strutturata
  - Tone adeguato al confidence level

### 5. Tracking Automatico
- Progressione KYC visualizzata
- Fan type classification automatica
- Suggerimenti upselling contestuali
- History chat memorizzata

## 📊 Funzionalità Avanzate

### S&S Framework Integration
- **Big Spender (BS)**: VIP treatment, custom offers
- **Occasional Buyer (BO)**: Urgency tactics, value propositions  
- **Free Trial (FT)**: Trust-building, low-risk offers
- **Time Waster (TW)**: Quick filtering, minimal engagement
- **Lurker (LK)**: Curiosity hooks, exclusive previews

### KYC Progression
- **Phase 0** (9 steps): Nome, Location, Age, Job, Relationship, Interests, Routine, Goals, Purchase
- **Phase 1** (Advanced): Attivata automaticamente al 70% Phase 0
- **Confidence Levels**: LOW/MED/HIGH con adaptation automatica

### Creator Personalities
- **Ella Blair**: Brazilian GFE, submissive, authentic
- **Vanp**: Dominant, tattooed, split tongue, 37 anni
- **Yana Sinner**: Artist, nerdy, lingerie designer
- **Venessa**: Latina gamer, creative, petite

## 🔒 Sicurezza e Privacy

- API keys protette in environment variables
- Session data gestita in memoria (non persistente)
- Input sanitization per XSS protection
- HTTPS ready per produzione
- Compliance con content policies

## 🐛 Troubleshooting

### Errori Comuni

**API Error**: Verifica API key Google AI sia corretta
```python
# In config.py, controlla:
GOOGLE_AI_API_KEY = "AIzaSyB-eQdOarmEG7xoH3c5p8ottrXdD-I1DVY"
```

**Import Error**: Installa dipendenze
```bash
pip install -r requirements.txt
```

**Port già in uso**: Cambia porta
```bash
python app.py --port 5001
```

### Debug Mode
Per debug dettagliato, modifica `config.py`:
```python
DEBUG = True
```

## 📞 Supporto

Per supporto tecnico o personalizzazioni:
1. Controlla i logs dell'applicazione
2. Verifica la configurazione API
3. Testa con messaggi semplici prima

## 🔄 Aggiornamenti

Il sistema è progettato per essere facilmente espandibile:
- Nuovi creator profiles
- Additional KYC steps  
- Enhanced S&S strategies
- UI/UX improvements
- Multi-language support

## 📝 Note per il Deploy

1. **Prima del deploy**: Testa localmente con tutti i creator
2. **Environment vars**: Configura tutte le variabili necessarie
3. **API limits**: Monitora utilizzo Google AI API
4. **Security**: Cambia SECRET_KEY in produzione
5. **Monitoring**: Setup logging per produzione

---

**🎉 Il tuo FanFocusGPT è pronto! Questo è il primo bot AI completo che integra S&S Framework con creator profiles personalizzati per massimizzare l'efficacia delle conversazioni e le conversioni.**
