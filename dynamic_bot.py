import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_banyak_halaman():
    print("🤖 Bot Pagination mulai berjalan...")
    
    # KITA NYALAKAN LAYARNYA (Tanpa --headless) agar bisa ditonton
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    
    # 1. Buka halaman pertama
    driver.get("https://quotes.toscrape.com/")
    
    semua_data = [] # Keranjang kosong untuk menampung semua data
    halaman_ke = 1
    
    # 2. Mulai Perulangan (Looping) tanpa henti sampai tombol Next habis
    while True:
        print(f"📄 Sedang menyedot data di Halaman {halaman_ke}...")
        time.sleep(2) # Tunggu sejenak agar halaman termuat sempurna
        
        # Ambil semua blok kutipan di halaman ini
        blok_kutipan = driver.find_elements(By.CLASS_NAME, "quote")
        
        for blok in blok_kutipan:
            # Ekstrak Teks dan Penulisnya
            teks = blok.find_element(By.CLASS_NAME, "text").text
            penulis = blok.find_element(By.CLASS_NAME, "author").text
            
            # Masukkan ke keranjang
            semua_data.append({
                "Kutipan": teks,
                "Penulis": penulis
            })
            
        # 3. Misi Pencarian Tombol "Next"
        try:
            # Mencari tombol dengan tulisan "Next"
            tombol_next = driver.find_element(By.CSS_SELECTOR, "li.next > a")
            tombol_next.click() # KLIK TOMBOLNYA!
            halaman_ke += 1
        except Exception:
            # Jika tombol tidak ditemukan (Error), berarti sudah halaman terakhir
            print("🚫 Tombol Next tidak ditemukan. Ini pasti halaman terakhir!")
            break # Hentikan perulangan
            
    # 4. Selesai dan Simpan Data
    driver.quit()
    print(f"🎉 Selesai! Total data terkumpul: {len(semua_data)} baris.")
    
    # Ubah ke Pandas DataFrame dan simpan ke Excel
    df = pd.DataFrame(semua_data)
    df.to_excel("hasil_10_halaman.xlsx", index=False)
    print("✅ Data berhasil disimpan ke 'hasil_10_halaman.xlsx'")

if __name__ == "__main__":
    scrape_banyak_halaman()