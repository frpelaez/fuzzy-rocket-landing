import json
from pathlib import Path
import random

import pyray as pr

from fuzzy_rocket_landing.config import load_engine_json
from fuzzy_rocket_landing.editor import draw_editor_panel, draw_info_panel
from fuzzy_rocket_landing.rocket import Rocket
from fuzzy_rocket_landing.wind import Wind, WindSystem
from fuzzy_rocket_landing.draw_utils import draw_tree

BASE_CONFIG_PATH = Path("./config/base_config.json")
CONFIG_PATH = Path("./config/config.json")


def main():
    sim_width = 600
    panel_width = 700
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

    dt = 0.15

    rocket = Rocket(pr.get_random_value(30, sim_width - 30), 40)

    wind = Wind(0.3)

    wind_effects = WindSystem(60, sim_width, screen_height - 100)

    ground_y = screen_height - 100
    platform_x = sim_width // 2

    forest = []
    for _ in range(6):
        x_tree = random.uniform(15, sim_width - 15)

        if 200 < x_tree < 400:
            continue

        tree_scale = random.uniform(0.8, 1.3)
        forest.append([x_tree, ground_y, tree_scale])

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

                rocket.reset(pr.get_random_value(30, sim_width - 30), 40)

            except Exception as e:
                print(f"[ERROR] Error reloading config.json: {e}")

        if pr.is_key_pressed(pr.KeyboardKey.KEY_V):
            engine.plot_decision_surface("Height", "VSpeed", "VThrust")

        if pr.is_key_pressed(pr.KeyboardKey.KEY_H):
            engine.plot_decision_surface("ErrorX", "HSpeed", "HThrust")

        if not paused:
            height = ground_y - (rocket.y + rocket.height / 2)
            v_speed = rocket.vy

            error_x = rocket.x - platform_x
            h_speed = rocket.vx

            inputs = {
                "Height": max(0.0, height),
                "VSpeed": v_speed,
                "ErrorX": error_x,
                "HSpeed": h_speed,
            }
            outputs = engine.compute(inputs)

            if "VThrust" not in outputs:
                print("[WARN] Could not recieve any output from engine")

            v_thrust = outputs.get("VThrust", 0.0)
            h_thrust = outputs.get("HThrust", 0.0)

            if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL):
                if pr.is_key_down(pr.KeyboardKey.KEY_UP):
                    v_thrust = 1.0
                if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):
                    rocket.get_thruster("right").set_thrust(1.0)
                else:
                    rocket.get_thruster("right").set_thrust(0.0)
                if pr.is_key_down(pr.KeyboardKey.KEY_RIGHT):
                    rocket.get_thruster("left").set_thrust(1.0)
                else:
                    rocket.get_thruster("left").set_thrust(0.0)

            rocket.get_thruster("main").set_thrust(v_thrust)

            rocket.get_thruster("left").set_thrust(0.0)
            rocket.get_thruster("right").set_thrust(0.0)

            if h_thrust > 0:
                rocket.get_thruster("left").set_thrust(h_thrust)
            elif h_thrust < 0:
                rocket.get_thruster("right").set_thrust(-h_thrust)

            current_wind = wind.update()
            if rocket.state == "airborne":
                rocket.vx += current_wind * dt

            rocket.update(dt, ground_y, platform_x, platform_width)

        pr.begin_drawing()
        pr.clear_background(pr.SKYBLUE)

        # Draw ground and platform
        pr.draw_rectangle(
            0, ground_y, sim_width, screen_height - ground_y, pr.DARKGREEN
        )
        pr.draw_rectangle(
            (sim_width - platform_width) // 2,
            ground_y,
            platform_width,
            10,
            pr.LIGHTGRAY,
        )

        for tree in forest:
            draw_tree(tree[0], tree[1], tree[2])

        # Draw rocket
        rocket.draw()
        rocket.draw_state(sim_width, screen_height)

        # Draw info panel
        info = {
            "height": height,
            "v_speed": v_speed,
            "error_x": error_x,
            "h_speed": h_speed,
            "v_thrust": v_thrust,
            "h_thrust": h_thrust,
            "state": rocket.state,
        }

        draw_info_panel(10, 10, 210, 175, info)

        if draw_editor_panel(sim_width, 0, panel_width, screen_height, config):
            print(f"[INFO] Saving config to '{CONFIG_PATH}'")
            with CONFIG_PATH.open("w") as f:
                json.dump(config, f, indent=2)
            engine = load_engine_json(CONFIG_PATH)

        # Draw wind indicator and particles
        Wind.draw_indicator(current_wind, sim_width)
        wind_effects.update_and_draw(current_wind)

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
