"""Repair only the target Binder extension; retain a real PID through async delivery."""
def repair(source, header):
    assert source.count('thread->sender_pid_nr = t->from_pid;') == 1
    assert source.count('kfree(t);') == 2
    assert 'sender_pid_ref' not in source and 'sender_pid_ref' not in header
    anchor='#ifdef CONFIG_ACCESS_TOKENID\n\tu64 sender_tokenid;'
    assert header.count(anchor)==1
    header=header.replace(anchor,'#ifdef CONFIG_ACCESS_TOKENID\n\tstruct pid *sender_pid_ref;\n\tu64 sender_tokenid;',1)
    anchor='\tt->sender_tokenid = READ_ONCE(current->token);'
    assert source.count(anchor)==1
    source=source.replace(anchor,'\t/* Hold the identity, not a reusable numerical outer PID. */\n\tt->sender_pid_ref = get_task_pid(current, PIDTYPE_TGID);\n'+anchor,1)
    source=source.replace('thread->sender_pid_nr = t->from_pid;',
        'thread->sender_pid_nr =\n\t\t\tpid_nr_ns(t->sender_pid_ref, task_active_pid_ns(current));',1)
    source=source.replace('\tkfree(t);','#ifdef CONFIG_ACCESS_TOKENID\n\tput_pid(t->sender_pid_ref);\n#endif\n\tkfree(t);')
    return source,header
