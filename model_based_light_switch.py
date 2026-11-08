"""
عامل واکنشی مدل‌گرا (Model-Based Reflex Agent)
مسئله: سوییچ نور در محیط ۲×۲
هدف: رساندن همه لامپ‌ها به وضعیت دلخواه (پیش‌فرض: همه خاموش)
"""


class LightSwitchEnvironment:
    """
    محیط ۲×۲ مسئله سوییچ نور
    هر خانه یک لامپ دارد: True = روشن، False = خاموش
    """

    def __init__(self, goal="all_off", initial_lights=None):
        """
        goal: "all_off" (همه خاموش) یا "all_on" (همه روشن)
        initial_lights: دیکشنری وضعیت اولیه لامپ‌ها
        """
        self.width = 2
        self.height = 2
        self.goal = goal

        # وضعیت اولیه لامپ‌ها
        if initial_lights is None:
            initial_lights = {
                (0, 0): True,   # روشن
                (1, 0): False,  # خاموش
                (0, 1): True,   # روشن
                (1, 1): True,   # روشن
            }
        self.lights = dict(initial_lights)

    def get_percept(self, position):
        """
        ادراک عامل: (مکان فعلی، آیا لامپ روشن است؟)
        """
        return (position, self.lights[position])

    def toggle(self, position):
        """
        تغییر وضعیت لامپ (روشن → خاموش یا بالعکس)
        """
        self.lights[position] = not self.lights[position]

    def print_state(self):
        """
        نمایش گرافیکی محیط
        """
        goal_str = "همه خاموش" if self.goal == "all_off" else "همه روشن"
        print(f"محیط فعلی (هدف: {goal_str}):")
        for y in range(self.height - 1, -1, -1):
            row = ""
            for x in range(self.width):
                lamp = "💡" if self.lights[(x, y)] else "🌑"
                row += f" [{lamp}] "
            print(row)
        print()


class ModelBasedLightSwitchAgent:
    """
    عامل مدل‌گرا برای مسئله سوییچ نور
    حافظه داخلی: وضعیت لامپ هر ۴ خانه (ناشناخته/روشن/خاموش)
    """

    def __init__(self, environment):
        self.environment = environment
        self.position = (0, 0)  # شروع از گوشه بالا-چپ

        # ---- حافظه داخلی (مدل جهان) ----
        # None = ناشناخته (هنوز دیده نشده)
        # True = روشن
        # False = خاموش
        self.world_model = {}
        for x in range(environment.width):
            for y in range(environment.height):
                self.world_model[(x, y)] = None

        self.steps = 0
        self.toggle_count = 0

    # ---------- بخش ادراک و حافظه ----------

    def perceive(self):
        """دریافت ادراک از محیط"""
        return self.environment.get_percept(self.position)

    def update_state(self, percept):
        """به‌روزرسانی مدل جهان با ادراک جدید"""
        location, is_on = percept
        self.world_model[location] = is_on
        self.position = location

    # ---------- بخش تصمیم‌گیری ----------

    def target_status(self):
        """وضعیت مطلوب لامپ‌ها بر اساس هدف"""
        return False if self.environment.goal == "all_off" else True

    def reached_goal(self, status):
        """آیا وضعیت یک لامپ با هدف یکسان است؟"""
        return status == self.target_status()

    def is_all_done(self):
        """
        بررسی پایان کار بر اساس حافظه
        خانه‌های ناشناخته (None) هرگز تمیز/درست فرض نمی‌شوند
        """
        for status in self.world_model.values():
            if status is None or not self.reached_goal(status):
                return False
        return True

    def get_pending_cells(self):
        """
        خانه‌هایی که طبق حافظه هنوز به هدف نرسیده‌اند:
        - ناشناخته (None)
        - یا وضعیتشان با هدف فرق دارد
        """
        cells = []
        for location, status in self.world_model.items():
            if status is None or not self.reached_goal(status):
                cells.append(location)
        return cells

    def move_towards(self, target):
        """حرکت یک قدم به سمت خانه هدف (اول محور X، بعد Y)"""
        x, y = self.position
        tx, ty = target

        if x != tx:
            self.position = (x + (1 if tx > x else -1), y)
        elif y != ty:
            self.position = (x, y + (1 if ty > y else -1))

    def choose_action(self, percept):
        """
        قانون واکنشی عامل مدل‌گرا:
        ترکیب ادراک فعلی + حافظه داخلی
        """
        location, is_on = percept

        # قانون ۱: اگر لامپ فعلی با هدف فرق دارد → تغییرش بده
        if not self.reached_goal(is_on):
            return "TOGGLE"

        # قانون ۲: اگر طبق حافظه همه به هدف رسیده‌اند → تمام
        if self.is_all_done():
            return "NO_OP"

        # قانون ۳: به سمت خانه‌ای حرکت کن که طبق حافظه هنوز به هدف نرسیده
        # (این همان کاری است که بدون حافظه ممکن نبود)
        pending = self.get_pending_cells()
        if pending:
            target = min(
                pending,
                key=lambda c: abs(c[0] - location[0]) + abs(c[1] - location[1])
            )
            self.move_towards(target)
            return "MOVE"

        return "NO_OP"

    # ---------- بخش اجرا ----------

    def run(self, max_steps=30):
        """حلقه اصلی عامل: ادراک → حافظه → تصمیم → عمل"""
        print("=" * 60)
        print("شروع عامل سوییچ نور مدل‌گرا")
        print("=" * 60)
        self.environment.print_state()

        while self.steps < max_steps:
            self.steps += 1
            print(f"--- گام {self.steps} ---")

            # ۱. ادراک
            percept = self.perceive()
            loc, is_on = percept
            print(f"ادراک: مکان={loc}، لامپ={'روشن' if is_on else 'خاموش'}")

            # ۲. به‌روزرسانی حافظه
            self.update_state(percept)
            self.print_memory()

            # ۳. تصمیم‌گیری
            action = self.choose_action(percept)
            print(f"عمل: {action}")

            # ۴. اجرای عمل
            if action == "TOGGLE":
                self.environment.toggle(self.position)
                self.toggle_count += 1
                # حافظه باید بلافاصله بعد از عمل هم به‌روز شود
                # چون عامل مدل‌گراست و نتیجه عملش را می‌داند
                self.world_model[self.position] = self.environment.lights[self.position]
                state = "روشن" if self.world_model[self.position] else "خاموش"
                print(f"✓ لامپ {self.position} شد: {state}")
                self.environment.print_state()

            if action == "NO_OP":
                if self.is_all_done():
                    print("\n🎉 همه لامپ‌ها به هدف رسیدند! عامل کار را تمام کرد.")
                    break

            print()

        print("=" * 60)
        print(f"خلاصه: {self.steps} گام، {self.toggle_count} تغییر وضعیت")
        print("=" * 60)

    def print_memory(self):
        """نمایش حافظه داخلی (مدل جهان)"""
        print("حافظه داخلی:")
        for (x, y), status in sorted(self.world_model.items()):
            text = {
                None: "ناشناخته",
                True: "روشن",
                False: "خاموش",
            }[status]
            mark = " ← (محل فعلی)" if (x, y) == self.position else ""
            print(f"  ({x},{y}): {text}{mark}")


# ==================== اجرای برنامه ====================

if __name__ == "__main__":
    # محیط با هدف "همه خاموش" و چند لامپ روشن اولیه
    env = LightSwitchEnvironment(goal="all_off")

    agent = ModelBasedLightSwitchAgent(env)
    agent.run(max_steps=30)

    print("\nوضعیت نهایی محیط:")
    env.print_state()
