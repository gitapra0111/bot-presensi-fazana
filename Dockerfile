# 1. Gunakan komputer Linux dengan Python
FROM python:3.10-slim

# 2. Install Chromium Browser & Driver-nya
RUN apt-get update && apt-get install -y chromium chromium-driver

# 3. Buat folder kerja
WORKDIR /app

# 4. Pindahkan semua file proyekmu ke dalam server
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 5. Beritahu server cara menyalakannya
CMD ["python", "server_bot.py"]