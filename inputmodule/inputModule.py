def input_loop():
    while True:
        prompt = raw_input(">").split(" ")
        if prompt == "help":
            print("Type 'set [var] [value]' to set a variable to a value\nType 'get [var]' to get the value stored in the variable output as a string\navailable variables are yaw, pitch, output, kernel")
        if prompt == "exit":
            return
        if prompt == "get":
            get()
        if prompt == "set":
            set()
input_loop()
def get():
    
def set():
#need some pointers with reading only the first word of input with split
#also not sure what "state" refers to
#I'm using python 3, so some of the terms are different. ex. "raw_input" is just "input" in 3


