# -*- coding: utf-8 -*-
"""
عامل واکنشی ساده (Simple Reactive Agent) براي مسئله كليد روشنايي در محيط 2*2
هدف: خاموش كردن همه خانه هاي روشن

ويژگي عامل واکنشی ساده:
  اقدام = تابع فقط از «ادراك فعلي» (if-then)
  هيچ حافظه اي از ادراك هاي قبلي و هيچ بروزرساني حالت داخلي وجود ندارد.
"""

import random


# ------------------- محيط 2*2 -------------------
class LightGridEnv:
    def __init__(self, lights=None):
        # lights[y][x] : True = روشن، False = خاموش
        if lights is None:
            lights = [[random.choice([True, False]) for _ in range(2)]
                      for _ in range(2)]
        self.lights = [row[:] for row in lights]
        self.x, self.y = 0, 0          # موقعيت عامل

    def all_off(self):
        return all(not cell for row in self.lights for cell in row)

    def percept(self):
        """ادراك فعلي عامل در هر لحظه"""
        return {
            "pos": (self.x, self.y),
            "light_on": self.lights[self.y][self.x],
            "all_off": self.all_off(),   # سنسور سراسري «همه خاموش شدند؟»
        }

    def step(self, action):
        """اعمال اقدام عامل روي محيط"""
        if action == "TURN_OFF":
            self.lights[self.y][self.x] = False
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
        print("  +" + "--------+" * 2)
        for row in self.lights:
            print("  |" + "".join("  ON  |" if c else " off |" for c in row))
            print("  +" + "--------+" * 2)


# ---------------- عامل واکنشی ساده ----------------
class SimpleReactiveAgent:
    """
    جدول قواعد if-then (به ترتیب اولویت) — فقط بر اساس ادراک فعلی:
      R1: همه خاموش شده اند      -> STOP
      R2: چراغ خانه فعلی روشن است -> TURN_OFF
      R3: حركت ساعتگرد ثابت بر اساس موقعيت:
          (0,0) -> راست ، (1,0) -> پايين ، (1,1) -> چپ ، (0,1) -> بالا
    """

    def act(self, p):
        x, y = p["pos"]

        # R1 : شرط خاتمه
        if p["all_off"]:
            return "STOP"

        # R2 : اولويت با خاموش كردن
        if p["light_on"]:
            return "TURN_OFF"

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
    env = LightGridEnv()
    agent = SimpleReactiveAgent()
    env.show("حالت اوليه")

    for t in range(1, 50):
        p = env.percept()
        action = agent.act(p)
        pos = p["pos"]
        print(f"گام {t:2d} | ادراک: خانه{pos} "
              f"{'روشن' if p['light_on'] else 'خاموش'}"
              f"{'، همه خاموش' if p['all_off'] else ''}"
              f" -> اقدام: {action}")

        if action == "STOP":
            print(">>> عامل متوقف شد: همه خانه ها خاموش هستند.")
            break

        env.step(action)
    else:
        print("خطا: عامل به STOP نرسيد.")

    env.show("حالت نهايي")


if __name__ == "__main__":
    main()
