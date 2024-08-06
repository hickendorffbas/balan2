use std::env;
use std::fs::File;
use std::io::{BufReader, Read};


fn main() {

    let args: Vec<String> = env::args().collect();
    let file_name = &args[1];

    let reader = BufReader::new(File::open(file_name.as_str()).unwrap());
    for byte in reader.bytes() {
        println!("{:b}", byte.unwrap());
    }
}

