mod engine;
mod membership;
mod rules;
mod variables;

use pyo3::prelude::*;

#[pymodule]
mod _fuzzers {
    use std::collections::HashMap;

    use pyo3::prelude::*;

    use crate::engine::FuzzyEngine;
    use crate::membership::{MembershipFn, Trapezoid, Triangle};
    use crate::rules::{Antecedent, Proposition, Rule};
    use crate::variables::{Shape, Variable};

    #[pyclass]
    pub struct PyTriangle {
        inner: Triangle,
    }

    #[pymethods]
    impl PyTriangle {
        #[new]
        fn new(a: f64, b: f64, c: f64) -> Self {
            PyTriangle {
                inner: Triangle::new(a, b, c),
            }
        }

        fn membership(&self, x: f64) -> f64 {
            self.inner.membership(x)
        }
    }

    #[pyclass]
    pub struct PyTrapezoid {
        inner: Trapezoid,
    }

    #[pymethods]
    impl PyTrapezoid {
        #[new]
        fn new(a: f64, b: f64, c: f64, d: f64) -> Self {
            PyTrapezoid {
                inner: Trapezoid::new(a, b, c, d),
            }
        }

        fn membership(&self, x: f64) -> f64 {
            self.inner.membership(x)
        }
    }

    #[pyclass]
    pub struct PyVariable {
        inner: Variable,
    }

    #[pymethods]
    impl PyVariable {
        #[new]
        fn new(name: &str, min: f64, max: f64) -> Self {
            PyVariable {
                inner: Variable::new(name, min, max),
            }
        }

        #[getter]
        fn name(&self) -> String {
            self.inner.name.clone()
        }

        #[getter]
        fn min(&self) -> f64 {
            self.inner.universe.0
        }

        #[getter]
        fn max(&self) -> f64 {
            self.inner.universe.1
        }

        fn add_triangle(&mut self, term_name: &str, a: f64, b: f64, c: f64) {
            let triangle = Triangle::new(a, b, c);
            self.inner.add_term(term_name, Shape::Triangle(triangle));
        }

        fn add_trapezoid(&mut self, term_name: &str, a: f64, b: f64, c: f64, d: f64) {
            let trapezoid = Trapezoid::new(a, b, c, d);
            self.inner.add_term(term_name, Shape::Trapezoid(trapezoid));
        }

        fn fuzzify(&self, x: f64) -> HashMap<String, f64> {
            self.inner.fuzzify(x)
        }
    }

    #[pyclass]
    #[derive(Clone)]
    pub struct PyAntecedent {
        pub inner: Antecedent,
    }

    #[pymethods]
    impl PyAntecedent {
        #[new]
        fn new(variable: &str, term: &str) -> Self {
            PyAntecedent {
                inner: Antecedent::Is(Proposition {
                    variable: variable.to_string(),
                    term: term.to_string(),
                }),
            }
        }

        fn __invert__(&self) -> Self {
            PyAntecedent {
                inner: Antecedent::Not(Box::new(self.inner.clone())),
            }
        }

        fn __and__(&self, other: &PyAntecedent) -> Self {
            PyAntecedent {
                inner: Antecedent::And(Box::new(self.inner.clone()), Box::new(other.inner.clone())),
            }
        }

        fn __or__(&self, other: &PyAntecedent) -> Self {
            PyAntecedent {
                inner: Antecedent::Or(Box::new(self.inner.clone()), Box::new(other.inner.clone())),
            }
        }
    }

    #[pyclass]
    pub struct PyRule {
        inner: Rule,
    }

    #[pymethods]
    impl PyRule {
        #[new]
        fn new(antecedent: &PyAntecedent, conseq_var: &str, conseq_term: &str) -> Self {
            Self {
                inner: Rule::new(
                    antecedent.inner.clone(),
                    Proposition::new(conseq_var, conseq_term),
                ),
            }
        }

        fn evaluate(&self, state: HashMap<String, HashMap<String, f64>>) -> f64 {
            self.inner.evaluate(&state)
        }
    }

    #[pyclass]
    pub struct PyFuzzyEngine {
        inner: FuzzyEngine,
    }

    #[pymethods]
    impl PyFuzzyEngine {
        #[new]
        fn new() -> Self {
            Self {
                inner: FuzzyEngine::new(),
            }
        }

        fn add_input(&mut self, variable: &PyVariable) {
            self.inner.add_input(variable.inner.clone());
        }

        fn add_output(&mut self, variable: &PyVariable) {
            self.inner.add_output(variable.inner.clone());
        }

        fn add_rule(&mut self, rule: &PyRule) {
            self.inner.add_rule(rule.inner.clone());
        }

        fn compute(&self, inputs: HashMap<String, f64>) -> HashMap<String, f64> {
            self.inner.compute(inputs)
        }

        fn input_names(&self) -> Vec<String> {
            self.inner.inputs.keys().cloned().collect()
        }

        fn inputs(&self) -> Vec<PyVariable> {
            self.inner
                .inputs
                .clone()
                .into_values()
                .map(|v| PyVariable { inner: v })
                .collect()
        }

        fn get_input(&self, name: &str) -> Option<PyVariable> {
            self.inner
                .inputs
                .get(name)
                .cloned()
                .map(|v| PyVariable { inner: v })
        }

        fn output_names(&self) -> Vec<String> {
            self.inner.outputs.keys().cloned().collect()
        }

        fn outputs(&self) -> Vec<PyVariable> {
            self.inner
                .outputs
                .clone()
                .into_values()
                .map(|v| PyVariable { inner: v })
                .collect()
        }

        fn get_output(&self, name: &str) -> Option<PyVariable> {
            self.inner
                .outputs
                .get(name)
                .cloned()
                .map(|v| PyVariable { inner: v })
        }

        fn variable_names(&self) -> Vec<String> {
            let mut res = self.input_names();
            res.append(&mut self.output_names());
            res
        }

        fn variables(&self) -> Vec<PyVariable> {
            let mut res = self.inputs();
            res.append(&mut self.outputs());
            res
        }

        fn get_variable(&self, name: &str) -> Option<PyVariable> {
            self.inner
                .inputs
                .get(name)
                .or_else(|| self.inner.outputs.get(name))
                .cloned()
                .map(|v| PyVariable { inner: v })
        }

        fn rules(&self) -> Vec<PyRule> {
            self.inner
                .rules
                .clone()
                .into_iter()
                .map(|r| PyRule { inner: r })
                .collect()
        }
    }
}
