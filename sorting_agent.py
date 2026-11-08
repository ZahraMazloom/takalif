# -*- coding: utf-8 -*-
"""
عامل واکنشی ساده (Simple Reactive Agent) براي مرتب‌سازي اقلام بر اساس وزن
در يك محيط خطی با 10 جعبه (وزن هاي تصادفي) — الگوريتمي شبيه مرتب‌سازي حببي

ويژگي عامل واکنشی ساده:
  اقدام = تابع فقط از «ادراك فعلي» (if-then) و بدون هيچ حافظه‌اي.
  ادراک: وزن جعبه فعلي + وزن جعبه بعدي + موقعيت + پرچم سراسري مرتب‌بودن.
"""

import random

N = 10            # تعداد جعبه ها
MIN_W, MAX_W = 1, 100   # بازه وزن هاي تصادفي


# ------------------- محيط خطی -------------------
class LinearEnv:
    def __init__(self, weights=None):
        if weights is None:
            weights = [random.randint(MIN_W, MAX_W) for _ in range(N)]
        self.w = list(weights)     # وزن جعبه ها
        self.pos = 0               # موقعيت عامل (0 .. N-1)
        self.swaps = 0             # شمارنده جابجايي ها
        self.steps = 0             # شمارنده گام ها

    def is_sorted(self):
        """سنسور سراسري: آيا کل لیست از کوچک به بزرگ مرتب است؟"""
        return all(self.w[i] <= self.w[i + 1] for i in range(len(self.w) - 1))

    def percept(self):
        """ادراك فعلي عامل"""
        last = self.pos == len(self.w) - 1
        return {
            "pos": self.pos,
            "cur": self.w[self.pos],                 # وزن جعبه فعلي
            "nxt": None if last else self.w[self.pos + 1],  # وزن جعبه بعدي
            "is_last": last,
            "sorted": self.is_sorted(),
        }

    def step(self, action):
        """اعمال اقدام عامل روي محيط"""
        self.steps += 1
        if action == "SWAP" and self.pos < len(self.w) - 1:
            self.w[self.pos], self.w[self.pos + 1] = \
                self.w[self.pos + 1], self.w[self.pos]
            self.swaps += 1
        elif action == "MOVE_RIGHT" and self.pos < len(self.w) - 1:
            self.pos += 1
        elif action == "MOVE_HOME":
            self.pos = 0
        # STOP يا اقدام غيرمجاز: تاثيري ندارد
        return self.percept()

    def show(self, title="ليست"):
        print(f"{title} (موقعيت عامل: {self.pos}): " +
              " | ".join(f"{x:3d}" for x in self.w))


# ---------------- عامل واکنشی ساده ----------------
class SimpleReactiveAgent:
    """
    جدول قواعد if-then (به ترتیب اولویت):
      R1: کل لیست مرتب شده          -> STOP
      R2: روی آخرین جعبه هستم (دیوار)-> MOVE_HOME  (پایان یک پاس)
      R3: وزن فعلی > وزن بعدی       -> SWAP
      R4: در غیر این صورت            -> MOVE_RIGHT
    """

    def act(self, p):
        # R1 : شرط خاتمه
        if p["sorted"]:
            return "STOP"

        # R2 : رسیدن به انتهاي لیست -> بازگشت براي پاس بعدی
        if p["is_last"]:
            return "MOVE_HOME"

        # R3 : زوج وارونه؟ جابجا کن (عامل در جا می‌ماند و دوباره می‌سنجد)
        if p["cur"] > p["nxt"]:
            return "SWAP"

        # R4 : زوج مرتب است -> حرکت به جعبه بعدي
        return "MOVE_RIGHT"


# ---------------------- اجرا ----------------------
def main():
    random.seed(42)          # برای تکرارپذیری (اختیاری)
    env = LinearEnv()
    agent = SimpleReactiveAgent()

    env.show("حالت اوليه")
    print(f"هدف: مرتب‌سازي {N} جعبه از کوچک به بزرگ\n")

    MAX_STEPS = 5000
    for _ in range(MAX_STEPS):
        p = env.percept()
        action = agent.act(p)

        if action == "STOP":
            print(">>> عامل متوقف شد: کل لیست مرتب شد.")
            break

        nxt_txt = "-" if p["nxt"] is None else p["nxt"]
        print(f"گام {env.steps + 1:3d} | pos={p['pos']} | "
              f"فعلی={p['cur']:3d} , بعدی={str(nxt_txt):>3s} -> {action}")
        env.step(action)
    else:
        print("خطا: عامل در مهلت تعیین‌شده به هدف نرسيد.")

    env.show("حالت نهايي")
    print(f"آمار: گام ها = {env.steps} , جابجايي ها = {env.swaps} , "
          f"مرتب؟ {env.is_sorted()}")


if __name__ == "__main__":
    main()
