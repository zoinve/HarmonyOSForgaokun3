"""Bind bridge-internal function calls locally; keep public exports available."""
def isolate_command(original, output):
    command=list(original)
    assert command.count('-o')==1
    position=command.index('-o')+1
    assert position<len(command)
    assert str(output)!=command[position], 'never overwrite the original bridge'
    assert not any('Bsymbolic' in arg for arg in command)
    command[position]=str(output)
    command.append('-Wl,-Bsymbolic-functions')
    return command
