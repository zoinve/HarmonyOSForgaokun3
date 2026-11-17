"""Preserve authentic oneway caller identity for the original OHOS service ABI."""
OLD = '''\t\t} else {
\t\t\ttrd->sender_pid = 0;
\t\t}

\t\tret = binder_apply_fd_fixups(proc, t);'''
NEW = '''\t\t} else {
\t\t\ttrd->sender_pid = 0;
#ifdef CONFIG_ACCESS_TOKENID
\t\t\t/* Original OHOS services key oneway state by the real caller PID. */
\t\t\tif ((cmd == BR_TRANSACTION || cmd == BR_TRANSACTION_SEC_CTX) &&
\t\t\t    (t->flags & TF_ONE_WAY))
\t\t\t\ttrd->sender_pid = pid_nr_ns(t->sender_pid_ref,
\t\t\t\t\t\t\t task_active_pid_ns(current));
#endif
\t\t}

\t\tret = binder_apply_fd_fixups(proc, t);'''


def repair(source):
    assert source.count(OLD) == 1
    assert 't->sender_pid_ref = get_task_pid(current, PIDTYPE_TGID);' in source
    assert source.count('put_pid(t->sender_pid_ref);') == 2
    return source.replace(OLD, NEW, 1)
