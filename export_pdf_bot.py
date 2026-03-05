import os
import time
import glob
import telebot # Library baru kita!
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

# 1. LOAD ENVIRONMENT VARIABLES
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Inisialisasi Bot Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def download_pdf_selenium():
    """Fungsi ini khusus bertugas sebagai 'Mesin Scraper' rahasia"""
    lokasi_download = os.path.join(os.getcwd(), "hasil_pdf")
    os.makedirs(lokasi_download, exist_ok=True)
    
    # Bersihkan file lama
    for file_lama in glob.glob(os.path.join(lokasi_download, "*.pdf")):
        os.remove(file_lama)

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": lokasi_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # JALANKAN SECARA GAIB (HEADLESS) agar layar laptop tidak terganggu
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://pt-fazana-berkah-mulia.infinityfree.me/auth/login.php")
        driver.find_element(By.NAME, "username").send_keys("sagita123")
        driver.find_element(By.NAME, "password").send_keys("sagita123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        driver.get("https://pt-fazana-berkah-mulia.infinityfree.me/admin/presensi/rekap_bulanan.php")
        time.sleep(3)
        
        tombol_pdf = driver.find_element(By.CSS_SELECTOR, "a[href*='export=pdf']")
        link_download = tombol_pdf.get_attribute("href")
        driver.get(link_download)
        
        time.sleep(10) # Jeda waktu unduh
        
        list_pdf = glob.glob(os.path.join(lokasi_download, "*.pdf"))
        if list_pdf:
            return max(list_pdf, key=os.path.getctime) # Kembalikan file terbaru
        return None
        
    finally:
        driver.quit()


# ==========================================
# 2. LOGIKA INTERAKSI CHAT TELEGRAM
# ==========================================

# Jika user mengetik /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Halo Bos Sagita! 🤖\nSaya adalah Asisten Presensi PT Fazana Berkah Mulia.\n\nKetik perintah /rekap untuk meminta laporan PDF bulanan terbaru.")

# Jika user mengetik /rekap
@bot.message_handler(commands=['rekap'])
def handle_rekap(message):
    # Bot membalas dulu agar user tidak mengira botnya mati (karena scraping butuh waktu)
    bot.reply_to(message, "⏳ Siap Bos! Menjalankan robot peretas ke server absensi... Mohon tunggu sekitar 15-20 detik ya.")
    
    # Panggil fungsi Selenium
    file_pdf = download_pdf_selenium()
    
    # Setelah Selenium selesai, kirim hasilnya!
    if file_pdf:
        with open(file_pdf, 'rb') as doc:
            bot.send_document(message.chat.id, doc, caption="✅ Ini dia laporan presensi bulanan yang diminta!")
    else:
        bot.reply_to(message, "🚨 Maaf Bos, bot gagal menemukan atau mengunduh file PDF dari server.")

if __name__ == "__main__":
    print("🤖 Asisten Bot sedang menyala dan mendengarkan chat Telegram... (Tekan CTRL+C untuk mematikan)")
    bot.polling(none_stop=True) # Perintah agar bot standby 24 jam!