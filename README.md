# RoOtIt VPN IP LIMIT

> به یاد جاویدنامان ۱۸۱۹ دی

محدودکننده IP همزمان برای پنل **PasarGuard** با مدیریت از طریق تلگرام  

پشتیبانی / Support: [t.me/AZROOT94](https://t.me/AZROOT94)

---

## فارسی

### این ابزار چه کاری می‌کند؟

- IPهای آنلاین هر کاربر VPN را از طریق PasarGuard / Xray می‌خواند
- محدودیت تعداد IP همزمان را اعمال می‌کند (فیلد `HWID Limit` هر کاربر، یا حد پیش‌فرض کلی)
- ربات تلگرام با منوی فارسی برای مدیریت دارد
- حالت پیش‌فرض: اگر کاربر بیش از حد مجاز IP داشته باشد، اکانت **غیرفعال می‌ماند** تا ادمین دستی فعالش کند

بعد از نصب، **محافظ IP خاموش** است تا خودتان از منوی تلگرام روشنش کنید.

### پیش‌نیازها

- سرور لینوکس با `systemd`
- API پنل پاسارگارد (پیش‌فرض `http://127.0.0.1:8000`)
- API Key پنل پاسارگارد
- Python 3
- ربات تلگرام خودتان از [@BotFather](https://t.me/BotFather)

### نصب

```bash
git clone https://github.com/rootitdev/rootit-vpn-ip-limit.git
cd rootit-vpn-ip-limit
sudo bash install.sh
sudo vpn-ip-limit setup
```

در `setup` این‌ها را وارد می‌کنید:

1. Bot Token
2. Bot Username
3. Admin User ID(ها) — اختیاری
4. رمز ورود ادمین (قابل اشتراک با افراد مورد اعتماد)

### استفاده از تلگرام

1. ربات را باز کنید
2. `/start` بفرستید
3. رمز ورود ادمین را بفرستید (اگر User ID شما در لیست ادمین باشد، مستقیم منو باز می‌شود)
4. از منوی فارسی استفاده کنید

دکمه‌های مهم:

- وضعیت کاربران و IPها
- کاربران بیش‌ازحد IP
- تنظیم حد IP کاربر
- فعال / غیرفعال کردن کاربر VPN
- روشن / خاموش کردن محافظ IP

### دستورات CLI

```bash
vpn-ip-limit              # راهنما
vpn-ip-limit status       # فقط گزارش (قطع نمی‌کند)
vpn-ip-limit setup        # تنظیم / سینک ربات تلگرام
vpn-ip-limit diag         # گزارش عیب‌یابی کامل
vpn-ip-limit log          # لاگ عملیات قطع کاربر
vpn-ip-limit bot-log      # لاگ دکمه‌ها/خطاهای ربات
vpn-ip-limit update       # آپدیت از پوشه git
vpn-ip-limit off          # خاموش کردن اجباری محافظ IP
vpn-ip-limit password     # نمایش رمز ورود ادمین
```

### اگر دکمه‌های تلگرام کار نکرد

1. در ربات بزنید: **گزارش عیب‌یابی (برای پشتیبانی)** یا `/diag`
2. یا روی سرور:

```bash
vpn-ip-limit diag
cat /tmp/vpn-ip-limit-diag.txt
tail -n 80 /var/log/vpn-ip-limit-bot.log
```

3. خروجی را برای پشتیبانی بفرستید: https://t.me/AZROOT94

نکته: «اجرای بررسی الان» فقط وقتی کسی را قطع می‌کند که **محافظ IP روشن** باشد.

### آپدیت گرفتن از گیتهاب

**شما (صاحب پروژه):** روی سیستم خودتان کد را عوض کنید، بعد:

```bash
cd /path/to/rootit-vpn-ip-limit
git add -A
git commit -m "شرح تغییرات"
git push
```

**دوست / سرورهای نصب‌شده:**

```bash
cd /root/rootit-vpn-ip-limit   # یا همان جایی که clone کرده‌اند
git pull
sudo bash install.sh
# یا:
sudo vpn-ip-limit update
```

تنظیمات (`ip-limit.json` و رمز/توکن) پاک نمی‌شود؛ فقط فایل‌های برنامه عوض می‌شود.

### فایل‌های تنظیمات

| مسیر | کاربرد |
|------|--------|
| `/root/.pg_nodes/api_key` | کلید API پاسارگارد |
| `/root/.pg_nodes/ip-limit.json` | محدودیت‌ها + تنظیمات تلگرام |
| `/var/lib/vpn-ip-limit/state.json` | وضعیت اجرا |
| `/var/log/vpn-ip-limit.log` | لاگ عملیات |
| `/var/log/vpn-ip-limit-bot.log` | لاگ دکمه‌ها و خطاهای ربات |
| `/tmp/vpn-ip-limit-diag.txt` | آخرین گزارش عیب‌یابی |

### نکات اشتراک با دیگران

- هر نفر باید **توکن ربات خودش** را از BotFather بگیرد
- ربات و رمز ورود را فقط به ادمین‌های مورد اعتماد بدهید
- توکن و کلید واقعی را داخل گیت commit نکنید

---

## English

### What it does

- Watches online client IPs per VPN user (PasarGuard / Xray)
- Enforces a per-user concurrent IP limit (`HWID Limit` field, or a global default)
- Optional Telegram bot with Persian admin menu
- Default action mode: **disable** user until an admin re-enables (no auto re-enable loop)

IP Guard stays **OFF** after install until you start it from Telegram.

### Requirements

- Linux server with `systemd`
- PasarGuard panel API reachable (default `http://127.0.0.1:8000`)
- PasarGuard API key
- Python 3
- Your own Telegram bot from [@BotFather](https://t.me/BotFather)

### Install

```bash
git clone https://github.com/rootitdev/rootit-vpn-ip-limit.git
cd rootit-vpn-ip-limit
sudo bash install.sh
sudo vpn-ip-limit setup
```

`setup` asks for:

1. Bot Token
2. Bot Username
3. Admin Telegram User ID(s) (optional)
4. Access password (shareable with trusted admins)

### Telegram usage

1. Open your bot
2. Send `/start`
3. Send the access password (admins listed by User ID get menu automatically)
4. Use the Persian menu

Useful buttons:

- وضعیت کاربران و IPها
- کاربران بیش‌ازحد IP
- تنظیم حد IP کاربر
- فعال / غیرفعال کردن کاربر VPN
- روشن / خاموش کردن محافظ IP

### CLI

```bash
vpn-ip-limit              # help
vpn-ip-limit status       # report only (safe)
vpn-ip-limit setup        # configure / sync Telegram bot
vpn-ip-limit diag         # full diagnostics report
vpn-ip-limit log          # action log
vpn-ip-limit bot-log      # telegram button / error log
vpn-ip-limit update       # update from git checkout
vpn-ip-limit off          # force stop IP Guard
vpn-ip-limit password     # show access password
```

### If Telegram buttons fail

1. Tap **گزارش عیب‌یابی (برای پشتیبانی)** or send `/diag`
2. Or on the server:

```bash
vpn-ip-limit diag
cat /tmp/vpn-ip-limit-diag.txt
tail -n 80 /var/log/vpn-ip-limit-bot.log
```

3. Send the output to support: https://t.me/AZROOT94

Note: **اجرای بررسی الان** only disconnects users when **IP Guard is ON**.

### Updating from GitHub

**Maintainer:**

```bash
cd /path/to/rootit-vpn-ip-limit
git add -A
git commit -m "describe change"
git push
```

**Installed servers / friends:**

```bash
cd /root/rootit-vpn-ip-limit
git pull
sudo bash install.sh
# or:
sudo vpn-ip-limit update
```

Config (`ip-limit.json`, tokens, password) is preserved.

### Config files

| Path | Purpose |
|------|---------|
| `/root/.pg_nodes/api_key` | PasarGuard API key |
| `/root/.pg_nodes/ip-limit.json` | Limits + Telegram settings |
| `/var/lib/vpn-ip-limit/state.json` | Runtime state |
| `/var/log/vpn-ip-limit.log` | Action log |
| `/var/log/vpn-ip-limit-bot.log` | Telegram button / error log |
| `/tmp/vpn-ip-limit-diag.txt` | Last diagnostics dump |

### Notes for sharing

- Each person should use **their own** BotFather token
- Share bot + access password only with trusted admins
- Do not commit real tokens/keys into git

---

## License

MIT
