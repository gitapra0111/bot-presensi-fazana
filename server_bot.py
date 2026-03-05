import os
import time
import glob
import threading
from flask import Flask
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv  # <-- Kunci Utama 1: Panggil pembaca .env

# --- HAPUS SENJATA RAHASIA HUGGING FACE ---
# (Kode DNS Bypass dihapus karena laptopmu tidak memblokir Telegram)

# 1. Load variabel rahasia dari file .env di laptopmu
load_dotenv()

# Setup Bot & Flask
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Server Bot Presensi PT Fazana jalan di LOKAL!"

def download_pdf_selenium():
    """Fungsi Scraping dengan pengaturan normal untuk Windows"""
    lokasi_download = os.path.join(os.getcwd(), "hasil_pdf")
    os.makedirs(lokasi_download, exist_ok=True)
    
    for file_lama in glob.glob(os.path.join(lokasi_download, "*.pdf")):
        os.remove(file_lama)

    options = Options()
    
    # --- Kunci Utama 2: HAPUS PATH LINUX ---
    # options.binary_location = '/usr/bin/chromium' (Dihapus)
    
    options.add_argument("--headless=new") # Tetap gaib agar tidak mengganggu layar
    options.add_argument("--window-size=1920,1080")
    
    prefs = {
        "download.default_directory": lokasi_download,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # --- Kunci Utama 3: Biarkan Selenium mencari Chrome di Windows otomatis ---
    # service = Service('/usr/bin/chromedriver') (Dihapus)
    driver = webdriver.Chrome(options=options)
    
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
    bot.reply_to(message, "Halo Bos! 🤖\nSaya asisten yang jalan di laptop lokal. Ketik /rekap untuk minta PDF presensi.")

@bot.message_handler(commands=['rekap'])
def handle_rekap(message):
    bot.reply_to(message, "⏳ Siap! Menerobos server absensi dari Windows... Mohon tunggu 15 detik.")
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
    # 1. Nyalakan Bot Telegram di "jalur" terpisah
    t = threading.Thread(target=run_bot)
    t.start()
    
    # 2. Nyalakan Web Server bohongan (Flask) di terminal VS Code
    app.run(host='0.0.0.0', port=7860)