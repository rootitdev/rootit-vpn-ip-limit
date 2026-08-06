# RoOtIt VPN IP LIMIT

> به یاد جاویدنامان ۱۸۱۹ دی  
> `RoOtIt VPN IP LIMIT | 1819 به یاد جاوید نامان`

محدودکنندهٔ IP همزمان برای پنل **PasarGuard** با مدیریت از طریق ربات تلگرام.

پشتیبانی / Support: [t.me/AZROOT94](https://t.me/AZROOT94)  
ریپو: [github.com/rootitdev/rootit-vpn-ip-limit](https://github.com/rootitdev/rootit-vpn-ip-limit)

---

## فارسی

### این ابزار چه کاری می‌کند؟

- IPهای آنلاین هر کاربر VPN را از API پنل PasarGuard می‌خواند
- محدودیت تعداد IP همزمان را اعمال می‌کند:
  - فیلد **HWID Limit** همان کاربر در پنل، یا
  - حد پیش‌فرض کلی (پیش‌فرض: `2`)
- ربات تلگرام با منوی فارسی برای مدیریت
- حالت پیش‌فرض (`mode=disable`): اگر کاربر بیش از حد مجاز IP داشته باشد، اکانت **غیرفعال می‌ماند** تا ادمین دستی فعالش کند

بعد از نصب، **محافظ IP خاموش** است تا خودتان از منوی تلگرام روشنش کنید.

### پیش‌نیازها

- سرور لینوکس با `systemd` و Python 3
- پنل **PasarGuard** روی همان سرور (یا در دسترس از آن)
- **API Key** پنل
- ربات تلگرام خودتان از [@BotFather](https://t.me/BotFather)

### نصب سریع

```bash
git clone https://github.com/rootitdev/rootit-vpn-ip-limit.git
cd rootit-vpn-ip-limit
sudo bash install.sh
sudo vpn-ip-limit setup
```

#### موقع نصب چه چیزهایی پرسیده می‌شود؟

1. **API Key** — فقط اگر فایل کلید پیدا نشود  
   فقط خود کلید را بچسبانید، مثلاً:
   ```text
   pg_key_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```
   نه دستور، نه فاصله، نه متن اضافه.

2. **آدرس پنل** — باید دقیقاً همان آدرس API پنل باشد:
   - اگر پنل HTTP است: `http://127.0.0.1:8000`
   - اگر پنل HTTPS است: `https://127.0.0.1:2087`
   - می‌توانید فقط پورت بزنید: `2087` → می‌شود `http://127.0.0.1:2087`  
     (برای HTTPS حتماً کامل با `https://` بنویسید)

بدون سؤال تعاملی:

```bash
PANEL_URL=https://127.0.0.1:2087 sudo -E bash install.sh
```

#### موقع `setup` چه چیزهایی وارد می‌کنید؟

1. Bot Token (از BotFather)
2. Bot Username بدون `@`
3. Admin Telegram User ID(ها) — اختیاری، با ویرگول
4. رمز ورود ادمین (قابل اشتراک با افراد مورد اعتماد)
5. لینک پشتیبانی (پیش‌فرض: `https://t.me/AZROOT94`)

### استفاده از تلگرام

1. ربات را باز کنید
2. `/start` بفرستید
3. اگر User ID شما در لیست ادمین باشد، منو مستقیم باز می‌شود؛ وگرنه رمز ورود را بفرستید
4. از منوی فارسی استفاده کنید

دکمه‌های مهم:

| دکمه | کار |
|------|-----|
| وضعیت کاربران و IPها | لیست کاربران + تعداد IP آنلاین |
| کاربران بیش‌ازحد IP | فقط کسانی که از حد رد شده‌اند |
| تنظیم حد IP کاربر | مثلاً `Ali 2` (۰ = نامحدود) |
| حد IP پیش‌فرض همه | برای کاربرانی بدون حد اختصاصی |
| فعال / غیرفعال کردن کاربر VPN | دستی |
| روشن / خاموش کردن محافظ IP | شروع یا توقف اعمال محدودیت |
| اجرای بررسی الان | یک‌بار چک فوری (فقط اگر محافظ روشن باشد) |
| گزارش عیب‌یابی | خلاصهٔ قابل‌فهم برای پشتیبانی |
| کاربران معاف | استثنا از محدودیت |
| رمز ورود ادمین | نمایش / تغییر / قطع نشست‌ها |


### رفتار محدودیت IP (مهم)

اسکریپت خودش «سشن ۱۰ دقیقه‌ای» ندارد. هر حدود **۲۰ ثانیه** از پنل می‌پرسد الان چند IP آنلاین است.

| وضعیت | نتیجه |
|--------|--------|
| تعداد IP ≤ حد مجاز | هیچ اتفاقی نمی‌افتد |
| تعداد IP > حد + محافظ روشن | اکانت غیرفعال می‌شود (`disable`) |
| تعویض نت موبایل ↔ وای‌فای با حد ۱ | اغلب موقتاً ۲ IP دیده می‌شود و ممکن است قطع شود |
| حد پیشنهادی برای یک نفر واقعی | معمولاً `2` |

IP قدیمی وقتی از لیست پنل پاک می‌شود که کلاینت قطع شده باشد و پنل دیگر آن را آنلاین نداند — نه با تایمر ثابت داخل این اسکریپت.

### دستورات CLI

```bash
vpn-ip-limit              # راهنما + وضعیت کلی
vpn-ip-limit setup        # تنظیم / سینک ربات تلگرام
vpn-ip-limit status       # گزارش کاربران (قطع نمی‌کند)
vpn-ip-limit diag         # گزارش عیب‌یابی فارسی
vpn-ip-limit log          # لاگ عملیات قطع کاربر
vpn-ip-limit bot-log      # لاگ دکمه‌ها / خطاهای ربات
vpn-ip-limit update       # آپدیت از پوشه git
vpn-ip-limit off          # خاموش کردن اجباری محافظ IP
vpn-ip-limit password     # نمایش رمز ورود ادمین
```

### آپدیت

روی سرور نصب‌شده:

```bash
cd ~/rootit-vpn-ip-limit    # یا مسیر clone شما
git pull
sudo bash install.sh
# یا:
sudo vpn-ip-limit update
```

تنظیمات (`ip-limit.json`، توکن، رمز) پاک نمی‌شود؛ فقط فایل‌های برنامه عوض می‌شود.

### حذف کامل / نصب دوباره

اگر نصب خراب شد (کلید آلوده، پورت اشتباه، ربات قاطی و …):

```bash
cd ~/rootit-vpn-ip-limit
git pull
sudo bash uninstall.sh --purge-key --yes
sudo bash install.sh
sudo vpn-ip-limit setup
```

| گزینه | معنی |
|--------|------|
| بدون فلگ | سرویس‌ها، باینری‌ها، کانفیگ اسکریپت، لاگ‌ها حذف می‌شوند؛ `api_key` می‌ماند |
| `--purge-key` | فایل `/root/.pg_nodes/api_key` هم پاک می‌شود |
| `--yes` | بدون تأیید تعاملی |

**حذف نمی‌شود:** پنل PasarGuard، کاربران VPN، Xray، پوشهٔ clone گیت.

### عیب‌یابی

#### ۱) گزارش داخل ربات

دکمه **گزارش عیب‌یابی (برای پشتیبانی)** یا دستور `/diag`

گزارش فارسی است و خلاصه می‌گوید پنل وصل است یا نه، محافظ روشن است یا نه، و راهنمای رفع می‌دهد.

#### ۲) روی سرور

```bash
vpn-ip-limit diag
cat /tmp/vpn-ip-limit-diag.txt
tail -n 80 /var/log/vpn-ip-limit-bot.log
```

#### ۳) تست دستی اتصال به پنل

```bash
# آدرس ذخیره‌شده
cat /root/.pg_nodes/panel_url

# تست (http یا https را مطابق پنل خودتان بزنید)
curl -sk --max-time 5 \
  -H "X-API-Key: $(cat /root/.pg_nodes/api_key)" \
  "$(cat /root/.pg_nodes/panel_url)/api/system"
```

باید JSON برگردد، نه `401` و نه `Empty reply`.

### مشکلات رایج

| نشانه | علت رایج | کار درست |
|--------|-----------|----------|
| `Empty reply` روی `http://...:2087` | پنل HTTPS است | آدرس را `https://127.0.0.1:PORT` بگذارید |
| `401 Unauthorized` | API Key اشتباه یا آلوده | فقط `pg_key_...` در فایل کلید؛ یا uninstall با `--purge-key` |
| `unknown url type: pasarguard...` | فایل `panel_url` خراب | نصب جدید یا `echo 'https://127.0.0.1:PORT' > /root/.pg_nodes/panel_url` |
| دکمه‌ها خطا می‌دهند ولی ربات جواب می‌دهد | پنل قطع / کلید بد | `vpn-ip-limit diag` |
| «اجرای بررسی الان» کسی را قطع نمی‌کند | محافظ خاموش است | اول «روشن کردن محافظ IP» |
| کلید شبیه `sudo vpn-ip-limit setuppg_key_...` | موقع نصب متن اضافه چسبیده | `uninstall.sh --purge-key` و نصب دوباره |

اصلاح سریع آدرس پنل بدون uninstall کامل:

```bash
echo 'https://127.0.0.1:2087' > /root/.pg_nodes/panel_url
systemctl restart vpn-ip-limit-bot
vpn-ip-limit diag
```

اصلاح سریع کلید:

```bash
echo 'pg_key_XXXX' > /root/.pg_nodes/api_key
chmod 600 /root/.pg_nodes/api_key
systemctl restart vpn-ip-limit-bot
```

### فایل‌های مهم

| مسیر | کاربرد |
|------|--------|
| `/opt/vpn-ip-limit/` | کد برنامه |
| `/usr/local/bin/vpn-ip-limit*` | دستورات CLI / ربات / setup |
| `/root/.pg_nodes/api_key` | کلید API پاسارگارد |
| `/root/.pg_nodes/panel_url` | آدرس پایهٔ API پنل |
| `/root/.pg_nodes/ip-limit.json` | محدودیت‌ها + تنظیمات تلگرام |
| `/var/lib/vpn-ip-limit/state.json` | وضعیت اجرا و نشست ادمین‌ها |
| `/var/log/vpn-ip-limit.log` | لاگ عملیات قطع |
| `/var/log/vpn-ip-limit-bot.log` | لاگ ربات |
| `/tmp/vpn-ip-limit-diag.txt` | آخرین گزارش عیب‌یابی (کامل) |

### نکات اشتراک با دیگران

- هر نفر **توکن ربات خودش** را از BotFather بگیرد
- ربات و رمز را فقط به ادمین‌های مورد اعتماد بدهید
- توکن و کلید واقعی را داخل گیت commit نکنید
- پورت پنل دوست‌تان ممکن است با شما فرق کند؛ همان آدرس واقعی پنل خودش را بزند

---

## English

### What it does

- Reads online client IPs per VPN user from the PasarGuard panel API
- Enforces concurrent IP limits (`HWID Limit` per user, or a global default — usually `2`)
- Telegram admin bot with Persian menu
- Default mode (`disable`): over-limit users stay disabled until an admin re-enables them

IP Guard stays **OFF** after install until you enable it from Telegram.

### Requirements

- Linux + `systemd` + Python 3
- PasarGuard panel API reachable
- Panel API key
- Your own Telegram bot from [@BotFather](https://t.me/BotFather)

### Quick install

```bash
git clone https://github.com/rootitdev/rootit-vpn-ip-limit.git
cd rootit-vpn-ip-limit
sudo bash install.sh
sudo vpn-ip-limit setup
```

Installer asks for:

1. **API key** (if missing) — paste **only** the key, e.g. `pg_key_...` (no commands, no extra text)
2. **Panel URL** — must match the real panel API:
   - HTTP example: `http://127.0.0.1:8000`
   - HTTPS example: `https://127.0.0.1:2087`
   - Port-only input becomes `http://127.0.0.1:PORT` — for HTTPS type the full `https://...` URL

Non-interactive:

```bash
PANEL_URL=https://127.0.0.1:2087 sudo -E bash install.sh
```

`setup` asks for bot token, username, optional admin IDs, access password, support link.

### How limiting works

The script does **not** use a fixed “10-minute session”. About every **20 seconds** it asks the panel how many IPs are currently online.

- If online IPs ≤ limit → OK
- If online IPs > limit and Guard is ON → account is disabled
- Switching mobile ↔ Wi‑Fi with limit `1` often briefly shows 2 IPs and may disable the account
- For a real single user, limit `2` is usually safer

### CLI

```bash
vpn-ip-limit              # help
vpn-ip-limit setup        # configure / sync Telegram bot
vpn-ip-limit status       # report only (safe)
vpn-ip-limit diag         # human-readable diagnostics
vpn-ip-limit log          # action log
vpn-ip-limit bot-log      # telegram / error log
vpn-ip-limit update       # update from git checkout
vpn-ip-limit off          # force stop IP Guard
vpn-ip-limit password     # show access password
```

### Update

```bash
cd ~/rootit-vpn-ip-limit
git pull
sudo bash install.sh
# or:
sudo vpn-ip-limit update
```

### Uninstall / clean reinstall

```bash
cd ~/rootit-vpn-ip-limit
git pull
sudo bash uninstall.sh --purge-key --yes
sudo bash install.sh
sudo vpn-ip-limit setup
```

- `--purge-key` also deletes `/root/.pg_nodes/api_key`
- Does **not** remove PasarGuard, VPN users, or Xray

### Troubleshooting

```bash
vpn-ip-limit diag
cat /root/.pg_nodes/panel_url
curl -sk --max-time 5 \
  -H "X-API-Key: $(cat /root/.pg_nodes/api_key)" \
  "$(cat /root/.pg_nodes/panel_url)/api/system"
```

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Empty reply` on HTTP | Panel is HTTPS | Use `https://127.0.0.1:PORT` |
| `401 Unauthorized` | Bad / polluted API key | Clean `pg_key_...` only, or uninstall `--purge-key` |
| Buttons fail, bot still replies | Panel unreachable / bad key | Run `diag` |
| “Run check now” does nothing | Guard is OFF | Enable IP Guard first |

### Important paths

| Path | Purpose |
|------|---------|
| `/opt/vpn-ip-limit/` | App code |
| `/usr/local/bin/vpn-ip-limit*` | CLI / bot / setup |
| `/root/.pg_nodes/api_key` | PasarGuard API key |
| `/root/.pg_nodes/panel_url` | Panel base URL |
| `/root/.pg_nodes/ip-limit.json` | Limits + Telegram settings |
| `/var/lib/vpn-ip-limit/state.json` | Runtime state |
| `/var/log/vpn-ip-limit.log` | Action log |
| `/var/log/vpn-ip-limit-bot.log` | Bot log |
| `/tmp/vpn-ip-limit-diag.txt` | Last full diagnostics dump |

### Sharing notes

- Each person should use **their own** BotFather token
- Share bot + password only with trusted admins
- Never commit real tokens/keys
- Panel port/protocol differs per server — use that server’s real panel URL

---

## License

MIT
