pub trait MembershipFn {
    fn membership(&self, x: f64) -> f64;
}

#[derive(Clone)]
pub struct Triangle {
    pub a: f64,
    pub b: f64,
    pub c: f64,
}

impl Triangle {
    pub fn new(a: f64, b: f64, c: f64) -> Self {
        Self { a, b, c }
    }
}

impl MembershipFn for Triangle {
    fn membership(&self, x: f64) -> f64 {
        if x <= self.a || x >= self.c {
            0.0
        } else if x == self.b {
            1.0
        } else if x > self.a && x < self.b {
            (x - self.a) / (self.b - self.a)
        } else {
            (self.c - x) / (self.c - self.b)
        }
    }
}

#[derive(Clone)]
pub struct Trapezoid {
    pub a: f64,
    pub b: f64,
    pub c: f64,
    pub d: f64,
}

impl Trapezoid {
    pub fn new(a: f64, b: f64, c: f64, d: f64) -> Self {
        Self { a, b, c, d }
    }
}

impl MembershipFn for Trapezoid {
    fn membership(&self, x: f64) -> f64 {
        if x <= self.a || x >= self.d {
            0.0
        } else if x >= self.b && x <= self.c {
            1.0
        } else if x > self.a && x < self.b {
            (x - self.a) / (self.b - self.a)
        } else {
            (self.d - x) / (self.d - self.c)
        }
    }
}
