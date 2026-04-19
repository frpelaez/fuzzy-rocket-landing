import fuzzers


def main():
    print("-- Initiating Fuzzy Control System --")

    # Service quality vaiable: 0 - 10
    service = fuzzers.PyVariable("Service", 0.0, 10.0)
    service.add_triangle("Bad", 0.0, 0.0, 5.0)
    service.add_triangle("Good", 0.0, 5.0, 10.0)
    service.add_triangle("Excelent", 5.0, 10.0, 10.0)

    # Food quality vaiable: 0 - 10
    food = fuzzers.PyVariable("Food", 0.0, 10.0)
    food.add_trapezoid("Bad", 0.0, 0.0, 3.0, 7.0)
    food.add_trapezoid("Delicious", 3.0, 7.0, 10.0, 10.0)

    # Tip % variable
    tip = fuzzers.PyVariable("Tip", 0.0, 25.0)
    tip.add_triangle("Low", 0.0, 5.0, 10.0)
    tip.add_triangle("Medium", 10.0, 15.0, 20.0)
    tip.add_triangle("High", 15.0, 20.0, 25.0)

    # Helper antecedents
    serv_bad = fuzzers.PyAntecedent("Service", "Bad")
    serv_good = fuzzers.PyAntecedent("Service", "Good")
    serv_excelent = fuzzers.PyAntecedent("Service", "Excelent")
    food_bad = fuzzers.PyAntecedent("Food", "Bad")
    food_delicious = fuzzers.PyAntecedent("Food", "Delicious")

    # Rules
    rule1 = fuzzers.PyRule(serv_bad | food_bad, "Tip", "Low")
    rule2 = fuzzers.PyRule(serv_good, "Tip", "Medium")
    rule3 = fuzzers.PyRule((serv_good | serv_excelent) & food_delicious, "Tip", "High")

    # Fuzzy engine setup
    engine = fuzzers.PyFuzzyEngine()
    engine.add_input(service)
    engine.add_input(food)
    engine.add_output(tip)
    engine.add_rule(rule1)
    engine.add_rule(rule2)
    engine.add_rule(rule3)

    test_cases = [
        {"Service": 2.0, "Food": 3.0},  # All bad
        {"Service": 5.0, "Food": 5.0},  # All mid
        {"Service": 9.0, "Food": 8.0},  # All good
        {"Service": 2.0, "Food": 9.5},  # Food amazing, bad service
    ]

    print("\nCentroid results:")
    print("-" * 30)
    for case in test_cases:
        res = engine.compute(case)
        tip_percentage = res.get("Tip", 0.0)
        print(f"Entries: {case} -> Suggested tip: {tip_percentage:.2f}%")

    engine.get_variable("Service").plot()
    engine.get_variable("Food").plot()
    engine.get_variable("Tip").plot()
    engine.plot_decision_surface("Service", "Food", "Tip")


if __name__ == "__main__":
    main()
