use std::collections::HashMap;

use crate::membership::{MembershipFn, Trapezoid, Triangle};

#[derive(Clone)]
pub enum Shape {
    Triangle(Triangle),
    Trapezoid(Trapezoid),
}

impl MembershipFn for Shape {
    fn membership(&self, x: f64) -> f64 {
        match self {
            Shape::Triangle(t) => t.membership(x),
            Shape::Trapezoid(t) => t.membership(x),
        }
    }
}

#[derive(Clone)]
pub struct Variable {
    pub name: String,
    pub universe: (f64, f64),
    pub terms: HashMap<String, Shape>,
}

impl Variable {
    pub fn new(name: &str, min: f64, max: f64) -> Self {
        Self {
            name: name.to_string(),
            universe: (min, max),
            terms: HashMap::new(),
        }
    }

    pub fn add_term(&mut self, term_name: &str, shape: Shape) {
        self.terms.insert(term_name.to_string(), shape);
    }

    pub fn fuzzify(&self, mut x: f64) -> HashMap<String, f64> {
        if x < self.universe.0 {
            x = self.universe.0;
        }
        if x > self.universe.1 {
            x = self.universe.1;
        }

        let mut res = HashMap::new();
        for (term_name, shape) in &self.terms {
            res.insert(term_name.clone(), shape.membership(x));
        }
        res
    }
}
