import os
import time
import glob
import threading
from flask import Flask
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Setup Bot & Flask
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Ini adalah "Pintu Depan" agar server Cloud (Render) tahu aplikasi kita hidup
@app.route('/')
def home():
    return "🤖 Server Bot Presensi PT Fazana 24/7 sedang berjalan normal!"

def download_pdf_selenium():
    """Fungsi Scraping dengan pengaturan khusus Docker/Linux"""
    lokasi_download = os.path.join(os.getcwd(), "hasil_pdf")
    os.makedirs(lokasi_download, exist_ok=True)
    
    for file_lama in glob.glob(os.path.join(lokasi_download, "*.pdf")):
        os.remove(file_lama)

    options = Options()
    options.binary_location = '/usr/bin/chromium' # Kunci utama untuk Docker!
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    prefs = {
        "download.default_directory": lokasi_download,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # ChromeDriver bawaan dari OS Linux
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://pt-fazana-berkah-mulia.infinityfree.me/auth/login.php")
        driver.find_element(By.NAME, "username").send_keys("sagita123")
        driver.find_element(By.NAME, "password").send_keys("sagita123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(4)
        
        driver.get("https://pt-fazana-berkah-mulia.infinityfree.me/admin/presensi/rekap_bulanan.php")
        time.sleep(4)
        
        tombol_pdf = driver.find_element(By.CSS_SELECTOR, "a[href*='export=pdf']")
        driver.get(tombol_pdf.get_attribute("href"))
        
        time.sleep(10)
        
        list_pdf = glob.glob(os.path.join(lokasi_download, "*.pdf"))
        if list_pdf:
            return max(list_pdf, key=os.path.getctime)
        return None
    finally:
        driver.quit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Halo Bos! 🤖\nSaya asisten 24/7 yang hidup di Cloud. Ketik /rekap untuk minta PDF presensi.")

@bot.message_handler(commands=['rekap'])
def handle_rekap(message):
    bot.reply_to(message, "⏳ Siap! Menerobos server absensi dari Cloud... Mohon tunggu 15 detik.")
    file_pdf = download_pdf_selenium()
    
    if file_pdf:
        with open(file_pdf, 'rb') as doc:
            bot.send_document(message.chat.id, doc, caption="✅ Laporan berhasil diambil!")
    else:
        bot.reply_to(message, "🚨 Gagal mengunduh laporan.")

def run_bot():
    """Fungsi agar bot mendengarkan chat terus-menerus"""
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # 1. Nyalakan Bot Telegram di "jalur" terpisah (Thread)
    t = threading.Thread(target=run_bot)
    t.start()
    
    # 2. Nyalakan Server Web Flask di "jalur" utama (Wajib untuk Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)