use std::collections::HashMap;

use crate::{membership::MembershipFn, rules::Rule, variables::Variable};

pub struct FuzzyEngine {
    pub inputs: HashMap<String, Variable>,
    pub outputs: HashMap<String, Variable>,
    pub rules: Vec<Rule>,
}

impl FuzzyEngine {
    pub fn new() -> Self {
        Self {
            inputs: HashMap::new(),
            outputs: HashMap::new(),
            rules: Vec::new(),
        }
    }

    pub fn add_input(&mut self, var: Variable) {
        self.inputs.insert(var.name.clone(), var);
    }

    // pub fn inputs(&self) -> &HashMap<String, Variable> {
    //     &self.inputs
    // }

    pub fn add_output(&mut self, var: Variable) {
        self.outputs.insert(var.name.clone(), var);
    }

    // pub fn outputs(&self) -> &HashMap<String, Variable> {
    //     &self.outputs
    // }

    pub fn add_rule(&mut self, rule: Rule) {
        self.rules.push(rule);
    }

    // pub fn rules(&self) -> &[Rule] {
    //     &self.rules
    // }

    pub fn compute(&self, inputs: HashMap<String, f64>) -> HashMap<String, f64> {
        let mut state = HashMap::new();
        for (name, var) in &self.inputs {
            if let Some(&val) = inputs.get(name) {
                state.insert(name.clone(), var.fuzzify(val));
            }
        }

        let mut output_activations: HashMap<String, HashMap<String, f64>> = HashMap::new();
        for rule in &self.rules {
            let activation = rule.evaluate(&state);
            let out_var = &rule.consequent.variable;
            let out_term = &rule.consequent.term;
            let var_activations = output_activations.entry(out_var.clone()).or_default();
            let current_act = var_activations.entry(out_term.clone()).or_insert(0.0);
            *current_act = current_act.max(activation);
        }

        let mut outputs = HashMap::new();
        for (out_name, out_var) in &self.outputs {
            if let Some(activations) = output_activations.get(out_name) {
                let (min_val, max_val) = out_var.universe;
                let steps = 100;
                let step_size = (max_val - min_val) / steps as f64;

                let mut num = 0.0;
                let mut denom = 0.0;
                for i in 0..=steps {
                    let x = min_val + (i as f64) * step_size;
                    let mut agg_membership: f64 = 0.0;
                    for (term_name, &activation) in activations {
                        if let Some(shape) = out_var.terms.get(term_name) {
                            let clipped_act = activation.min(shape.membership(x));
                            agg_membership = agg_membership.max(clipped_act);
                        }
                    }

                    num += x * agg_membership;
                    denom += agg_membership;
                }

                let deffuzified_val = if denom == 0.0 {
                    (min_val + max_val) / 2.0
                } else {
                    num / denom
                };

                outputs.insert(out_name.clone(), deffuzified_val);
            }
        }

        outputs
    }
}
