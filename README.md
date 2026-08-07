# RoOtIt VPN IP LIMIT

> به یاد جاویدنامان ۱۸۱۹ دی  
> RoOtIt VPN IP LIMIT | 1819

محدودکنندهٔ تعداد IP همزمان برای پنل PasarGuard با مدیریت از طریق ربات تلگرام.

پشتیبانی: [t.me/AZROOT94](https://t.me/AZROOT94)  
ریپو: [github.com/rootitdev/rootit-vpn-ip-limit](https://github.com/rootitdev/rootit-vpn-ip-limit)

---

<!-- Persian section -->

## فارسی — خلاصه

این ابزار از API پنل PasarGuard تعداد IPهای آنلاین هر کاربر VPN را می‌خواند و بر اساس محدودیت تعریف‌شده (HWID Limit برای هر کاربر یا حد پیش‌فرض سراسری) اقدام می‌کند. مدیریت و تنظیمات از طریق ربات تلگرام با منوی فارسی انجام می‌شود.

نکته: پس از نصب محافظ IP خاموش است — باید از منوی تلگرام آن را روشن کنید.

### مهم — عملکرد محدودیت IP

- اسکریپت به طور مداوم (تقریباً هر ~20 ثانیه) وضعیت آنلاین شدن IPها را از پنل می‌پرسد.
- اگر تعداد IPهای آنلاین یک کاربر ≤ حد مجاز → کاری انجام نمی‌شود.
- اگر تعداد IPها > حد و محافظ روشن باشد → حساب کاربر غیرفعال می‌شود (disable).
- تغییر شبکه موبایل ↔ وای‌فای ممکن است موقتاً دو IP نشان دهد؛ برای یک کاربر واقعی مقدار پیش‌فرض `2` منطقی است.

### پیش‌نیازها

- سرور لینوکس با systemd و Python 3
- پنل PasarGuard در دسترس سرور
- API Key پنل
- ربات تلگرام از @BotFather

### نصب سریع

```bash
git clone https://github.com/rootitdev/rootit-vpn-ip-limit.git
cd rootit-vpn-ip-limit
sudo bash install.sh
sudo vpn-ip-limit setup
```

برای نصب غیرتعاملی (مثال):

```bash
PANEL_URL=https://127.0.0.1:2087 sudo -E bash install.sh
```

### آنچه هنگام نصب پرسیده می‌شود

1. API Key — تنها زمانی پرسیده می‌شود که فایل کلید وجود نداشته باشد. فقط خود کلید را بچسبانید، مثلاً:
   ```
   pg_key_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```
2. آدرس پنل — باید دقیقاً آدرس API پنل باشد:
   - HTTP: `http://127.0.0.1:8000`
   - HTTPS: `https://127.0.0.1:2087`
   - اگر فقط پورت وارد کنید (مثلاً `2087`) به صورت `http://127.0.0.1:2087` در نظر گرفته می‌شود — برای HTTPS باید کامل بنویسید.

در مرحلهٔ `setup` اطلاعات زیر وارد می‌شوند: توکن ربات، نام کاربری ربات (بدون @)، User ID ادمین‌ها (اختیاری، با ویرگول)، رمز دسترسی ادمین، و لینک پشتیبانی (پیش‌فرض: `https://t.me/AZROOT94`).

### استفاده از تلگرام

1. ربات را باز کنید و `/start` بفرستید.
2. اگر User ID شما در فهرست ادمین‌ها باشد منو مستقیم باز می‌شود؛ در غیر این صورت رمز ورود را وارد کنید.
3. از منوی فارسی برای مدیریت استفاده کنید.

دکمه‌های مهم:
- وضعیت کاربران و IPها — فهرست کاربران و تعداد IP آنلاین
- کاربران بیش‌ازحد IP — فقط کاربران نقض‌کننده
- تنظیم حد IP کاربر — مثال: `Ali 2` (۰ = نامحدود)
- حد IP پیش‌فرض همه
- فعال/غیرفعال کردن کاربر VPN (دستی)
- روشن/خاموش کردن محافظ IP
- اجرای بررسی حالا — چک فوری (فقط اگر محافظ روشن باشد)
- گزارش عیب‌یابی — خروجی برای پشتیبانی
- کاربران معاف — استثناها
- رمز ورود ادمین — نمایش/تغییر/قطع نشست‌ها

### دستورات CLI

```bash
vpn-ip-limit              # راهنما + وضعیت کلی
vpn-ip-limit setup        # تنظیم / سینک ربات تلگرام
vpn-ip-limit status       # گزارش کاربران (بدون قطع)
vpn-ip-limit diag         # گزارش عیب‌یابی خوانا
vpn-ip-limit log          # لاگ عملیات قطع کاربران
vpn-ip-limit bot-log      # لاگ ربات
vpn-ip-limit update       # به‌روزرسانی از پوشه گیت
vpn-ip-limit off          # خاموش کردن اجباری محافظ IP
vpn-ip-limit password     # نمایش رمز ورود ادمین
```

### به‌روزرسانی

روی سرور نصب‌شده:

```bash
cd ~/rootit-vpn-ip-limit
git pull
sudo bash install.sh
# یا:
sudo vpn-ip-limit update
```

تنظیمات (مثل `ip-limit.json`، توکن و رمز) محفوظ می‌مانند.

### حذف کامل / نصب دوباره

```bash
cd ~/rootit-vpn-ip-limit
git pull
sudo bash uninstall.sh --purge-key --yes
sudo bash install.sh
sudo vpn-ip-limit setup
```

- بدون فلگ: سرویس‌ها، باینری‌ها، کانفیگ‌ها و لاگ‌ها حذف می‌شوند؛ فایل api_key باقی می‌ماند.
- `--purge-key`: فایل `/root/.pg_nodes/api_key` هم پاک می‌شود.
- `--yes`: بدون تأیید تعاملی اجرا می‌شود.

### عیب‌یابی سریع

1. داخل ربات: دکمه "گزارش عیب‌یابی" یا دستور `/diag`.
2. روی سرور:

```bash
vpn-ip-limit diag
cat /tmp/vpn-ip-limit-diag.txt
tail -n 80 /var/log/vpn-ip-limit-bot.log
```

3. تست دستی اتصال به پنل:

```bash
cat /root/.pg_nodes/panel_url

curl -sk --max-time 5 \
  -H "X-API-Key: $(cat /root/.pg_nodes/api_key)" \
  "$(cat /root/.pg_nodes/panel_url)/api/system"
```

خروجی باید JSON معتبر باشد (نه `401` و نه `Empty reply`).

### مشکلات رایج و رفع آنها

- Empty reply روی `http://...:PORT` → پنل HTTPS است → از `https://...` استفاده کنید.
- 401 Unauthorized → کلید API اشتباه یا آلوده است → فقط `pg_key_...` قرار دهید یا `--purge-key`.
- دکمه‌ها ارور می‌دهند اما ربات پاسخ می‌دهد → پنل قطع یا کلید خراب است (`vpn-ip-limit diag`).
- "اجرای بررسی الان" کاری نمی‌کند → محافظ خاموش است؛ اول روشن کنید.

### مسیرهای مهم

- /opt/vpn-ip-limit/ — کد برنامه
- /usr/local/bin/vpn-ip-limit* — دستورات CLI / ربات / setup
- /root/.pg_nodes/api_key — کلید API
- /root/.pg_nodes/panel_url — آدرس پایه API پنل
- /root/.pg_nodes/ip-limit.json — محدودیت‌ها و تنظیمات تلگرام
- /var/lib/vpn-ip-limit/state.json — وضعیت اجرا و نشست‌ها
- /var/log/vpn-ip-limit.log — لاگ عملیات قطع
- /var/log/vpn-ip-limit-bot.log — لاگ ربات
- /tmp/vpn-ip-limit-diag.txt — آخرین گزارش عیب‌یابی

---

<!-- English section -->

## English — Summary

RoOtIt VPN IP LIMIT reads online client IPs per VPN user from the PasarGuard panel API and enforces concurrent IP limits (per-user HWID Limit or a global default). Administration is done via a Telegram bot with a Persian interface.

Note: IP Guard remains OFF after installation — enable it through the Telegram bot.

### How it works

- Polls the panel every ~20 seconds to get online IPs.
- If online IPs ≤ limit → no action.
- If online IPs > limit and Guard is ON → the account is disabled.
- For mobile↔Wi‑Fi switches, transient duplicate IPs can appear — using `2` as default is recommended.

### Requirements

- Linux server with systemd and Python 3
- PasarGuard panel API reachable
- Panel API key
- Telegram bot token from @BotFather

### Quick install

```bash
git clone https://github.com/rootitdev/rootit-vpn-ip-limit.git
cd rootit-vpn-ip-limit
sudo bash install.sh
sudo vpn-ip-limit setup
```

Non-interactive example:

```bash
PANEL_URL=https://127.0.0.1:2087 sudo -E bash install.sh
```

### CLI

```bash
vpn-ip-limit              # help
vpn-ip-limit setup        # configure / sync Telegram bot
vpn-ip-limit status       # report only
vpn-ip-limit diag         # diagnostics (human-readable)
vpn-ip-limit log          # action log
vpn-ip-limit bot-log      # bot/error log
vpn-ip-limit update       # update from git checkout
vpn-ip-limit off          # force stop IP Guard
vpn-ip-limit password     # show admin password
```

### Update

On the installed server:

```bash
cd ~/rootit-vpn-ip-limit
git pull
sudo bash install.sh
# or:
sudo vpn-ip-limit update
```

### Uninstall / Clean reinstall

```bash
cd ~/rootit-vpn-ip-limit
git pull
sudo bash uninstall.sh --purge-key --yes
sudo bash install.sh
sudo vpn-ip-limit setup
```

### Troubleshooting

- Use `vpn-ip-limit diag` and check `/tmp/vpn-ip-limit-diag.txt`.
- Test panel connectivity:

```bash
curl -sk --max-time 5 \
  -H "X-API-Key: $(cat /root/.pg_nodes/api_key)" \
  "$(cat /root/.pg_nodes/panel_url)/api/system"
```

Expect a valid JSON response.

### Important paths

- /opt/vpn-ip-limit/ — app code
- /usr/local/bin/vpn-ip-limit* — CLI / bot / setup
- /root/.pg_nodes/api_key — PasarGuard API key
- /root/.pg_nodes/panel_url — panel base URL
- /root/.pg_nodes/ip-limit.json — limits + Telegram settings
- /var/lib/vpn-ip-limit/state.json — runtime state
- /var/log/vpn-ip-limit.log — action log
- /var/log/vpn-ip-limit-bot.log — bot log
- /tmp/vpn-ip-limit-diag.txt — last diagnostic dump

---

## License

MIT
```
