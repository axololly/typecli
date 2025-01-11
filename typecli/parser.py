from .colour import error
from .commands import Command
from .types import *

class Parser:
    def __init__(self, valid_commands: list[Command] = []) -> None:
        if not valid_commands:
            raise ValueError("list of valid commands is empty.")

        taken_aliases = set(cmd.name for cmd in valid_commands)

        for command in valid_commands:
            for alias in command.aliases:
                if alias in taken_aliases:
                    raise ValueError(f"alias '{alias}' has already been taken by another command. Choose a different alias.")
        
        self._commands = valid_commands
        self._command_lookup = {
            cmd.name: cmd
            for cmd in self._commands
        } | {
            alias: cmd
            for cmd in self._commands
            for alias in cmd.aliases
        }

    def collect_args(self, raw_text: str) -> list[str]:
        args = []
        _arg = ""
        in_quotes: bool = False
        pos = 0

        while pos < len(raw_text):
            char = raw_text[pos]

            match char:
                case '"':
                    # End of quote
                    if in_quotes:
                        args += [_arg]
                        _arg = ""
                        in_quotes = False
                        pos += 1
                    else:
                        in_quotes = True

                case ' ':
                    if not in_quotes:
                        args += [_arg]
                        _arg = ""
                    else:
                        _arg += char
                
                case _:
                    _arg += char
            
            pos += 1
        
        if _arg:
            args += [_arg]
        
        return args
    
    def parse(self, tokens: list[str]) -> None:
        "Parse and run the given tokens."

        command = self._command_lookup.get(tokens[0])

        if not command:
            error(f"No command was found by the name '{tokens[0]}'.")
            return
        
        _parameter_lookup = {
            param.name: param
            for param in command.callback.parameters
        }
        
        current_param_pos = 0
        current_token_pos = 1

        callback_args = ()
        callback_kwargs = {}

        addressed_flags: list[str] = []

        while current_token_pos < len(tokens):
            token = tokens[current_token_pos]
            param = command.callback.parameters[current_param_pos]

            # Keyworded arguments
            if param.kind == param.KEYWORD_ONLY:
                if token.startswith('--'):
                    flag_param = _parameter_lookup.get(token.removeprefix('--').replace('-', '_'))

                    if flag_param:
                        addressed_flags.append(flag_param.name)

                        callback_kwargs[flag_param.name] = True
                        current_token_pos += 1
                        
                        continue
                    else:
                        error(f"No flag found with the name '{token}'.")
                
                if token != f"-{param.name}" and param.default is param.empty:
                    error(f"Invalid parameter name '{token}': expected '-{param.name}'.")
                    return

                # Check if not EOL
                if current_token_pos + 1 == len(tokens):
                    error(f"EOL parsing error: parameter '-{param.name}' had no value.")
                    return
                
                if param.annotation == Char: # type: ignore
                    next_token = tokens[current_token_pos + 1]

                    if len(next_token) != 1:
                        error(f"Invalid input: expected one character for parameter '-{param.name}' but received {len(next_token)} characters.")
                        return
                    
                    callback_kwargs[param.name] = next_token
                    current_token_pos += 1

                if param.annotation == Word: # type: ignore
                    callback_kwargs[param.name] = tokens[current_token_pos + 1]
                    current_token_pos += 1
                    
                if param.annotation == Sentence: # type: ignore
                    for pos in range(current_token_pos + 1, len(tokens)):
                        if tokens[pos].startswith('-') and tokens[pos][1:] in _parameter_lookup:
                            input_end_index = pos
                            break
                    else:
                        input_end_index = len(tokens)

                    callback_kwargs[param.name] = ' '.join(tokens[current_token_pos + 1 : input_end_index])

                    current_token_pos = input_end_index - 1
                
                if param.annotation == int:
                    next_token = tokens[current_token_pos + 1]

                    try:
                        callback_kwargs[param.name] = int(next_token)
                    except ValueError:
                        error(f"Cannot convert '{next_token}' into a base-10 integer.")
                        return
                    
                    current_token_pos += 1
                
                if param.annotation == float:
                    next_token = tokens[current_token_pos + 1]

                    try:
                        callback_kwargs[param.name] = float(next_token)
                    except ValueError:
                        error(f"Cannot convert '{next_token}' into a base-10 integer.")
                        return
                    
                    current_token_pos += 1
            
            # Positional arguments
            else:
                if param.annotation == Char: # type: ignore
                    if len(token) != 1:
                        error(f"Invalid input: expected one character for parameter '-{param.name}' but received {len(token)} characters.")
                        return
                    
                    callback_args += (token,)

                if param.annotation == Word: # type: ignore
                    callback_args += (tokens[current_token_pos],)
                    
                if param.annotation == Sentence: # type: ignore
                    for pos in range(current_token_pos, len(tokens)):
                        if tokens[pos].startswith('-') and tokens[pos][1:] in _parameter_lookup:
                            input_end_index = pos
                            break
                    else:
                        input_end_index = len(tokens)

                    callback_args += (' '.join(tokens[current_token_pos : input_end_index]),)

                    current_token_pos = input_end_index - 1
                
                if param.annotation == int:
                    try:
                        callback_args += (int(token),)
                    except ValueError:
                        error(f"Cannot convert '{token}' into a base-10 integer.")
                        return
                
                if param.annotation == float:
                    try:
                        callback_args += (float(token),)
                    except ValueError:
                        error(f"Cannot convert '{token}' into a base-10 integer.")
                        return
                    
                    current_token_pos += 1
                
            current_token_pos += 1
            current_param_pos += 1
        
        # Set `False` as the default for all flags
        # that weren't mentioned
        callback_kwargs |= {
            param.name: False
            for param in command.callback.parameters
            if param.annotation is Flag
            and param.name not in addressed_flags
        }
        
        command.callback(*callback_args, **callback_kwargs)
    
    def run(self) -> None:
        while True:
            from_cli = input(">>> ")

            if from_cli.startswith('stop'):
                break

            tokens = self.collect_args(from_cli)

            self.parse(tokens)