if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
    exit
fi

cd compiler
python3 main.py ../$1 ../target/out.bb2

cd ..

cd balan2_vm
cargo run ../target/out.bb2


