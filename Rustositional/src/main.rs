use std::collections::HashMap;

fn infix_to_postfix(expression: &str) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let precedence = |op: &char| match op {
        '~' => 5,
        '&' => 4,
        '^' => 3,
        '|' => 2,
        '-' => 1,
        '=' => 0,
        _ => -1,
    };

    let mut output: Vec<String> = Vec::new();
    let mut operators: Vec<String> = Vec::new();
    let mut current_str: String = String::new();

    for char in expression.chars() {
        if char.is_alphabetic() {
            current_str.push(char);
        } else {
            if !current_str.is_empty() {
                output.push(current_str.clone());
                current_str.clear();
            }

            if ['~', '&', '^', '|', '-', '='].contains(&char) {
                while !operators.is_empty()
                    && precedence(&operators.last().unwrap().chars().last().unwrap()) >= precedence(&char) {
                    output.push(operators.pop().unwrap());
                }
                operators.push(char.to_string());
            } else if char == '(' {
                operators.push(char.to_string());
            } else if char == ')' {
                while !operators.is_empty() && *operators.last().unwrap() != "(" {
                    match operators.pop() {
                        Some(x) => output.push(x),
                        None => return Err("Unbalanced parentheses".into()),
                    }
                }
                if operators.is_empty() {
                    return Err("Unbalanced parentheses".into());
                }
                operators.pop();
            }
        }
    }

    if !current_str.is_empty() {
        output.push(current_str);
    }

    while !operators.is_empty() {
        if operators.last().unwrap() == "(" {
            return Err("Unbalanced parentheses".into());
        }
        output.push(operators.pop().unwrap());
    }

    Ok(output)
}

struct PExp {
    expression: String,
    post_expression: Vec<String>,
    key_elements: HashMap<String, Vec<bool>>,
    num_var: usize,
}

impl PExp {
    fn new(expression: &str) -> Self {
        if let Ok(post_expression) = infix_to_postfix(expression) {
            let mut exp = PExp {
            expression: expression.to_string(),
            post_expression,
            key_elements: HashMap::new(),
            num_var: 0,
        };
        exp.key_elements = exp.build_table();
        exp
        } else {
            panic!("Invalid expression: {}", expression)
        }
    }

    fn vars(&self) -> Vec<String> {
        let mut seen = HashMap::new();
        self.post_expression
            .iter()
            .filter(|s| s.chars().any(|c| c.is_alphanumeric()))
            .map(|s| s.to_string())
            .filter(|s| {
                if seen.contains_key(s) {
                    false
                } else {
                    seen.insert(s.clone(), true);
                    true
                }
            })
            .collect()
    }

    fn build_table(&mut self) -> HashMap<String, Vec<bool>> {
        let variables = self.vars();
        self.num_var = variables.len();
        let mut table = HashMap::new();
        for (i, var) in variables.iter().enumerate() {
            let j = 1 << i + 1;
            let pattern = self.build_col(j);
            table.insert(var.clone(), pattern);
        }
        table
    }

    fn build_col(&mut self, j: usize) -> Vec<bool> {
        let segment = 2_usize.pow(self.num_var as u32) / j;
        let mut col = Vec::with_capacity(1 << self.num_var);
        for _ in 0..(j / 2) {
            col.extend(vec![true; segment]);
            col.extend(vec![false; segment]);
        }
        col
    }

    fn solve(&mut self) {
        let mut solve_stack: Vec<String> = Vec::new();
        for elem in self.post_expression.iter() {
            if self.key_elements.contains_key(elem) {
                solve_stack.push(elem.clone());
                continue;
            }
            let right = solve_stack.pop().expect(
                &format!("Invalid expression: {}", self.expression)
            );
            let value: Vec<bool>;
            let key: String;

            if elem == "~" {
                value = self.key_elements[&right].iter().map(|x| !x).collect();
                key = format!("~{}", right);
            } else {
                let left = solve_stack.pop().expect(
                    &format!("Invalid expression: {}", self.expression)
                );
                key = format!("{}{}{}", left, elem, right);

                value = self.apply_op(elem, &right, &left);
            }

            self.key_elements.insert(key.clone(), value);
            solve_stack.push(key.clone());
        }
    }

    fn apply_op(&self, elem: &String, right: &String, left: &String) -> Vec<bool> {
    let pairs = self.key_elements[left]
        .iter()
        .zip(&self.key_elements[right]);

    let rizz = match elem.as_str() {
        "&" => pairs.map(|(l, r)| *l && *r).collect(),
        "|" => pairs.map(|(l, r)| *l || *r).collect(),
        "^" => pairs.map(|(l, r)| *l ^ *r).collect(),
        "=" => pairs.map(|(l, r)| l == r).collect(),
        "-" => pairs.map(|(l, r)| !l || *r).collect(),
        _ => panic!("Invalid expression: {}", self.expression),
    };
    rizz
}
    fn show_table(&self) {
    let mut sorted_elements: Vec<_> = self.key_elements.iter().collect();
    sorted_elements.sort_by_key(|&(key, _)| key.len());

    let max_key_length = sorted_elements.last().map_or(0, |(key, _)| key.len());

    println!("\n\n");

    for (var, _) in &sorted_elements {
        print!("| {:width$} ", var, width = max_key_length);
    }
    println!("|");

    println!("{}-", "-".repeat((max_key_length + 3) * sorted_elements.len()));

    for i in 0..2_usize.pow(self.num_var as u32) {
        for (_, vec) in &sorted_elements {
            print!("| {:<width$} ", vec[i] as u8, width = max_key_length);
        }
        println!("|");
    }
}
    fn show(&self) {
        let mut sorted_elements = self.key_elements.iter().collect::<Vec<(&String, &Vec<bool>)>>();
        sorted_elements.sort_by_key(|&(key, _)| key.len());
        for (key, val) in sorted_elements {
            print!(
                "{}: {:?}\n",
                key,
                val
                    .iter()
                    .map(|x| *x as u8)
                    .collect::<Vec<u8>>()
            );
        }
    }

    fn final_answer(&self) -> Vec<bool> {
        let mut last_key: String = String::new();
        let mut last_val: Vec<bool> = Vec::new();
        for (key, val) in self.key_elements.iter() {
            if key.len() > last_key.len() {
                last_key = key.to_string();
                last_val = val.to_vec();
            }
        }
        last_val
    }
}

fn main() {
    let mut exp0 = PExp::new("dog-sui");
    exp0.solve();
    exp0.show_table();
    let mut exp1 = PExp::new("~a|b");
    exp1.solve();
    exp1.show_table();
    println!("{:?}", exp1.final_answer() == exp0.final_answer());
}
