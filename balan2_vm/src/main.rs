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

        //println!("running opcode {:?} on stack {:?}", opcode.as_ref().unwrap().as_ref().ok().as_ref().unwrap(), stack);


        match opcode.unwrap().ok().unwrap() {
            1 => { //builtin print()
                let popped_arg = stack.pop().unwrap();
                println!("{}", popped_arg);
            },
            2 => { // push value (a byte for now)
                let value = bytes.next().unwrap().ok().unwrap();
                stack.push(value);
            },
            3 => { //plus
                let left = stack.pop().unwrap();
                let right = stack.pop().unwrap();
                stack.push(left + right);
            },
            4 => { //store
                let address = bytes.next().unwrap().ok().unwrap(); //TODO: this is an idiotic amount of unwrapping
                stack[usize::from(address)] = stack.pop().unwrap();
            },
            5 => { //load
                let address = bytes.next().unwrap().ok().unwrap(); //TODO: this is an idiotic amount of unwrapping
                let value = stack[usize::from(address)].clone();
                stack.push(value);
            },


            _ => {
                todo!("Unknown opode");
            }

        }

    }
}

