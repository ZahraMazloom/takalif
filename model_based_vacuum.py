"""
عامل واکنشی مدل‌گرا (Model-Based Reflex Agent)
مسئله: جاروبرقی در محیط ۲×۲
"""

import random


class ModelBasedVacuumAgent:
    """
    عامل جاروبرقی مدل‌گرا با حافظه داخلی.
    محیط: شبکه ۲×۲ (۴ خانه) با مختصات (0,0) تا (1,1)
    """

    def __init__(self, environment):
        """
        مقداردهی اولیه حافظه داخلی

        world_model: دیکشنری وضعیت همه خانه‌ها
                      None = ناشناخته (هنوز دیده نشده)
                      True = تمیز
                      False = آلوده
        position: مکان فعلی عامل (x, y)
        """
        self.environment = environment
        self.position = (0, 0)  # شروع از گوشه بالا-چپ

        # حافظه داخلی: مدل جهان - ابتدا همه خانه‌ها ناشناخته
        self.world_model = {}
        for x in range(environment.width):
            for y in range(environment.height):
                self.world_model[(x, y)] = None  # None = هنوز دیده نشده

        self.steps = 0
        self.clean_actions = 0  # تعداد عملیات مکش

    def perceive(self):
        """
        دریافت ادراک: وضعیت خانه فعلی
        خروجی: (مکان فعلی، آیا آلوده است؟)
        """
        status = self.environment.get_status(self.position)
        return (self.position, status)

    def update_state(self, percept):
        """
        به‌روزرسانی حافظه داخلی بر اساس ادراک جدید
        این همان "مدل‌سازی جهان" است
        """
        location, is_dirty = percept

        # ثبت وضعیت مشاهده‌شده در حافظه
        # True = تمیز، False = آلوده
        self.world_model[location] = not is_dirty

        # همچنین مکان فعلی را به‌روزرسانی کن
        self.position = location

    def is_all_clean(self):
        """
        بررسی آیا همه خانه‌ها بر اساس حافظه تمیز هستند؟
        خانه‌های ناشناخته (None) را نیز تمیز فرض نمی‌کنیم
        """
        for status in self.world_model.values():
            if status is None or status is False:
                return False
        return True

    def get_unknown_or_dirty_cells(self):
        """
        لیست خانه‌هایی که بر اساس حافظه:
        - ناشناخته هستند (None)
        - یا آلوده هستند (False)
        """
        cells = []
        for location, status in self.world_model.items():
            if status is None or status is False:
                cells.append(location)
        return cells

    def move_towards(self, target):
        """
        حرکت یک قدم به سمت خانه هدف
        اول در محور X، بعد در محور Y
        """
        x, y = self.position
        tx, ty = target

        if x != tx:
            # حرکت در محور X
            new_x = x + (1 if tx > x else -1)
            self.position = (new_x, y)
        elif y != ty:
            # حرکت در محور Y
            new_y = y + (1 if ty > y else -1)
            self.position = (x, new_y)

    def choose_action(self, percept):
        """
        انتخاب عمل بر اساس:
        ۱. ادراک فعلی (خانه جاروبرقی چه وضعیتی دارد)
        ۲. حافظه داخلی (کدام خانه‌ها هنوز تمیز نشده‌اند)
        """
        location, is_dirty = percept

        # قانون ۱: اگر خانه فعلی آلوده است → مکش کن
        if is_dirty:
            return "SUCK"

        # قانون ۲: اگر همه خانه‌ها بر اساس حافظه تمیز شده‌اند → تمیز!
        if self.is_all_clean():
            return "NO_OP"  # هیچ عملی لازم نیست

        # قانون ۳: به سمت خانه ناشناخته یا آلوده حرکت کن
        # (این همان چیزی است که بدون حافظه ممکن نبود!)
        target_cells = self.get_unknown_or_dirty_cells()

        if target_cells:
            # نزدیک‌ترین خانه هدف را انتخاب کن
            target = min(target_cells, key=lambda c: abs(c[0] - location[0]) + abs(c[1] - location[1]))
            self.move_towards(target)

            # حرکت انجام شد، عمل بعدی بررسی خانه جدید است
            return "MOVE"

        return "NO_OP"

    def run(self, max_steps=20):
        """
        اجرای حلقه اصلی عامل
        """
        print("=" * 60)
        print("شروع عامل جاروبرقی مدل‌گرا")
        print("=" * 60)

        while self.steps < max_steps:
            self.steps += 1
            print(f"\n--- گام {self.steps} ---")

            # ۱. دریافت ادراک
            percept = self.perceive()
            loc, dirty = percept

            print(f"ادراک: مکان={loc}، وضعیت={'آلوده' if dirty else 'تمیز'}")

            # ۲. به‌روزرسانی حافظه
            self.update_state(percept)

            # نمایش حافظه داخلی
            print("حافظه داخلی (مدل جهان):")
            for (x, y), status in sorted(self.world_model.items()):
                status_str = {
                    None: "ناشناخته",
                    True: "تمیز ✓",
                    False: "آلوده ✗"
                }[status]
                marker = " ← (محل فعلی)" if (x, y) == self.position else ""
                print(f"  ({x},{y}): {status_str}{marker}")

            # ۳. تصمیم‌گیری و اجرا
            action = self.choose_action(percept)
            print(f"عمل: {action}")

            # اجرای عمل مکش
            if action == "SUCK":
                self.environment.clean(self.position)
                self.clean_actions += 1
                print(f"✓ خانه {self.position} جارو کشیده شد!")

            # بررسی پایان
            if action == "NO_OP" and self.is_all_clean():
                print("\n🎉 همه خانه‌ها تمیز شدند! عامل کار را تمام کرد.")
                break

        print("\n" + "=" * 60)
        print(f"خلاصه: {self.steps} گام، {self.clean_actions} مکش")
        print("=" * 60)


class Environment:
    """
    محیط ۲×۲ مسئله جاروبرقی
    """

    def __init__(self, dirty_cells=None):
        """
        dirty_cells: لیست مختصات خانه‌های آلوده اولیه
        """
        self.width = 2
        self.height = 2

        # وضعیت اولیه: True = تمیز، False = آلوده
        self.grid = {}
        for x in range(self.width):
            for y in range(self.height):
                self.grid[(x, y)] = True  # ابتدا همه تمیز

        # تعیین خانه‌های آلوده
        if dirty_cells is None:
            dirty_cells = [(0, 0), (1, 1)]  # پیش‌فرض: دو خانه آلوده

        for cell in dirty_cells:
            self.grid[cell] = False

    def get_status(self, position):
        """
        دریافت وضعیت خانه: True = آلوده است
        """
        return not self.grid[position]

    def clean(self, position):
        """
        تمیز کردن خانه
        """
        self.grid[position] = True

    def print(self):
        """
        نمایش گرافیکی محیط
        """
        print("\nمحیط فعلی:")
        for y in range(self.height - 1, -1, -1):
            row = ""
            for x in range(self.width):
                status = "🧹" if self.grid[(x, y)] else "💩"
                row += f" [{status}] "
            print(row)


# ==================== اجرای برنامه ====================

if __name__ == "__main__":
    # ساخت محیط با دو خانه آلوده
    env = Environment(dirty_cells=[(0, 0), (1, 1)])
    env.print()

    # ساخت و اجرای عامل
    agent = ModelBasedVacuumAgent(env)
    agent.run(max_steps=20)

    # نمایش محیط نهایی
    env.print()
