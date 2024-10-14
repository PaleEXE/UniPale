use std::collections::HashMap;

fn infix_to_postfix(expression: &str) -> Vec<String> {
    let precedence = |op: &str| match op {
        "~" => 4,
        "&" => 3,
        "^" => 2,
        "|" => 1,
        "-" => 0,
        "=" => 0,
        _ => -1,
    };

    let mut output: Vec<String> = Vec::new();
    let mut operators: Vec<String> = Vec::new();

    for char in expression.chars() {
        let c = char.to_string();
        if char.is_alphanumeric() {
            output.push(c);
        } else if ["~", "&", "^", "|", "-", "="].contains(&c.as_str()) {
            while !operators.is_empty() && precedence(&operators.last().unwrap()) >= precedence(&c)
            {
                output.push(operators.pop().unwrap());
            }
            operators.push(c.clone());
        } else if char == '(' {
            operators.push(c);
        } else if char == ')' {
            while *operators.last().unwrap() != "(" {
                output.push(operators.pop().unwrap());
            }
            operators.pop();
        }
    }

    while !operators.is_empty() {
        output.push(operators.pop().unwrap());
    }

    output
}

struct PExp {
    expression: String,
    post_expression: Vec<String>,
    variable: Vec<String>,
    key_elements: HashMap<String, Vec<bool>>,
    num_var: usize,
}

impl PExp {
    fn new(expression: &str) -> Self {
        let post_expression = infix_to_postfix(expression);
        let mut exp = PExp {
            expression: expression.to_string(),
            post_expression,
            variable: vec![],
            key_elements: HashMap::new(),
            num_var: 0,
        };
        exp.variable = exp.chars();
        exp.key_elements = exp.build_table();
        exp
    }

    fn chars(&self) -> Vec<String> {
        let mut seen = Vec::new();
        self.expression
            .chars()
            .filter(|c| c.is_alphanumeric())
            .map(|c| c.to_string())
            .filter(|c| {
                if seen.contains(c) {
                    false
                } else {
                    seen.push(c.clone());
                    true
                }
            })
            .collect()
    }

    fn build_table(&mut self) -> HashMap<String, Vec<bool>> {
        self.num_var = self.variable.len();
        let mut table = HashMap::new();
        for (i, var) in self.variable.iter().enumerate() {
            let j = 2_usize.pow((i + 1) as u32);
            let mut pattern = Vec::new();
            let mut flag = true;

            while pattern.len() < 2_usize.pow(self.num_var as u32) {
                for _ in 0..(2_usize.pow(self.num_var as u32) / j) {
                    pattern.push(flag);
                }
                flag = !flag;
            }

            table.insert(var.clone(), pattern);
        }
        table
    }

    fn solve(&mut self) {
        let mut solve_stack: Vec<String> = Vec::new();
        for elem in &self.post_expression {
            if self.key_elements.contains_key(elem) {
                solve_stack.push(elem.clone());
                continue;
            }
            let right = solve_stack.pop().unwrap();
            let value: Vec<bool>;
            let key: String;

            if elem == "~" {
                value = self.key_elements[&right].iter().map(|x| !x).collect();
                key = format!("~{}", right);
            } else {
                let left = solve_stack.pop().unwrap();
                key = format!("{}{}{}", left, elem, right);

                value = match elem.as_str() {
                    "&" => self.key_elements[&left]
                        .iter()
                        .zip(&self.key_elements[&right])
                        .map(|(l, r)| *l && *r)
                        .collect(),
                    "|" => self.key_elements[&left]
                        .iter()
                        .zip(&self.key_elements[&right])
                        .map(|(l, r)| *l || *r)
                        .collect(),
                    "^" => self.key_elements[&left]
                        .iter()
                        .zip(&self.key_elements[&right])
                        .map(|(l, r)| *l ^ *r)
                        .collect(),
                    "=" => self.key_elements[&left]
                        .iter()
                        .zip(&self.key_elements[&right])
                        .map(|(l, r)| l == r)
                        .collect(),
                    "-" => self.key_elements[&left]
                        .iter()
                        .zip(&self.key_elements[&right])
                        .map(|(l, r)| !l || *r)
                        .collect(),
                    _ => panic!("Invalid expression: {}", self.expression),
                };
            }

            self.key_elements.insert(key.clone(), value);
            solve_stack.push(key.clone());
            self.variable.push(key);
        }
    }

    fn show(&self) {
        for (key, value) in &self.key_elements {
            print!(
                "{}: {:?}\n",
                key,
                value
                    .iter()
                    .map(|x| if *x { 1 } else { 0 })
                    .collect::<Vec<u8>>()
            );
        }
    }

    fn final_answer(&self) -> Vec<bool> {
        self.key_elements[&self.variable.last().unwrap().clone()].clone()
    }
}

fn main() {
    let mut exp0 = PExp::new("a|b");
    exp0.solve();
    exp0.show();
    println!("\n");
    let mut exp1 = PExp::new("~(a&b)|(c|d)");
    exp1.solve();
    exp1.show();
    println!("{:?}", exp1.final_answer() == exp0.final_answer());
}
