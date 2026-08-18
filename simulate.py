#!/usr/bin/env python3
"""
Benares Traffic Simulator - Versione Playwright senza stealth_async
"""

import os
import sys
import random
import asyncio
import logging
from datetime import datetime
import time

def casual_delay():
    """
    Aggiunge un ritardo casuale tra 1 e 59 minuti
    Così l'esecuzione non parte esattamente allo stesso minuto
    """
    minuti = random.randint(1, 59)
    secondi = minuti * 60
    
    # Aggiunge anche secondi extra per maggiore variabilità
    secondi_extra = random.randint(0, 59)
    totale_secondi = secondi + secondi_extra
    
    logger.info(f"⏰ Attendo {minuti} minuti e {secondi_extra} secondi...")
    time.sleep(totale_secondi)
    logger.info("✅ Attesa completata, avvio simulazione")

import requests
from playwright.async_api import async_playwright

# Configurazione Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# VARIABILI D'AMBIENTE
# ============================================

SERP_API_KEY = os.environ.get('SERP_API_KEY')
PROXY_USERNAME = os.environ.get('PROXY_USERNAME')
PROXY_PASSWORD = os.environ.get('PROXY_PASSWORD')
PROXY_HOST = os.environ.get('PROXY_HOST', 'prod-proxy.geonode.io')
PROXY_PORT = os.environ.get('PROXY_PORT', '9000')

YOUR_DOMAIN = 'benaresfilm.com'
KEYWORDS = [
    'pierre loti spiritualità india',
    'benares india misticismo film',
    'benares varanasi cinema letteratura',
    'pierre loti india sacra',
    'benares spiritualità indiana film'
]

# ============================================
# 1. RICERCA SU GOOGLE (SERP API)
# ============================================

def search_google(keyword):
    if not SERP_API_KEY:
        logger.error("? SERP_API_KEY non configurata")
        return None

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
        logger.info(f"? Ricerca Google: '{keyword}'")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        for result in data.get('organic_results', []):
            link = result.get('link', '')
            if YOUR_DOMAIN in link:
                logger.info(f"? Trovato: {link}")
                return link
        
        logger.warning(f"?? Nessun risultato per il dominio in: {keyword}")
        return None
        
    except Exception as e:
        logger.error(f"? Errore SERP API: {e}")
        return None

# ============================================
# 2. VISITA SIMULATA (Playwright senza stealth)
# ============================================

async def simulate_visit(url, proxy_url):
    if not url:
        return False
    
    logger.info(f"? Simulo visita: {url}")
    
    async with async_playwright() as p:
        try:
            # Avvia browser con proxy
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": proxy_url},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # User-Agent casuale
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.5 Safari/605.1.15',
            ]
            
            context = await browser.new_context(
                user_agent=random.choice(user_agents),
                viewport={'width': random.randint(1024, 1920), 'height': random.randint(768, 1080)},
                locale='it-IT',
                timezone_id='Europe/Rome'
            )
            
            page = await context.new_page()
            
            # Nasconde il segno di automazione (senza playwright-stealth)
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # Vai alla pagina
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Scrolla lentamente
            logger.info("   ? Scrolling...")
            for _ in range(random.randint(3, 8)):
                await page.mouse.wheel(delta_x=0, delta_y=random.randint(200, 600))
                await asyncio.sleep(random.uniform(0.8, 2.5))
            
            # Clicca su un link interno (se presente)
            logger.info("   ? Cerca link interno...")
            links = await page.query_selector_all('a[href^="/"], a[href*="benaresfilm.com"]')
            if links and random.random() < 0.6:
                valid_links = []
                for link in links:
                    href = await link.get_attribute('href')
                    if href and len(href) > 3 and not href.startswith('#'):
                        valid_links.append(link)
                
                if valid_links:
                    random_link = random.choice(valid_links)
                    try:
                        if await random_link.is_visible():
                            href = await random_link.get_attribute('href')
                            logger.info(f"   ? Clicca su: {href}")
                            await random_link.click()
                            await page.wait_for_load_state('networkidle', timeout=10000)
                            await asyncio.sleep(random.uniform(2, 5))
                            await page.go_back()
                            await page.wait_for_load_state('networkidle')
                    except Exception as e:
                        logger.debug(f"   ?? Errore click: {e}")
            
            # Attesa finale
            wait_time = random.uniform(5, 15)
            logger.info(f"   ? Attendo {wait_time:.1f} secondi...")
            await asyncio.sleep(wait_time)
            
            await browser.close()
            logger.info("? Visita completata")
            return True
            
        except Exception as e:
            logger.error(f"? Errore durante la visita: {e}")
            try:
                await browser.close()
            except:
                pass
            return False

# ============================================
# 3. FUNZIONE PRINCIPALE
# ============================================

async def main():
    logger.info("=" * 60)
    logger.info("🚀 BENARES TRAFFIC SIMULATOR")
    logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # === RITARDO CASUALE ===
    # Solo se non siamo in esecuzione manuale
    if not os.environ.get('MANUAL_RUN'):
        casual_delay()
    
    if not SERP_API_KEY:
        logger.error("? SERP_API_KEY mancante")
        return
    
    proxy_url = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
    keyword = random.choice(KEYWORDS)
    logger.info(f"? Parola chiave: '{keyword}'")
    
    target_url = search_google(keyword)
    if not target_url:
        for fallback in KEYWORDS:
            if fallback != keyword:
                target_url = search_google(fallback)
                if target_url:
                    break
    
    if not target_url:
        logger.error("? Impossibile trovare il sito su Google")
        return
    
    await simulate_visit(target_url, proxy_url)
    logger.info("? Flusso completato")

if __name__ == "__main__":
    asyncio.run(main())
