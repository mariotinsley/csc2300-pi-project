from os.path import abspath, dirname, exists

def input_loop(state):
    while True:
        prompt = input("->").split(" ")
        if prompt[0] == "help":
            print("Type 'set [var] [value]' to set a variable to a value\nType 'get [var]' to get the value stored in the variable output as a string\navailable variables are yaw, pitch, output, kernel")
        if prompt[0] == "exit":
            return
        if prompt[0] == "get":
            get(state, prompt[1])
        if prompt[0] == "set":
            set(state, prompt[1], prompt[2])

def get(state, var):
    str(getattr(state, var))
	
def set(state, var, value):
    if var in ["yaw", "pitch"]:
	    try:
			int(value)
		except ValueError:
			return state
	elif var == "output":
	    if not exists(dirname(abspath(value))):
		     return state
	elif var == "kernel":
	    return state
    setattr(state, var, eval(value))
    return state

