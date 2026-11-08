# -*- coding: utf-8 -*-
"""
عامل واکنشی ساده (Simple Reactive Agent) براي مسئله جاروبرقي در محيط 2*2
هدف: تميز كردن همه خانه هاي آلوده

ويژگي عامل واکنشی ساده:
  اقدام = تابع فقط از «ادراك فعلي» (if-then)
  هيچ حافظه اي از ادراك هاي قبلي و هيچ بروزرساني حالت داخلي وجود ندارد.
"""

import random


# ------------------- محيط 2*2 -------------------
class VacuumEnv:
    def __init__(self, grid=None):
        # grid[y][x] : True = کثیف (Dirty)، False = تمیز (Clean)
        if grid is None:
            grid = [[random.choice([True, False]) for _ in range(2)]
                    for _ in range(2)]
        self.grid = [row[:] for row in grid]
        self.x, self.y = 0, 0          # موقعيت عامل
        self.cleaned = 0               # تعداد خانه هايي كه عامل تميز كرده

    def all_clean(self):
        return all(not cell for row in self.grid for cell in row)

    def percept(self):
        """ادراك فعلي عامل در هر لحظه"""
        return {
            "pos": (self.x, self.y),
            "dirty": self.grid[self.y][self.x],
            "all_clean": self.all_clean(),  # سنسور سراسري «همه تميز شدند؟»
        }

    def step(self, action):
        """اعمال اقدام عامل روي محيط (محيط را تغيير مي دهد)"""
        if action == "SUCK":
            if self.grid[self.y][self.x]:
                self.grid[self.y][self.x] = False
                self.cleaned += 1
        elif action == "MOVE_RIGHT" and self.x < 1:
            self.x += 1
        elif action == "MOVE_LEFT" and self.x > 0:
            self.x -= 1
        elif action == "MOVE_DOWN" and self.y < 1:
            self.y += 1
        elif action == "MOVE_UP" and self.y > 0:
            self.y -= 1
        # اقدام غيرمجاز (برخورد با ديوار): ناديده گرفته مي شود
        return self.percept()

    def show(self, title="محيط"):
        print(title + ":")
        print("  +" + "---------+" * 2)
        for row in self.grid:
            print("  |" + "".join("  DIRTY |" if c else " clean |" for c in row))
            print("  +" + "---------+" * 2)
        print(f"  موقعيت عامل: ({self.x}, {self.y})")


# ---------------- عامل واکنشی ساده ----------------
class SimpleReactiveAgent:
    """
    جدول قواعد if-then (به ترتیب اولویت) — فقط بر اساس ادراک فعلی:
      R1: همه خانه ها تميز شده اند -> STOP
      R2: خانه فعلي كثيف است       -> SUCK
      R3: حركت ساعتگرد ثابت بر اساس موقعيت:
          (0,0) -> راست ، (1,0) -> پايين ، (1,1) -> چپ ، (0,1) -> بالا
    """

    def act(self, p):
        x, y = p["pos"]

        # R1 : شرط خاتمه
        if p["all_clean"]:
            return "STOP"

        # R2 : اولويت با تميز كردن
        if p["dirty"]:
            return "SUCK"

        # R3 : الگوي حركت ساعتگرد (بدون حافظه، فقط از روي موقعيت)
        if (x, y) == (0, 0):
            return "MOVE_RIGHT"
        if (x, y) == (1, 0):
            return "MOVE_DOWN"
        if (x, y) == (1, 1):
            return "MOVE_LEFT"
        return "MOVE_UP"            # (0, 1)


# ---------------------- اجرا ----------------------
def main():
    env = VacuumEnv()
    agent = SimpleReactiveAgent()
    env.show("حالت اوليه")

    for t in range(1, 50):
        p = env.percept()
        action = agent.act(p)
        pos = p["pos"]
        print(f"گام {t:2d} | ادراک: خانه{pos} "
              f"{'کثیف' if p['dirty'] else 'تمیز'}"
              f"{'، همه تمیز' if p['all_clean'] else ''}"
              f" -> اقدام: {action}")

        if action == "STOP":
            print(">>> عامل متوقف شد: همه خانه ها تميز شدند.")
            break

        env.step(action)
    else:
        print("خطا: عامل به STOP نرسيد.")

    env.show("حالت نهايي")


if __name__ == "__main__":
    main()
