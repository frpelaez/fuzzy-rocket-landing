import pyray as pr

GRAVITY = 1


class Rocket:
    MAX_THRUST = 2
    VEL_THRESHOLD = 1.5

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 9.0

        self.width = 50
        self.height = 80

        self.state = "airborne"

        self.thrusters = {
            "main": Thruster(0, self.height / 2, 0, 1, self.MAX_THRUST, 1.0),
            "left": Thruster(-self.width / 2, 0, -1, 0, self.MAX_THRUST / 2, 0.6),
            "right": Thruster(self.width / 2, 0, 1, 0, self.MAX_THRUST / 2, 0.6),
        }

    def get_thruster(self, name: str) -> Thruster:
        return self.thrusters[name]

    def reset(self, y: int) -> None:
        self.y = y
        self.vy = 9.0
        self.state = "airborne"

    def update(self, dt: float, ground_y: float) -> None:
        if self.state != "airborne":
            return

        force_x = 0.0
        force_y = GRAVITY * dt

        for thruster in self.thrusters.values():
            force = thruster.get_force()
            force_x += force.x * dt
            force_y += force.y * dt

        self.vx += force_x
        self.vy += force_y

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y + self.height / 2 >= ground_y:
            self.y = ground_y - self.height / 2

            if self.vy <= self.VEL_THRESHOLD:
                self.state = "land"
            else:
                self.state = "crash"

            print(f"[INFO] Land/Crash speed: {self.vy:.1f}")

            self.vy = 0.0

    def draw(self) -> None:
        color_body = pr.RAYWHITE
        if self.state == "land":
            color_body = pr.DARKGREEN
        elif self.state == "crash":
            color_body = pr.RED

        pr.draw_rectangle_pro(
            pr.Rectangle(
                self.x,
                self.y,
                self.width,
                self.height,
            ),
            pr.Vector2(self.width / 2, self.height / 2),
            0.0,
            color_body,
        )

        u1 = pr.Vector2(self.x - self.width / 2, self.y - self.height / 2)
        u2 = pr.Vector2(self.x + self.width / 2, self.y - self.height / 2)
        u3 = pr.Vector2(self.x, self.y - self.height / 2 - 30)
        pr.draw_triangle(u1, u2, u3, pr.RED if self.state != "land" else pr.DARKGREEN)

        pr.draw_circle_sector(
            (int(self.x + self.width / 2), int(self.y)), 6.0, 90, 270, 10, pr.DARKGRAY
        )
        pr.draw_circle_sector(
            (int(self.x + self.width / 2), int(self.y)), 3.0, 90, 270, 10, pr.LIGHTGRAY
        )
        pr.draw_circle_sector(
            (int(self.x - self.width / 2), int(self.y)), 6.0, -90, 90, 10, pr.DARKGRAY
        )
        pr.draw_circle_sector(
            (int(self.x - self.width / 2), int(self.y)), 3.0, -90, 90, 10, pr.LIGHTGRAY
        )

        pr.draw_circle(int(self.x), int(self.y) - 10, 15.0, pr.DARKGRAY)
        pr.draw_circle(int(self.x), int(self.y) - 10, 13.0, pr.LIGHTGRAY)

        if self.state == "airborne":
            self.draw_thurst()

    def draw_thurst(self) -> None:
        for thruster in self.thrusters.values():
            thruster.draw(self.x, self.y)

    def draw_state(self, sim_width: int, screen_height: int) -> None:
        match self.state:
            case "land":
                txt = "SUCCESSFULL LANDING!"
                width = pr.measure_text(txt, 45)
                color = pr.DARKGREEN
            case "crash":
                txt = "CRASHED!"
                width = pr.measure_text(txt, 45)
                color = pr.RED
            case _:
                return

        pr.draw_text(
            txt, int((sim_width - width) / 2), int(screen_height / 3), 45, color
        )


class Thruster:
    def __init__(
        self,
        offset_x: float,
        offset_y: float,
        dir_x: float,
        dir_y: float,
        max_force: float,
        flame_scale: float,
    ) -> None:
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.max_force = max_force
        self.activation: float = 0.0
        self.flame_scale = flame_scale

    def get_force(self) -> pr.Vector2:
        total_force = self.max_force * self.activation
        return pr.Vector2(-self.dir_x * total_force, -self.dir_y * total_force)

    def set_thrust(self, thrust: float) -> None:
        self.activation = max(0.0, min(1.0, thrust))

    def draw(self, rocket_x: float, rocket_y: float) -> None:
        if self.activation > 0.01:
            base_x = rocket_x + self.offset_x
            base_y = rocket_y + self.offset_y

            perp_x = -self.dir_y
            perp_y = self.dir_x

            ext_length = 55 * self.activation * self.flame_scale
            ext_width = 15 * self.flame_scale

            o1 = pr.Vector2(base_x + perp_x * ext_width, base_y + perp_y * ext_width)
            o2 = pr.Vector2(
                base_x + self.dir_x * ext_length, base_y + self.dir_y * ext_length
            )
            o3 = pr.Vector2(base_x - perp_x * ext_width, base_y - perp_y * ext_width)

            inn_length = 35 * self.activation * self.flame_scale
            inn_width = 7 * self.flame_scale

            base_int_x = base_x + self.dir_x * 2 * self.flame_scale
            base_int_y = base_y + self.dir_y * 2 * self.flame_scale

            y1 = pr.Vector2(
                base_int_x + perp_x * inn_width, base_int_y + perp_y * inn_width
            )
            y2 = pr.Vector2(
                base_x + self.dir_x * inn_length, base_y + self.dir_y * inn_length
            )
            y3 = pr.Vector2(
                base_int_x - perp_x * inn_width, base_int_y - perp_y * inn_width
            )

            pr.draw_triangle(o1, o2, o3, pr.ORANGE)
            pr.draw_triangle(y1, y2, y3, pr.YELLOW)
