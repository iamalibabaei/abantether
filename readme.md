# Abantether
بهتر است apiهای مربوط به auth و همینطور مدل account به یک اپ دیگر منتفل شود اما بخاطر سادگی و اسکوپ پروژه تستی، در یک فایل و اپلیکیشن هندل شد.
مقدار دیباگ در پروداکشن هم مساوی ۱ است تا برای لود شدن استاتیک فایل‌ها نیازی به nginx یا چیزهای مشابه نداشته باشیم.
برای پروداکشن می‌توان از gunicorn استفاده کرد.

برای ران کردن پروژه باید یک سیستم که داکر روی آن نصب شده داشته باشید. سپس 
```
sudo docker-compose up -d --build 
```
را زده و در آدرس
```
http://0.0.0.0:8000/
```
به پروژه دسترسی خواهید داشت.

برای لاگین کردن می‌توانید از پنل ادمین استفاده کنید. یک کاربر با نام کاربری admin و پسورد verysecurepassword برای شما ایجاد شده است.

