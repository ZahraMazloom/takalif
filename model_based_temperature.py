"""
عامل واکنشی مدل‌گرا (Model-Based Reflex Agent)
مسئله: کنترل دما در محیط شامل ۲ خانه
هدف: نگه داشتن دمای هر دو خانه در حدود ۲۰ درجه سانتی‌گراد

نکته کلیدی: فرمان گرمایش/سرمایش با یک گام تأخیر اعمال می‌شود،
بنابراین عامل باید با مدل فیزیک خود پیش‌بینی کند تا دما
سرریز (Overheating) نشود و نوسان نکند.
"""

# ---------- ثابت‌های سیستم ----------
TARGET = 20                    # دمای مطلوب (درجه سانتی‌گراد)
HEAT = "HEAT"                  # گرمایش
COOL = "COOL"                  # سرمایش
OFF = "OFF"                    # خاموش
DELTA = {HEAT: +1, COOL: -1, OFF: 0}   # تغییر دما در هر گام


class TemperatureEnvironment:
    """
    محیط ۲ خانه مسئله کنترل دما
    فیزیک ساده: هر گام دما ±۱ درجه تغییر می‌کند
    تأخیر: فرمانِ صادرشده از گام بعد اعمال می‌شود
    """

    def __init__(self, temps=None):
        """
        temps: دمای اولیه خانه‌ها (پیش‌فرض: 17 و 24)
        """
        if temps is None:
            temps = [17, 24]
        self.n = len(temps)
        self.temps = list(temps)

        # وضعیت "در جریان" هر خانه (چه سیستمی الان دارد کار می‌کند)
        self.running = [OFF] * self.n

        # فرمانِ صادرشده که هنوز اعمال نشده (با تأخیر اعمال می‌شود)
        self.pending = [OFF] * self.n

    def perceive(self, room):
        """
        ادراک عامل: فقط دمای خانه‌ای که در آن حضور دارد
        (وضعیت سیستم را عامل از حافظه خودش می‌داند)
        """
        return self.temps[room]

    def command(self, room, cmd):
        """
        عامل فرمان جدید برای خانه جاری صادر می‌کند
        """
        self.pending[room] = cmd

    def step(self):
        """
        یک گام از زمان:
        ۱. دما با توجه به وضعیتِ در جریانِ همین گام تغییر می‌کند
        ۲. سپس فرمان جدید وارد وضعیتِ در جریان می‌شود (تأخیر یک گامی)
        """
        for r in range(self.n):
            self.temps[r] += DELTA[self.running[r]]
        self.running = list(self.pending)

    def print_state(self):
        """نمایش وضعیت محیط"""
        labels = [f"خانه {i + 1}" for i in range(self.n)]
        print("وضعیت محیط:")
        for i in range(self.n):
            mode = {HEAT: "گرمایش", COOL: "سرمایش", OFF: "خاموش"}[self.running[i]]
            print(f"  {labels[i]}: {self.temps[i]}° (سیستم: {mode})")
        print()


class ModelBasedTemperatureAgent:
    """
    عامل مدل‌گرا برای کنترل دما

    حافظه داخلی (مدل جهان) برای هر خانه:
        temp  : دمای آخرین مشاهده (یا پیش‌بینی) آن خانه
        mode  : وضعیتِ در جریان سیستم آن خانه (گرمایش/سرمایش/خاموش)
    """

    def __init__(self, environment):
        self.env = environment
        self.n = environment.n
        self.position = 0                     # شروع از خانه اول

        # ---- حافظه داخلی (مدل جهان) ----
        self.model = [{"temp": None, "mode": OFF} for _ in range(self.n)]

        self.steps = 0
        self.prevented_overheats = 0           # تعداد دفعاتی که پیش‌بینی از سرریز جلوگیری کرد

    # ---------- ادراک و حافظه ----------

    def perceive(self):
        """دریافت دمای خانه فعلی"""
        return self.env.perceive(self.position)

    def update_state(self, temp):
        """
        به‌روزرسانی حافظه:
        - دمای خانه فعلی از مشاهده
        - وضعیت سیستم هر خانه از روی فرمان‌های خود عامل (تأخیر یک گامی)
        """
        room = self.position
        self.model[room]["temp"] = temp
        # فرمانی که در گام قبل صادر شده، الان "در جریان" است
        self.model[room]["mode"] = self.env.running[room]

    def propagate_model(self):
        """
        مدل‌سازی خانه‌هایی که در دیدرس نیستند:
        عامل بدون دیدن آنها، دمای آینده‌شان را با مدل فیزیک حساب می‌کند
        """
        for r in range(self.n):
            if r == self.position:
                continue
            m = self.model[r]
            if m["temp"] is None:
                continue                       # هنوز دیده نشده، قابل پیش‌بینی نیست
            m["temp"] += DELTA[m["mode"]]      # پیش‌بینی دمای گام بعدی

    # ---------- پیش‌بینی و تصمیم‌گیری ----------

    def predict_next_temp(self, room):
        """
        مدل پیش‌بینی عامل:
        دمای گام بعدی = دمای فعلی + تغییر ناشی از وضعیت در جریان
        """
        m = self.model[room]
        return m["temp"] + DELTA[m["mode"]]

    def choose_mode(self):
        """
        انتخاب وضعیت سیستم برای خانه فعلی با جلوگیری از سرریز

        قانون کلیدی: اگر سیستمِ در جریان خودش دما را به هدف می‌رساند،
        همین الان خاموشش کن — چون فرمان با تأخیر اعمال می‌شود و
        ادامه دادن باعث Overheating خواهد شد.
        """
        room = self.position
        temp = self.model[room]["temp"]
        pred = self.predict_next_temp(room)    # دمای گام بعدی با وضعیت فعلی

        if temp < TARGET:
            # نیاز به گرمایش، اما اگر گرمایشِ در جریان کافی است → خاموش
            if pred >= TARGET:
                self.prevented_overheats += 1
                print(f"  پیش‌بینی: گرمایشِ در جریان دما را به {pred}° می‌رساند"
                      f" → خاموش کردن برای جلوگیری از سرریز")
                return OFF
            return HEAT

        if temp > TARGET:
            # نیاز به سرمایش، اما اگر سرمایشِ در جریان کافی است → خاموش
            if pred <= TARGET:
                self.prevented_overheats += 1
                print(f"  پیش‌بینی: سرمایشِ در جریان دما را به {pred}° می‌رساند"
                      f" → خاموش کردن برای جلوگیری از سردشدن بیش از حد")
                return OFF
            return COOL

        return OFF                             # دما دقیقاً روی هدف است

    def is_settled(self, room):
        """
        آیا خانه تثبیت شده؟ یعنی دمایش ۲۰° است و سیستمش خاموش
        (در این حالت دما بدون دخالت عامل ثابت می‌ماند)
        """
        m = self.model[room]
        if m["temp"] is None:
            return False                       # ناشناخته هرگز تثبیت‌شده فرض نمی‌شود
        return abs(m["temp"] - TARGET) < 0.5 and m["mode"] == OFF

    def room_needs_attention(self, room):
        """
        آیا خانه (طبق حافظه) هنوز به هدف نرسیده؟
        خانه ناشناخته هم همیشه نیاز به بررسی دارد
        """
        m = self.model[room]
        if m["temp"] is None:
            return True
        return abs(m["temp"] - TARGET) >= 0.5 or m["mode"] != OFF

    def choose_move(self):
        """
        تصمیم حرکتی بر اساس حافظه:
        - این خانه تثبیت شد و خانه دیگر مشکل دارد → MOVE
        - هر دو خانه طبق حافظه درست‌اند → STOP (بدون نیاز به بازگشت!)
        - در غیر این صورت → STAY (تا خانه جاری تثبیت شود)
        """
        current = self.position
        other = 1 - current

        if not self.is_settled(current):
            return "STAY"                      # خانه جاری هنوز آماده نیست

        if self.room_needs_attention(other):
            return "MOVE"                      # خانه دیگر طبق حافظه مشکل دارد

        return "STOP"                          # هر دو خانه درست‌اند → پایان

    # ---------- اجرا ----------

    def print_memory(self):
        """نمایش حافظه داخلی (مدل جهان)"""
        print("حافظه داخلی:")
        for r in range(self.n):
            m = self.model[r]
            temp_str = "ناشناخته" if m["temp"] is None else f"{m['temp']}°"
            mode_str = {HEAT: "گرمایش", COOL: "سرمایش", OFF: "خاموش"}[m["mode"]]
            mark = " ← (خانه فعلی)" if r == self.position else ""
            print(f"  خانه {r + 1}: دما={temp_str}، سیستم={mode_str}{mark}")

    def run(self, max_steps=30):
        """حلقه اصلی عامل: ادراک → حافظه → پیش‌بینی → تصمیم → عمل"""
        print("=" * 60)
        print("شروع عامل کنترل دمای مدل‌گرا (هدف: ۲۰ درجه)")
        print("=" * 60)
        self.env.print_state()

        while self.steps < max_steps:
            self.steps += 1
            print(f"--- گام {self.steps} | عامل در خانه {self.position + 1} ---")

            # ۱. ادراک و به‌روزرسانی حافظه
            temp = self.perceive()
            self.update_state(temp)
            print(f"ادراک: دمای خانه {self.position + 1} = {temp}°")
            self.print_memory()

            # ۲. مدل‌سازی خانه‌های دور از دیدرس
            self.propagate_model()

            # ۳. تصمیم‌گیری درباره وضعیت سیستم
            cmd = self.choose_mode()
            mode_name = {HEAT: "گرمایش", COOL: "سرمایش", OFF: "خاموش"}[cmd]
            print(f"عمل (سیستم): {mode_name}")

            # ۴. تصمیم‌گیری درباره حرکت
            move = self.choose_move()
            print(f"عمل (حرکت): {move}")

            # ۵. اعمال فرمان و پیشروی محیط
            self.env.command(self.position, cmd)
            self.env.step()

            if move == "MOVE":
                self.position = 1 - self.position
                print(f"→ حرکت به خانه {self.position + 1}")

            if move == "STOP":
                print("\n🎉 طبق حافظه داخلی، هر دو خانه به ۲۰ درجه رسیده‌اند.")
                print("عامل بدون بازگشت به خانه‌های قبلی، کار را تمام کرد.")
                break

            print()
            self.env.print_state()

        print("=" * 60)
        print(f"خلاصه: {self.steps} گام، "
              f"{self.prevented_overheats} پیش‌بینی برای جلوگیری از سرریز")
        print("=" * 60)


# ==================== اجرای برنامه ====================

if __name__ == "__main__":
    # محیط با دمای اولیه 17 و 24 درجه
    env = TemperatureEnvironment(temps=[17, 24])

    agent = ModelBasedTemperatureAgent(env)
    agent.run(max_steps=30)

    print("\nوضعیت نهایی محیط:")
    env.print_state()
