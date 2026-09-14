# 1. تحديد صورة بايثون الأساسية
FROM python:3.11-slim

# 2. تحديد مجلد العمل داخل الـ Container
WORKDIR /app

# 3. نسخ ملف المكتبات أولاً للاستفادة من الـ Cache
COPY requirements.txt .

# 4. تثبيت المكتبات داخل الـ Container
RUN pip install --no-cache-dir -r requirements.txt

# 5. نسخ بقية كود المشروع
COPY . .

# 6. فتح المنفذ الذي يعمل عليه السيرفر
EXPOSE 8000

# 7. الأمر الذي سيتم تشغيله عند بدء الـ Container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]