import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd # Kita panggil lagi Pandas kesayangan kita

def login_dan_ambil_data():
    print("🔐 Memulai proses Automasi Login & Scraping...")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # 1. BUKA GERBANG & LOGIN
        driver.get("https://the-internet.herokuapp.com/login")
        driver.find_element(By.ID, "username").send_keys("tomsmith")
        driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Tunggu sampai masuk ke area rahasia
        pesan_sukses = wait.until(EC.presence_of_element_located((By.ID, "flash")))
        print("✅ Berhasil menembus keamanan!")
        
        # 2. MENGAMBIL DATA DARI DALAM (Scraping)
        print("🕵️‍♂️ Mulai menyedot data rahasia...")
        judul_rahasia = driver.find_element(By.TAG_NAME, "h2").text
        sub_judul = driver.find_element(By.CLASS_NAME, "subheader").text
        pesan_alert = pesan_sukses.text.strip()
        
        # 3. MENGAMBIL SCREENSHOT BUKTI
        # Ini ilmu baru: Menyuruh bot memfoto layar!
        driver.save_screenshot("bukti_login.png")
        print("📸 Screenshot dashboard berhasil disimpan sebagai 'bukti_login.png'")
        
        # 4. SIMPAN DATA KE EXCEL
        data_rahasia = [{
            "Judul Halaman": judul_rahasia,
            "Sub Judul": sub_judul,
            "Pesan Server": pesan_alert
        }]
        df = pd.DataFrame(data_rahasia)
        df.to_excel("data_rahasia.xlsx", index=False)
        print("💾 Data rahasia berhasil disimpan ke 'data_rahasia.xlsx'")
        
        # 5. LOGOUT (Sopan santun berinternet)
        time.sleep(2) # Tahan sebentar biar kelihatan
        driver.find_element(By.CSS_SELECTOR, "a.button.secondary.radius").click()
        print("🚪 Berhasil Logout dengan aman.")
        
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
    finally:
        time.sleep(2)
        driver.quit()
        print("🛑 Browser ditutup.")

if __name__ == "__main__":
    login_dan_ambil_data()