from typing import Any

import pyray as pr


def draw_editor_panel(
    x: int, y: int, width: int, height: int, config: dict[str, Any]
) -> bool:
    pr.draw_rectangle(x, y, width, height, pr.SKYBLUE)
    r, g, b, _ = pr.RAYWHITE
    pr.draw_rectangle_rounded(
        pr.Rectangle(x + 20, y + 20, width - 40, height - 40), 0.1, 10, (r, g, b, 100)
    )

    title = "RULE EDITOR"
    txt_width = pr.measure_text(title, 40)
    pr.draw_text("RULE EDITOR", x + (width - txt_width) // 2, y + 40, 40, pr.DARKGRAY)

    mouse_pos = pr.get_mouse_position()
    click = pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT)

    terms = get_config_terms(config)

    y_offset = 120
    y_gutter = 10
    rules = config.get("rules", [])
    for i, rule in enumerate(rules):
        cursor_y = int(y + y_offset) + i * y_gutter
        if cursor_y > height - 50:
            break

        cursor_x = x + 30
        pr.draw_text(
            f"R{i + 1}:",
            int(cursor_x),
            cursor_y,
            15,
            pr.DARKGRAY,
        )
        cursor_x += 25

        pr.draw_text("IF ", int(cursor_x), int(y + y_offset + i * y_gutter), 15, pr.RED)
        cursor_x += pr.measure_text("IF ", 15)
        cursor_x, mod_if = draw_logic_node(
            rule["if"], cursor_x, y + y_offset + i * y_gutter, terms, mouse_pos, click
        )

        pr.draw_text(
            " THEN ", int(cursor_x), int(y + y_offset + i * y_gutter), 15, pr.RED
        )
        cursor_x += pr.measure_text(" THEN ", 15)
        cursor_x, mod_then = draw_logic_node(
            rule["then"], cursor_x, y + y_offset + i * y_gutter, terms, mouse_pos, click
        )

        if mod_if or mod_then:
            rule["desc"] = "[Modified from UI]"

        y_offset += 30

    rect_save = pr.Rectangle(x + 30, y + height - 90, width - 60, 60)
    color_button = (
        pr.DARKBLUE if pr.check_collision_point_rec(mouse_pos, rect_save) else pr.BLUE
    )
    pr.draw_rectangle_rounded(rect_save, 0.3, 10, color_button)
    txt_save = "Save and apply"
    width_save = pr.measure_text(txt_save, 30)
    pr.draw_text(
        "Save and apply",
        int(rect_save.x + (rect_save.width - width_save) // 2),
        int(rect_save.y + 18),
        30,
        pr.RAYWHITE,
    )

    if (
        pr.check_collision_point_rec(mouse_pos, rect_save) and click
    ) or pr.is_key_pressed(pr.KeyboardKey.KEY_S):
        return True

    return False


def draw_logic_node(
    node,
    x: int,
    y: int,
    terms: dict[str, list[str]],
    mouse_pos: pr.Vector2,
    click: bool,
):
    cursor_x = x
    modified = False

    if isinstance(node, dict):
        if "var" in node and "is" in node:
            text = f"{node['var']} IS "
            pr.draw_text(text, int(cursor_x), int(y), 15, pr.DARKGRAY)
            cursor_x += pr.measure_text(text, 15) + 2

            term = str(node["is"])
            width = pr.measure_text(term, 15) + 10
            rect = pr.Rectangle(cursor_x, y - 2, width, 16)

            color = pr.LIGHTGRAY
            if pr.check_collision_point_rec(mouse_pos, rect):
                color = pr.GRAY
                if click:
                    lst = terms.get(node["var"], [])
                    if term in lst:
                        idx = (lst.index(term) + 1) % len(lst)
                        node["is"] = lst[idx]
                        modified = True

            pr.draw_rectangle_rec(rect, color)
            pr.draw_text(node["is"], int(cursor_x + 5), int(y + 1), 15, pr.BLACK)
            cursor_x += width + 5

        else:
            for k, v in node.items():
                if k in ["and", "or", "not"]:
                    pr.draw_text(k.upper(), int(cursor_x), int(y), 15, pr.BLUE)
                    cursor_x += pr.measure_text(k.upper(), 15) + 5
                    nuevo_x, mod = draw_logic_node(
                        v, cursor_x, y, terms, mouse_pos, click
                    )
                    cursor_x = nuevo_x
                    modified = modified or mod

    elif isinstance(node, list):
        pr.draw_text("(", int(cursor_x), int(y), 15, pr.DARKGRAY)
        cursor_x += pr.measure_text("(", 15) + 2
        for i, item in enumerate(node):
            nuevo_x, mod = draw_logic_node(item, cursor_x, y, terms, mouse_pos, click)
            cursor_x = nuevo_x
            modified = modified or mod
            if i < len(node) - 1:
                pr.draw_text(" - ", int(cursor_x), int(y), 10, pr.LIGHTGRAY)
                cursor_x += pr.measure_text(" - ", 10)
        pr.draw_text(")", int(cursor_x), int(y), 15, pr.DARKGRAY)
        cursor_x += pr.measure_text(")", 15) + 5

    return cursor_x, modified


def get_config_terms(config: dict[str, Any]) -> dict[str, list[str]]:
    terms: dict[str, list[str]] = {}
    vars = config.get("inputs", []) + config.get("outputs", [])
    for var in vars:
        terms[var["name"]] = [t["name"] for t in var.get("terms", [])]
    return terms


def draw_info_panel(
    x: int, y: int, width: int, height: int, info: dict[str, Any]
) -> None:
    r, g, b, _ = pr.RAYWHITE
    pr.draw_rectangle_rounded(
        pr.Rectangle(x, y, width, height), 0.1, 10, (r, g, b, 100)
    )

    pr.draw_text(f"Height:    {info['height']:.1f}", x + 10, y + 10, 20, pr.DARKGRAY)
    pr.draw_text(f"ErrorX:   {info['error_x']:.1f}", x + 10, y + 30, 20, pr.DARKGRAY)
    pr.draw_text(f"VSpeed:  {info['v_speed']:.2f}", x + 10, y + 50, 20, pr.DARKGRAY)
    pr.draw_text(f"HSpeed:   {info['h_speed']:.2f}", x + 10, y + 70, 20, pr.DARKGRAY)
    pr.draw_text(f"VThrust: {info['v_thrust']:.2f}", x + 10, y + 90, 20, pr.DARKGRAY)
    pr.draw_text(f"HThrust: {info['h_thrust']:.2f}", x + 10, y + 110, 20, pr.DARKGRAY)
    state = info["state"]
    pr.draw_text(
        f"State:     {state}",
        x + 10,
        y + 130,
        20,
        pr.DARKGREEN
        if state == "land"
        else (pr.RED if state == "crash" else pr.DARKGRAY),
    )
    pr.draw_text(f"FPS:       {pr.get_fps()}", x + 10, y + 150, 20, pr.DARKGRAY)
