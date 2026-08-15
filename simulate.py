#!/usr/bin/env python3
"""
Benares Traffic Simulator
- Cerca su Google tramite SerpApi
- Visita il sito con Playwright Stealth
- Simula comportamento umano con proxy residenziali
"""

import os
import random
import time
import asyncio
import logging
from datetime import datetime
from urllib.parse import urlparse

import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth

# Configurazione Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURAZIONE (da variabili d'ambiente)
# ============================================

SERP_API_KEY = os.environ.get('SERP_API_KEY')
PROXY_USERNAME = os.environ.get('PROXY_USERNAME')
PROXY_PASSWORD = os.environ.get('PROXY_PASSWORD')
PROXY_HOST = os.environ.get('PROXY_HOST', 'proxy.geonode.com')
PROXY_PORT = os.environ.get('PROXY_PORT', '8080')

YOUR_DOMAIN = 'benaresfilm.com'
KEYWORDS = [
    'benaresfilm pierre loti spiritualità india',
    'benaresfilm india misticismo',
    'benaresfilm varanasi cinema letteratura',
    'benaresfilm pierre loti india sacra',
    'benaresfilm spiritualità indiana'
]

# ============================================
# 1. RICERCA SU GOOGLE (SERP API)
# ============================================

def search_google(keyword):
    """
    Cerca su Google tramite SerpApi
    Restituisce il primo URL del dominio benaresfilm.com trovato
    """
    if not SERP_API_KEY:
        logger.error("❌ SERP_API_KEY non configurata")
        return None

    # Usa SerpApi (versione gratuita o a pagamento)
    # Se hai SerpApi gratis, usa questo endpoint:
    url = "https://serpapi.com/search"
    
    params = {
        'api_key': SERP_API_KEY,
        'q': keyword,
        'num': 10,
        'device': 'desktop',
        'location': 'Italy',
        'hl': 'it'
    }
    
    try:
        logger.info(f"🔍 Ricerca Google: '{keyword}'")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Cerca il primo link che contiene il dominio
        for result in data.get('organic_results', []):
            link = result.get('link', '')
            if YOUR_DOMAIN in link:
                logger.info(f"✅ Trovato: {link}")
                return link
        
        logger.warning(f"⚠️ Nessun risultato per il dominio in: {keyword}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Errore SERP API: {e}")
        return None

# ============================================
# 2. VISITA SIMULATA (Playwright Stealth)
# ============================================

async def simulate_visit(url, proxy_url):
    """
    Visita un URL simulando un utente reale
    Usa Playwright con Stealth e proxy
    """
    if not url:
        return False
    
    logger.info(f"🌐 Simulo visita: {url}")
    logger.info(f"   Proxy: {proxy_url[:50]}...")
    
    async with async_playwright() as p:
        try:
            # Configura il browser con il proxy
            browser = await p.chromium.launch(
                headless=True,  # False per debug, True per produzione
                proxy={
                    "server": proxy_url
                },
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # Crea un contesto con User-Agent casuale
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.5 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36'
            ]
            user_agent = random.choice(user_agents)
            
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={
                    'width': random.randint(1024, 1920),
                    'height': random.randint(768, 1080)
                },
                locale='it-IT',
                timezone_id='Europe/Rome'
            )
            
            page = await context.new_page()
            
            # Applica Stealth per nascondere l'automazione
			await stealth(page)

            # Naviga alla pagina
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # === SIMULA COMPORTAMENTO UMANO ===
            
            # 1. Scrolla lentamente (simula la lettura)
            logger.info("   📜 Scrolling...")
            for _ in range(random.randint(3, 8)):
                scroll_amount = random.randint(200, 600)
                await page.mouse.wheel(delta_y=scroll_amount)
                await asyncio.sleep(random.uniform(0.8, 2.5))
            
            # 2. Clicca su un link interno (se presente)
            logger.info("   👆 Cerca link interno...")
            internal_links = await page.query_selector_all(
                'a[href^="/"], a[href*="benaresfilm.com"]'
            )
            
            if internal_links:
                # Filtra link che non sono vuoti o di navigazione
                valid_links = []
                for link in internal_links:
                    href = await link.get_attribute('href')
                    if href and len(href) > 3 and not href.startswith('#'):
                        valid_links.append(link)
                
                if valid_links and random.random() < 0.6:  # 60% di probabilità
                    random_link = random.choice(valid_links)
                    try:
                        if await random_link.is_visible():
                            href = await random_link.get_attribute('href')
                            logger.info(f"   🔗 Clicca su: {href}")
                            await random_link.click()
                            await page.wait_for_load_state('networkidle', timeout=10000)
                            await asyncio.sleep(random.uniform(2, 5))
                            await page.go_back()
                            await page.wait_for_load_state('networkidle')
                    except Exception as e:
                        logger.debug(f"   ⚠️ Errore click: {e}")
            
            # 3. Attesa finale e chiusura
            wait_time = random.uniform(5, 15)
            logger.info(f"   ⏳ Attendo {wait_time:.1f} secondi...")
            await asyncio.sleep(wait_time)
            
            await browser.close()
            logger.info("✅ Visita completata con successo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore durante la visita: {e}")
            try:
                await browser.close()
            except:
                pass
            return False

# ============================================
# 3. FUNZIONE PRINCIPALE
# ============================================

async def main():
    """Esegue il flusso completo"""
    logger.info("=" * 60)
    logger.info("🚀 BENARES TRAFFIC SIMULATOR")
    logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Verifica configurazione
    if not SERP_API_KEY:
        logger.error("❌ SERP_API_KEY non configurata come variabile d'ambiente")
        return
    
    if not PROXY_USERNAME or not PROXY_PASSWORD:
        logger.error("❌ Credenziali proxy non configurate")
        return
    
    # Costruisci URL proxy
    proxy_url = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
    
    # Scegli una parola chiave casuale
    keyword = random.choice(KEYWORDS)
    logger.info(f"🔑 Parola chiave: '{keyword}'")
    
    # 1. Cerca su Google
    target_url = search_google(keyword)
    if not target_url:
        logger.warning("⚠️ Nessun URL trovato. Riprovo con un'altra keyword...")
        # Prova con un'altra keyword
        for fallback_keyword in KEYWORDS:
            if fallback_keyword != keyword:
                target_url = search_google(fallback_keyword)
                if target_url:
                    break
    
    if not target_url:
        logger.error("❌ Impossibile trovare il sito su Google")
        return
    
    # 2. Visita il sito
    success = await simulate_visit(target_url, proxy_url)
    
    if success:
        logger.info("✅ Flusso completato con successo")
    else:
        logger.warning("⚠️ Flusso completato con errori")

# ============================================
# 4. ENTRY POINT
# ============================================

if __name__ == "__main__":
    asyncio.run(main())
