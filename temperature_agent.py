# -*- coding: utf-8 -*-
"""
عامل واکنشی ساده (Simple Reactive Agent) براي كنترل دما در محيط 2 خانه
هدف: نگه داشتن دماي هر دو خانه در حدود 20 درجه سانتي‌گراد
     خانه 1 با دماي اوليه 17 درجه ، خانه 2 با دماي اوليه 24 درجه

ويژگي عامل واکنشی ساده:
  اقدام = تابع فقط از «ادراك فعلي» (if-then) و بدون هيچ حافظه‌اي.
  قاعده به‌صورت مستقل روي هر خانه اعمال مي‌شود.
"""

TARGET = 20.0      # دماي هدف
HEAT_STEP = 1.0    # هر گام گرمایش: +1 درجه
COOL_STEP = 1.0    # هر گام سرمایش: -1 درجه


# ------------------- محيط 2 خانه -------------------
class TempEnv:
    def __init__(self, temps=None):
        # temps = [دمای خانه 1 , دمای خانه 2]
        self.temps = list(temps) if temps is not None else [17.0, 24.0]

    def percept(self):
        """ادراك فعلي عامل: دماي لحظه‌اي هر دو خانه"""
        return {"temps": tuple(self.temps)}

    @staticmethod
    def at_target(t):
        return t == TARGET

    def all_at_target(self):
        return all(self.at_target(t) for t in self.temps)

    def step(self, actions):
        """اعمال اقدام هر خانه روي محيط (بروزرساني دماها)"""
        for i, a in enumerate(actions):
            if a == "HEATER_ON":
                self.temps[i] += HEAT_STEP
            elif a == "COOLER_ON":
                self.temps[i] -= COOL_STEP
            # IDLE : بدون تغيير دما
        return self.percept()

    def show(self, title="محيط"):
        print(f"{title}: خانه 1 = {self.temps[0]:g}°C | "
              f"خانه 2 = {self.temps[1]:g}°C")


# ---------------- عامل واکنشی ساده ----------------
class SimpleReactiveAgent:
    """
    جدول قواعد if-then (به ترتیب اولویت):
      R1: هر دو خانه به 20 درجه رسيدند -> STOP
      R2: دماي خانه < 20 -> HEATER_ON  (برای همان خانه)
      R3: دماي خانه > 20 -> COOLER_ON  (برای همان خانه)
      R4: دماي خانه = 20 -> IDLE       (هيچ اقدامي)
    همان قاعده به‌طور مستقل روي هر خانه ارزيابي مي‌شود.
    """

    @staticmethod
    def rule(t):
        """قاعده واکنشی برای یک خانه — فقط با دمای فعلی"""
        if t < TARGET:          # R2
            return "HEATER_ON"
        if t > TARGET:          # R3
            return "COOLER_ON"
        return "IDLE"           # R4 : دما دقیقاً 20 است

    def act(self, p):
        t1, t2 = p["temps"]

        # R1 : شرط خاتمه (بررسی قبل از قواعد حرارتی)
        if self.at_target(t1) and self.at_target(t2):
            return "STOP", ["IDLE", "IDLE"]

        # R2/R3/R4 : اعمال مستقل قاعده روی هر خانه
        return "RUN", [self.rule(t1), self.rule(t2)]

    @staticmethod
    def at_target(t):
        return t == TARGET


# ---------------------- اجرا ----------------------
def main():
    env = TempEnv()                      # [17, 24]
    agent = SimpleReactiveAgent()

    print("حالت اوليه:")
    env.show()
    print("هدف: 20°C براي هر دو خانه\n")

    for t in range(1, 51):
        p = env.percept()
        status, actions = agent.act(p)

        a1, a2 = actions
        print(f"گام {t:2d} | ادراک: T1={p['temps'][0]:g}°C , "
              f"T2={p['temps'][1]:g}°C | خانه1: {a1} , خانه2: {a2}")

        if status == "STOP":
            print(">>> عامل متوقف شد: هر دو خانه به 20 درجه رسيدند.")
            break

        env.step(actions)
        env.show("      ")
    else:
        print("خطا: عامل به هدف نرسيد (بررسي TARGET/گام‌ها).")

    env.show("حالت نهايي")


if __name__ == "__main__":
    main()
