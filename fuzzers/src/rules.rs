use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct Proposition {
    pub variable: String,
    pub term: String,
}

impl Proposition {
    pub fn new(variable: &str, term: &str) -> Self {
        Self {
            variable: variable.to_string(),
            term: term.to_string(),
        }
    }
}

#[derive(Debug, Clone)]
pub enum Antecedent {
    Is(Proposition),
    Not(Box<Antecedent>),
    And(Box<Antecedent>, Box<Antecedent>),
    Or(Box<Antecedent>, Box<Antecedent>),
}

impl Antecedent {
    pub fn evaluate(&self, state: &HashMap<String, HashMap<String, f64>>) -> f64 {
        match self {
            Antecedent::Is(prop) => state
                .get(&prop.variable)
                .and_then(|terms| terms.get(&prop.term))
                .copied()
                .unwrap_or(0.0),
            Antecedent::Not(inner) => 1.0 - inner.evaluate(state),
            Antecedent::And(left, right) => left.evaluate(state).min(right.evaluate(state)),
            Antecedent::Or(left, right) => left.evaluate(state).max(right.evaluate(state)),
        }
    }
}

#[derive(Clone)]
pub struct Rule {
    pub antecedent: Antecedent,
    pub consequent: Proposition,
}

impl Rule {
    pub fn new(antecedent: Antecedent, consequent: Proposition) -> Self {
        Self {
            antecedent,
            consequent,
        }
    }

    pub fn evaluate(&self, state: &HashMap<String, HashMap<String, f64>>) -> f64 {
        self.antecedent.evaluate(state)
    }
}
