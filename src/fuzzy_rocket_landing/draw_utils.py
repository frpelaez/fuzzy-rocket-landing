import pyray as pr


def draw_tree(x_base: float, y_base: float, scale: float = 1.0):
    trunk_width = int(16 * scale)
    trunk_height = int(45 * scale)
    leaves_radius = 25 * scale

    x_trunk = int(x_base - trunk_width / 2)
    y_trunk = int(y_base - trunk_height)
    pr.draw_rectangle(x_trunk, y_trunk, trunk_width, trunk_height, pr.DARKBROWN)

    leaves_center_y = y_base - trunk_height + (10 * scale)

    pr.draw_circle(
        int(x_base),
        int(leaves_center_y - leaves_radius * 0.8),
        leaves_radius * 1.1,
        pr.DARKGREEN,
    )

    pr.draw_circle(
        int(x_base - leaves_radius * 0.7), int(leaves_center_y), leaves_radius, pr.GREEN
    )

    pr.draw_circle(
        int(x_base + leaves_radius * 0.7),
        int(leaves_center_y),
        leaves_radius * 0.9,
        pr.LIME,
    )
