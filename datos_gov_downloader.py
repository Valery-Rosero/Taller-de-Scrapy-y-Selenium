from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import glob

def descargar_dataset_datos_gov():

    print("🚀 Iniciando automatización de datos.gov.co...")
    
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')

    download_path = os.path.join(os.getcwd(), 'datasets')
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        print(f"📁 Carpeta creada: {download_path}")
    
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = None
    try:
        print("🌐 Inicializando navegador Chrome...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        print("🌐 Accediendo a https://www.datos.gov.co/ ...")
        driver.get('https://www.datos.gov.co/')
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ Página cargada correctamente")
        
        print("👉 Buscando sección 'DESCUBRE'...")
        
        selectores_descubre = [
            "//a[contains(text(), 'DESCUBRE')]",
            "//button[contains(text(), 'DESCUBRE')]",
            "//div[contains(text(), 'DESCUBRE')]",
            "//span[contains(text(), 'DESCUBRE')]",
            "//*[contains(@class, 'discover')]",
            "//*[contains(@href, 'discover')]"
        ]
        
        descubre_encontrado = False
        for selector in selectores_descubre:
            try:
                descubre_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                descubre_btn.click()
                print(f"✅ Click en DESCUBRE con selector: {selector}")
                descubre_encontrado = True
                break
            except:
                continue
        
        if not descubre_encontrado:
            print("⚠️ No se encontró DESCUBRE, intentando con búsqueda directa...")
            driver.get('https://www.datos.gov.co/browse')
        
        print("⏳ Esperando que carguen los datasets...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/dataset/'], .dataset-item, .asset-card"))
        )
        
        print("📋 Seleccionando el primer dataset...")
        
        selectores_dataset = [
            "a[href*='/dataset/']",
            ".dataset-heading a",
            ".asset-card a",
            ".entry-name a",
            "h3 a",
            "a.title"
        ]
        
        primer_dataset = None
        for selector in selectores_dataset:
            try:
                datasets = driver.find_elements(By.CSS_SELECTOR, selector)
                if datasets:
                    primer_dataset = datasets[0]
                    print(f"✅ Dataset encontrado con selector: {selector}")
                    break
            except:
                continue
        
        if primer_dataset:
            primer_dataset.click()
        else:
            print("❌ No se pudo encontrar ningún dataset")
            return
        
        print("⏳ Cargando página del dataset...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".resource-item, .download-button, [data-format]"))
        )
        
        print("🔎 Buscando botón TEXT/CSV...")
        
        botones_csv = driver.find_elements(By.XPATH, "//*[contains(text(), 'TEXT/CSV') or contains(text(), 'CSV')]")
        
        if not botones_csv:
            recursos = driver.find_elements(By.CSS_SELECTOR, ".resource-item, [data-format]")
            for recurso in recursos:
                texto = recurso.text.upper()
                if 'CSV' in texto:
                    botones_csv = [recurso]
                    break
        
        descargado = False
        if botones_csv:
            for boton in botones_csv:
                if boton.is_displayed():
                    print("📥 Haciendo clic en TEXT/CSV...")
                    boton.click()
                    descargado = True
                    break
        
        if not descargado:
            print("⚠️ No se encontró TEXT/CSV, buscando cualquier CSV...")
            enlaces_csv = driver.find_elements(By.XPATH, "//a[contains(@href, '.csv') or contains(@href, 'format=csv')]")
            if enlaces_csv:
                enlaces_csv[0].click()
                descargado = True
        
        if descargado:
            print("⏳ Esperando que se complete la descarga...")
            time.sleep(15)
            
            archivos_descargados = glob.glob(os.path.join(download_path, '*'))
            if archivos_descargados:
                archivo_mas_reciente = max(archivos_descargados, key=os.path.getctime)
                print(f"✅ Descarga completada: {os.path.basename(archivo_mas_reciente)}")
                print(f"📂 Guardado en: {archivo_mas_reciente}")
                
                tamaño = os.path.getsize(archivo_mas_reciente)
                print(f"📊 Tamaño: {tamaño} bytes")
            else:
                print("⚠️ No se detectaron archivos descargados")
        else:
            print("❌ No se pudo iniciar la descarga")
        
        print("🎉 Proceso completado!")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(f"🔍 Detalles: {traceback.format_exc()}")
    
    finally:
        if driver:
            time.sleep(2)
            driver.quit()
            print("🛑 Navegador cerrado")

if __name__ == "__main__":
    descargar_dataset_datos_gov()