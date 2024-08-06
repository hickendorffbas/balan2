use std::env;
use std::fs::File;
use std::io::{BufReader, Read};


fn main() {

    let args: Vec<String> = env::args().collect();
    let file_name = &args[1];

    let reader = BufReader::new(File::open(file_name.as_str()).unwrap());
    let mut bytes = reader.bytes();


    let mut stack = Vec::new();

    loop {
        let opcode = bytes.next();
        if opcode.is_none() {
            break;
        }

        match opcode.unwrap().ok().unwrap() {
            1 => {
                //builtin print()

                let popped_arg = stack.pop().unwrap();
                println!("{}", popped_arg);

            },
            2 => {
                // push value (a byte for now)
                let value = bytes.next().unwrap().ok().unwrap();
                stack.push(value);
            },
            _ => {
                todo!("Unknown opode");
            }

        }

    }
}

