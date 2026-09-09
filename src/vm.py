# this vm is carried by poor design choices ❤️
class VM:
    def __init__(self):
        self.content:bytes = None
        self.constants:list[tuple] = [0]
        self.names:list[str] = []
        self.bp:int = 0               # byte pointer
        self.stack:list = []          # just the stack
        self.variables:dict = {-1:{}} # just variables
        self.return_addrs = []        # just return addresses
        self.next_id:int = 0          # just the uhh yeah the uhh actually yeah its the uhhh the uhh oh ye the uhhh oh uhh the uhh

    def get(self)->int:
        try:
            return self.content[self.bp]
        except:
            return 0

    def fetch(self)->int:
        byte = self.get()
        self.bp += 1
        return byte

    def fetch_number(self)->int:
        number = self.fetch()
        number += self.fetch() * 256
        return number

    def get_constant(self, to_load:int)->int|float|str|None:
        const:tuple = self.constants[to_load]
        const_type:int = const[0]
        const_value:str = const[1]
        if const_type == 0x1a:
            if const_value.count(".") == 0:
                return int(const_value)
            else:
                return float(const_value)
        elif const_type == 0x1f:
            return const_value
        else:
            # unknown type
            return None

    def get_name(self, to_load:int)->str:
        name:str = self.names[to_load]
        return name

    def push(self, value)->None:
        self.stack.append(value)

    def pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            return None

    def get_variable(self, name:str, scope:int, parent_scope:int|None):
        # return scope.name
        value = self.variables.get(scope).get(name)
        if value is None:
            # check parent scope
            if parent_scope is None:
                value = None
            else:
                value = self.variables.get(parent_scope).get(name)
            if value is None:
                # variable doesnt exist
                return None
            else:
                return value
        else:
            return value

    def set_variable(self, name:str, value, scope:int)->None:
        # scope.name = value
        self.variables.get(scope).update({name: value})

    def create_new_scope(self)->int:
        scope_id = self.next_id
        self.next_id += 1
        self.variables.update({scope_id: {}})
        return scope_id

    def destroy_scope(self, scope:int)->None:
        self.variables.pop(scope, None)

    def execute_instruction(self, instruction:int, scope:int, parent_scope:int|None)->int:
        if instruction == 0x1c:    # nop
            pass
        elif instruction == 0x20:    # load_value
            to_load = self.fetch_number()
            value = self.get_constant(to_load)
            self.push(value)
        elif instruction == 0x2a:    # load_literal
            value = self.fetch_number()
            self.push(value)
        elif instruction == 0x30:    # load_name
            to_load = self.fetch_number()
            value = self.get_variable(self.get_name(to_load), scope, parent_scope)
            self.push(value)
        elif instruction == 0x3f:    # store_name
            to_load = self.fetch_number()
            value = self.pop()
            self.set_variable(self.get_name(to_load), value, scope)
        elif instruction == 0x40:    # pop_top
            self.pop()
        elif instruction == 0x4a:    # call
            # pop N arguments and jump to the next popped value
            arg_count = self.fetch_number()
            arguments = []
            for i in range(arg_count):
                arguments.append(self.pop())
            jump_loc = self.pop()
            if type(jump_loc) != int:
                print("error: invalid call address")
                return 1
            # save current location for returning
            return_byte = self.bp
            # jump to jump_loc
            self.bp = jump_loc
            # create a new scope for the variables and shi
            new_scope = self.create_new_scope()
            self.return_addrs.append(return_byte)
            # push arguments back (for parameters)
            for arg in arguments:
                self.push(arg)
        elif instruction == 0x50:    # bin_op
            operator = self.fetch_number()
            right = self.pop()
            if operator not in [11, 14]:
                left = self.pop()
            if   operator == 0:  result = left + right
            elif operator == 1:  result = left - right
            elif operator == 2:  result = left * right
            elif operator == 3:  result = left / right
            elif operator == 4:  result = left == right
            elif operator == 5:  result = left < right
            elif operator == 6:  result = left > right
            elif operator == 7:  result = left <= right
            elif operator == 8:  result = left >= right
            elif operator == 9:  result = left and right
            elif operator == 10: result = left or right
            elif operator == 11: result = not right
            elif operator == 12: result = left & right
            elif operator == 13: result = left | right
            elif operator == 14: result = ~right
            elif operator == 15: result = left ^ right
            elif operator == 16: result = left << right
            elif operator == 17: result = left >> right
            self.push(int(result))
        elif instruction == 0x60:    # jump_label
            target = self.fetch_number()
            self.bp = target
        elif instruction == 0x6a:    # jump_if_false
            condition = self.pop()
            target = self.fetch_number()
            if not condition:
                self.bp = target
        elif instruction == 0x6f:    # jump_if_true
            condition = self.pop()
            target = self.fetch_number()
            if condition:
                self.bp = target
        elif instruction == 0x70:    # return_value
            self.destroy_scope(scope)
            return 0
        elif instruction == 0x77:    # return_const
            to_load = self.fetch_number()
            self.push(self.get_constant(to_load))
            self.destroy_scope(scope)
            return 0
        return 0

    def run(self, content:bytes)->int:
        self.content:bytes = content
        self.constants:list[tuple] = [0]
        self.names:list[str] = []
        self.bp:int = 0    # check the __init__ function to see this comment
        self.stack:list = []    # lists can larp stacks
        self.variables:dict = {-1: {}}
        self.return_addrs = []
        self.next_id:int = 0
        # read magic bytes (A0 FF)
        if self.fetch() != 0xA0 or self.fetch() != 0xFF:
            print("error: invalid binary")
            return 1
        # read constants
        while self.get() != 0xFF:
            const_type = self.fetch()
            # it doesnt matter whether we are reading a number or string
            # we still expect null termination
            const_value:str = ""
            while self.get() != 0x00:
                const_value += chr(self.fetch())
            self.fetch()
            # make a tuple and append it to self.constants
            self.constants.append((const_type, const_value))
            # the next constant (or a 0xFF) is ready to be read
        self.fetch()
        # read names
        while self.get() != 0xFF:
            # read until null terminator (just like last time)
            name:str = ""
            while self.get() != 0x00:
                name += chr(self.fetch())
            self.fetch()
            self.names.append(name)
        self.fetch()
        # execute instructions
        while True:
            instruction = self.fetch()
            if instruction == 0xff:
                print("warning: reached end of text section")
            code:int = self.execute_instruction(instruction, list(self.variables.keys())[-1], None)
            if len(self.variables) < 1:
                print(self.stack)
                return 0
        return 0