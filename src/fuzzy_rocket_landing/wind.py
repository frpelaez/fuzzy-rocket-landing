import math
import random

import pyray as pr


class Wind:
    def __init__(self, max_force: float) -> None:
        self.max_force = max_force
        self.force = 0.0
        self.sign = random.choice([-1, 1])

    def update(self) -> float:
        time = pr.get_time()
        self.force = self.sign * self.max_force * math.sin(time * 0.2) + random.uniform(
            -0.05, 0.05
        )
        return self.force

    @staticmethod
    def draw_indicator(current_wind: float, sim_width: int) -> None:
        wind_bar_x = sim_width // 2 + 20
        wind_bar_y = 50
        pr.draw_text("Wind", wind_bar_x - 20, wind_bar_y + 10, 20, pr.DARKGRAY)
        pr.draw_line(wind_bar_x - 50, wind_bar_y, wind_bar_x + 50, wind_bar_y, pr.GRAY)
        pr.draw_circle(wind_bar_x, wind_bar_y, 3, pr.GRAY)
        visual_length = int(current_wind * 200)
        wind_color = pr.RED if abs(current_wind) > 0.05 else pr.GREEN
        pr.draw_line_ex(
            pr.Vector2(wind_bar_x, wind_bar_y),
            pr.Vector2(wind_bar_x + visual_length, wind_bar_y),
            4,
            wind_color,
        )
        pr.draw_text(
            f"{current_wind:.2f}", wind_bar_x - 15, wind_bar_y - 20, 15, wind_color
        )


class WindSystem:
    def __init__(self, num_particles: int, world_width: int, world_height: int) -> None:
        self.width = world_width
        self.height = world_height
        self.particles = []

        for _ in range(num_particles):
            self.particles.append(self.generate_particle(random_x=True))

    def generate_particle(self, random_x=False):
        x = random.uniform(0, self.width) if random_x else 0
        y = random.uniform(0, self.height)
        length = random.uniform(15.0, 60.0)

        relative_speed = length / 30.0
        thickness = 1.0 if length < 30 else 2.0

        return [x, y, length, relative_speed, thickness]

    def update_and_draw(self, wind_force: float):
        if abs(wind_force) < 0.001:
            return

        vel_base = wind_force * 2000 * pr.get_frame_time()

        wind_color = pr.fade(pr.WHITE, 0.3)

        for i, p in enumerate(self.particles):
            p[0] += vel_base * p[3]

            if vel_base > 0 and p[0] > self.width:
                self.particles[i] = self.generate_particle(random_x=False)
                self.particles[i][0] = -self.particles[i][2]
            elif vel_base < 0 and p[0] < -p[2]:
                self.particles[i] = self.generate_particle(random_x=False)
                self.particles[i][0] = self.width

            start = pr.Vector2(p[0], p[1])
            end = pr.Vector2(p[0] + p[2], p[1])

            pr.draw_line_ex(start, end, p[4], wind_color)
