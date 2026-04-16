import matplotlib.pyplot as plt
import numpy as np


def _plot_variable(self):
    x_values = np.linspace(self.min, self.max, 500)
    sample = self.fuzzify(self.min)
    terms = list(sample.keys())
    y_values = {term: [] for term in terms}

    for x in x_values:
        resultados = self.fuzzify(x)
        for term in terms:
            y_values[term].append(resultados.get(term, 0.0))

    plt.figure(figsize=(8, 4))
    for term in terms:
        plt.plot(x_values, y_values[term], label=term, linewidth=2)

    plt.title(f"Fuzzy Variable: {self.name}")
    plt.xlabel(self.name)
    plt.ylabel("Membership level (μ)")
    plt.ylim(-0.05, 1.05)
    plt.xlim(self.min, self.max)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()


def _plot_surface(
    self, input1_name: str, input2_name: str, output_name: str, resolution: int = 50
) -> None:
    print("[INFO] Generating decision surface")

    var1 = self.get_input(input1_name)
    var2 = self.get_input(input2_name)
    out = self.get_output(output_name)

    if not var1 or not var2 or not out:
        print(
            f"[ERROR] Unnable to find some of the variables: {input1_name}, {input2_name}, {output_name}"
        )
        return

    eps1 = (var1.max - var1.min) * 0.0001
    eps2 = (var2.max - var2.min) * 0.0001

    x_range = np.linspace(var1.min + eps1, var1.max - eps1, resolution)
    y_range = np.linspace(var2.min + eps2, var2.max - eps2, resolution)

    X, Y = np.meshgrid(x_range, y_range)
    Z = np.zeros(X.shape)

    for i in range(resolution):
        for j in range(resolution):
            inputs = {input1_name: X[i, j], input2_name: Y[i, j]}
            res = self.compute(inputs)
            Z[i, j] = res.get(output_name, np.nan)

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(X, Y, Z, cmap="plasma", linewidth=0, antialiased=True)

    ax.set_xlabel(f"{input1_name}")
    ax.set_ylabel(f"{input2_name}")
    ax.set_zlabel(f"{output_name}")
    ax.set_title("Fuzzy Decision Surface")

    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()
