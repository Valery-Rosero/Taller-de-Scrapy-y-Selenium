from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
from urllib.parse import urljoin


def descargar_html_primer_resultado():
    print("🚀 Iniciando flujo: Inicio ➜ Descubre ➜ 1er resultado ➜ TEXT/HTML")

    # Configuración de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    # Agregar headers para evitar bloqueos
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
    options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1) Página principal
        driver.get("https://www.datos.gov.co/")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("✅ Página principal cargada")

        # 2) Clic en 'Descubre'
        try:
            btn_descubre = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Descubre")))
        except:
            btn_descubre = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href,'/browse') and contains(.,'Descubre')]")
            ))
        btn_descubre.click()
        print("✅ Click en 'Descubre'")

        # 3) Primer resultado
        primer_link = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.entry-name-link[data-testid='view-card-entry-link']")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", primer_link)
        time.sleep(0.5)
        dataset_url = primer_link.get_attribute("href")
        dataset_title = primer_link.text.strip()
        print(f"🔗 Primer dataset: {dataset_title}")
        print(f"🔗 URL: {dataset_url}")
        driver.execute_script("arguments[0].click();", primer_link)

        # 4) Asegurar que estamos en /about_data
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        curr = driver.current_url
        if "/about_data" not in curr:
            if curr.endswith("/"):
                curr = curr[:-1]
            about_url = curr + "/about_data"
            driver.get(about_url)
            time.sleep(2)
        print(f"📄 Página de 'Acerca de estos datos': {driver.current_url}")

        # 5) Buscar enlace de descarga - Múltiples estrategias
        enlace_descarga = None
        
        # Estrategia 1: Buscar enlace directo con texto específico
        try:
            enlace_descarga = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='download-file-link']")
            ))
            print("✅ Encontrado enlace por CSS selector download-file-link")
        except:
            pass
        
        # Estrategia 2: Buscar por clase específica que veo en la imagen
        if not enlace_descarga:
            try:
                enlace_descarga = driver.find_element(By.CSS_SELECTOR, "a.download-file-link.all-caps")
                print("✅ Encontrado enlace por clase download-file-link all-caps")
            except:
                pass
        
        # Estrategia 3: Buscar dentro de forge-button usando shadow DOM
        if not enlace_descarga:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.download-buttons")))
                forge_buttons = driver.find_elements(By.CSS_SELECTOR, "div.download-buttons forge-button")
                
                for fb in forge_buttons:
                    try:
                        enlace = driver.execute_script("""
                            return arguments[0].shadowRoot.querySelector('a.download-file-link.all-caps');
                        """, fb)
                        if enlace and enlace.get_attribute("href"):
                            enlace_descarga = enlace
                            print("✅ Encontrado enlace dentro de Shadow DOM")
                            break
                    except:
                        continue
            except:
                pass
        
        # Estrategia 4: Buscar cualquier enlace que contenga palabras clave de descarga
        if not enlace_descarga:
            try:
                posibles_enlaces = driver.find_elements(By.TAG_NAME, "a")
                for enlace in posibles_enlaces:
                    href = enlace.get_attribute("href")
                    texto = enlace.text.lower()
                    if href and any(word in href.lower() for word in ['download', 'export', 'data']):
                        if any(word in texto for word in ['descargar', 'download', 'exportar', 'datos']):
                            enlace_descarga = enlace
                            print("✅ Encontrado enlace por palabras clave")
                            break
            except:
                pass

        if not enlace_descarga:
            raise Exception("❌ No se pudo encontrar ningún enlace de descarga")

        href = enlace_descarga.get_attribute("href")
        print(f"✅ Enlace de descarga encontrado: {href}")

        # 6) Descargar archivo con requests
        # Asegurar que tenemos una URL completa
        if href.startswith('//'):
            href = 'https:' + href
        elif href.startswith('/'):
            href = urljoin(driver.current_url, href)
        
        print(f"📥 Descargando desde: {href}")
        
        # Headers para simular navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        resp = requests.get(href, timeout=120, headers=headers, allow_redirects=True)
        
        if resp.status_code == 200:
            download_dir = os.path.join(os.getcwd(), "datasets")
            os.makedirs(download_dir, exist_ok=True)
            
            # Determinar extensión basada en Content-Type
            content_type = resp.headers.get('content-type', '').lower()
            if 'html' in content_type:
                extension = '.html'
            elif 'json' in content_type:
                extension = '.json'
            elif 'csv' in content_type:
                extension = '.csv'
            elif 'xml' in content_type:
                extension = '.xml'
            else:
                # Intentar determinar por la URL o usar .html como default
                if '.csv' in href:
                    extension = '.csv'
                elif '.json' in href:
                    extension = '.json'
                elif '.xml' in href:
                    extension = '.xml'
                else:
                    extension = '.html'
            
            # Crear nombre de archivo limpio
            filename = dataset_title.replace(' ', '_').replace('/', '_')[:50] + extension
            out_path = os.path.join(download_dir, filename)
            
            with open(out_path, "wb") as f:
                f.write(resp.content)
            
            file_size = len(resp.content)
            print(f"📥 Archivo descargado exitosamente:")
            print(f"   📁 Ubicación: {out_path}")
            print(f"   📊 Tamaño: {file_size:,} bytes")
            print(f"   🏷️ Tipo de contenido: {content_type}")
            
        else:
            print(f"❌ Error al descargar (status {resp.status_code})")
            print(f"   Respuesta: {resp.text[:200]}...")

        print("🎉 Flujo completado exitosamente")

    except Exception as e:
        import traceback
        print(f"⚠️ Error: {e}")
        print("📋 Detalles del error:")
        print(traceback.format_exc())
    finally:
        time.sleep(1)
        driver.quit()
        print("🛑 Navegador cerrado")


if __name__ == "__main__":
    descargar_html_primer_resultado()