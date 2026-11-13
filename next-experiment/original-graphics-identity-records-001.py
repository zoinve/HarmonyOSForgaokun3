"""Never infer a UID from a console-corrupted proc-status record."""
import re


def audit_identities(raw, prefix, pids, uid, name):
    expected_domain = 'u:r:' + name + ':s0'
    verified, incomplete = [], []
    for pid in sorted(set(pids)):
        marker = re.escape(prefix + ('IDENTITY pid=%d Uid:' % pid).encode())
        rows = re.findall(marker + rb'\t(\d+)\t(\d+)\t(\d+)\t(\d+)\r?$', raw, re.M)
        for row in rows:
            assert tuple(map(int, row)) == (uid,) * 4, (name, pid, row)
        domains = re.findall(re.escape(prefix + ('DOMAIN pid=%d value=' % pid).encode())
                             + rb'([^\s\[]+)', raw)
        for domain in domains:
            assert domain.decode() == expected_domain, (name, pid, domain)
        if rows and domains:
            verified.append(pid)
        else:
            incomplete.append(pid)
    assert verified, ('no fully witnessed identity', name)
    return dict(pids=verified, uid=uid, domain=expected_domain,
                observed_process_pids=sorted(set(pids)),
                incomplete_identity_pids=incomplete)
