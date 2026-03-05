import os
import time
import glob
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 1. LOAD ENVIRONMENT VARIABLES DARI .ENV
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def kirim_pesan(pesan):
    """Fungsi kirim pesan teks ke Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": pesan})

def kirim_file(filepath):
    """Fungsi kirim file dokumen ke Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filepath, 'rb') as file:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID}, files={'document': file})

def jalankan_tugas_bulanan():
    print("🚀 Memulai proses scraping PDF di Cloud Server (Mode Headless)...")
    
    # 2. SETUP FOLDER DOWNLOAD ABSOLUT (Sangat penting untuk Linux Server)
    lokasi_download = os.path.join(os.getcwd(), "hasil_pdf_cloud")
    os.makedirs(lokasi_download, exist_ok=True)
    
    # Bersihkan file sisa bulan lalu (jika ada)
    for file_lama in glob.glob(os.path.join(lokasi_download, "*.pdf")):
        os.remove(file_lama)
    
    # 3. PENGATURAN KHUSUS SERVER HEADLESS (LINUX UBUNTU)
    options = Options()
    options.add_argument("--headless=new") # Wajib: Jalan tanpa buka jendela browser
    options.add_argument("--no-sandbox")   # Wajib: Bypass OS security model di Linux
    options.add_argument("--disable-dev-shm-usage") # Wajib: Atasi masalah memori terbatas di server Cloud
    options.add_argument("--window-size=1920,1080")
    
    # Aturan agar langsung download PDF tanpa nanya "Save As"
    prefs = {
        "download.default_directory": lokasi_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 4. TAHAP LOGIN KE SISTEM PT FAZANA
        print("🔐 Melakukan autentikasi...")
        driver.get("https://pt-fazana-berkah-mulia.infinityfree.me/auth/login.php")
        driver.find_element(By.NAME, "username").send_keys("sagita123")
        driver.find_element(By.NAME, "password").send_keys("sagita123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(4) # Tunggu loading dashboard
        
        # 5. MENUJU HALAMAN REKAP & DOWNLOAD
        print("📂 Membuka halaman rekap...")
        driver.get("https://pt-fazana-berkah-mulia.infinityfree.me/admin/presensi/rekap_bulanan.php")
        time.sleep(4) # Tunggu tabel selesai dimuat
        
        print("📥 Mengunduh dokumen PDF...")
        tombol_pdf = driver.find_element(By.CSS_SELECTOR, "a[href*='export=pdf']")
        
        # Eksekusi URL download
        link_download = tombol_pdf.get_attribute("href")
        driver.get(link_download)
        
        print("⏳ Menunggu unduhan selesai... (10 detik)")
        time.sleep(10) 
        
        # 6. CARI FILE TERBARU & KIRIM KE TELEGRAM
        list_pdf = glob.glob(os.path.join(lokasi_download, "*.pdf"))
        if list_pdf:
            file_terbaru = max(list_pdf, key=os.path.getctime)
            nama_file = os.path.basename(file_terbaru)
            print(f"✅ File {nama_file} siap dikirim!")
            
            kirim_pesan("📅 *Laporan Presensi Otomatis (Cloud Server)*\n\nData absensi bulan ini telah berhasil di-generate oleh sistem otomatis tanpa perlu menyalakan laptop!")
            kirim_file(file_terbaru)
            print("🎉 Notifikasi dan file sukses terkirim ke Telegram.")
        else:
            print("🚨 File PDF tidak ditemukan di folder download.")
            kirim_pesan("🚨 *Alert System:* Cloud Bot gagal menemukan file PDF setelah proses unduh.")
            
    except Exception as e:
        print(f"❌ Terjadi Error: {e}")
        kirim_pesan(f"🚨 *Error Cloud Bot:* Terjadi kendala saat scraping.\nLog: {e}")
        
    finally:
        driver.quit()
        print("🛑 Browser ditutup.")

if __name__ == "__main__":
    jalankan_tugas_bulanan()