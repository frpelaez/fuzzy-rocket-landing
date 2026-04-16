import json
from typing import Any
from collections.abc import Sequence

import fuzzers


def load_engine_json(filepath: str) -> fuzzers.PyFuzzyEngine:
    with open(filepath, "r") as f:
        config = json.load(f)

    engine = fuzzers.PyFuzzyEngine()

    add_variables(engine, config.get("inputs", []), is_input=True)
    add_variables(engine, config.get("outputs", []), is_input=False)

    for rule_data in config.get("rules", []):
        desc = rule_data["desc"]
        print(f"[INFO] Successfully loaded rule: {desc}")
        antecedent = parse_condition(rule_data["if"])
        consequent = rule_data["then"]
        print(
            f"[INFO] Processing consequent: THEN {consequent['var']} IS {consequent['is']}"
        )
        rule = fuzzers.PyRule(antecedent, consequent["var"], consequent["is"])
        engine.add_rule(rule)

    return engine


def add_variables(
    engine: fuzzers.PyFuzzyEngine, var_list: Sequence[dict[str, Any]], is_input: bool
):
    for var_data in var_list:
        var = fuzzers.PyVariable(var_data["name"], var_data["min"], var_data["max"])
        print(
            f"[INFO] Adding variable: {var_data['name']} with universe ({var_data['min']}, {var_data['max']})"
        )
        for term in var_data["terms"]:
            if term["type"] == "triangle":
                var.add_triangle(term["name"], *term["points"])
                print(
                    f"[INFO]   Adding triangle for {term['name']}: {[t for t in term['points']]}"
                )
            if term["type"] == "trapezoid":
                print(
                    f"[INFO]   Adding trapezoid for {term['name']}: {[t for t in term['points']]}"
                )
                var.add_trapezoid(term["name"], *term["points"])

        if is_input:
            engine.add_input(var)
        else:
            engine.add_output(var)


def parse_condition(rule_node: dict[str, Any]) -> fuzzers.PyAntecedent:
    if "var" in rule_node and "is" in rule_node:
        print(
            f"[INFO] Processing condition: IF {rule_node['var']} IS {rule_node['is']}"
        )
        return fuzzers.PyAntecedent(rule_node["var"], rule_node["is"])

    if "and" in rule_node:
        print(f"[INFO] Processing AND rule with {len(rule_node['and'])} conditions")
        conditions = [parse_condition(cond) for cond in rule_node["and"]]
        res = conditions[0]
        for cond in conditions[1:]:
            res = res & cond
        return res

    if "or" in rule_node:
        print(f"[INFO] Processing OR rule with {len(rule_node['or'])} conditions")
        conditions = [parse_condition(cond) for cond in rule_node["or"]]
        res = conditions[0]
        for cond in conditions[1:]:
            res = res | cond
        return res

    if "not" in rule_node:
        print("[INFO] Processing NOT rule")
        condition = parse_condition(rule_node["not"])
        return ~condition

    raise ValueError(f"Unsupported rule: {rule_node}")
