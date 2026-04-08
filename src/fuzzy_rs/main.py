import json
from pathlib import Path

import pyray as pr

from fuzzy_rs.config import load_engine_json
from fuzzy_rs.editor import draw_editor_panel, draw_info_panel
from fuzzy_rs.rocket import Rocket

BASE_CONFIG_PATH = Path("./config/base_config.json")
CONFIG_PATH = Path("./config/config.json")


def main():
    sim_width = 600
    panel_width = 600
    screen_height = 800
    platform_width = 150

    pr.init_window(
        sim_width + panel_width, screen_height, "Fuzzy Rocket Landing Simulation"
    )
    pr.set_target_fps(60)

    paused = False

    with BASE_CONFIG_PATH.open("r") as f:
        config = json.load(f)

    engine = load_engine_json(BASE_CONFIG_PATH)

    dt = 0.25

    rocket = Rocket(sim_width / 2, 40)

    ground_y = screen_height - 100

    while not pr.window_should_close():
        if pr.is_key_pressed(pr.KeyboardKey.KEY_SPACE):
            paused = not paused

        if pr.is_key_pressed(pr.KeyboardKey.KEY_R):
            print("[INFO] Reseting config back to base...")
            try:
                engine = load_engine_json(BASE_CONFIG_PATH)
                with BASE_CONFIG_PATH.open("r") as f:
                    config = json.load(f)
                print("[INFO] Engine reloaded successfully")

                rocket.reset(40)

            except Exception as e:
                print(f"[ERROR] Error reloading config.json: {e}")

        if pr.is_key_pressed(pr.KeyboardKey.KEY_V):
            engine.plot_decision_surface("Height", "Velocity", "Thrust")

        if not paused:
            height = ground_y - (rocket.y + rocket.height / 2)
            velocity = rocket.vy

            inputs = {"Height": max(0.0, height), "Velocity": velocity}
            res = engine.compute(inputs)

            if "Thrust" not in res:
                print("[WARN] Could not recieve any output from engine")

            # thrust = res.get("Thrust", 0.0)
            thrust = 0.0

            if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL):
                if pr.is_key_down(pr.KeyboardKey.KEY_UP):
                    thrust = 1.0
                if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):
                    rocket.get_thruster("right").set_thrust(1.0)
                else:
                    rocket.get_thruster("right").set_thrust(0.0)
                if pr.is_key_down(pr.KeyboardKey.KEY_RIGHT):
                    rocket.get_thruster("left").set_thrust(1.0)
                else:
                    rocket.get_thruster("left").set_thrust(0.0)

            rocket.get_thruster("main").set_thrust(thrust)

            rocket.update(dt, ground_y)

        pr.begin_drawing()
        pr.clear_background(pr.SKYBLUE)

        # Draw ground and platform
        pr.draw_rectangle(0, ground_y, sim_width, screen_height - ground_y, pr.DARKGRAY)
        pr.draw_rectangle(
            (sim_width - platform_width) // 2,
            ground_y,
            platform_width,
            10,
            pr.YELLOW,
        )
        pr.draw_line(0, 350, sim_width, 350, (15, 15, 15, 50))
        pr.draw_line(0, ground_y - 100, sim_width, ground_y - 100, (15, 15, 15, 50))
        pr.draw_line(0, ground_y - 30, sim_width, ground_y - 30, (15, 15, 15, 50))

        # Draw rocket
        rocket.draw()
        rocket.draw_state(sim_width, screen_height)

        # Draw info panel
        info = {
            "height": height,
            "velocity": velocity,
            "thrust": thrust,
            "state": rocket.state,
        }

        draw_info_panel(10, 10, 200, 120, info)

        if draw_editor_panel(sim_width, 0, panel_width, screen_height, config):
            print(f"[INFO] Saving config to '{CONFIG_PATH}'")
            with CONFIG_PATH.open("w") as f:
                json.dump(config, f, indent=2)
            engine = load_engine_json(CONFIG_PATH)

        # Draw paused text
        if paused:
            txt = "PAUSED"
            txt_width = pr.measure_text(txt, 45)
            pr.draw_text(
                txt,
                int((sim_width - txt_width) / 2),
                int(screen_height / 3),
                45,
                pr.BLACK,
            )

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()
