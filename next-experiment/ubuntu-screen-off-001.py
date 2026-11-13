#!/usr/bin/python3
"""Turn off active local GNOME displays, leaving SSH and authentication alone."""
import json
import subprocess


def run_once(runner=subprocess.run):
    def command(args):
        result = runner(args, capture_output=True, text=True, timeout=5)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or f'exit {result.returncode}')
        return result.stdout.strip()

    rows = []
    sessions = command(['loginctl', 'list-sessions', '--no-legend', '--no-pager'])
    for line in sessions.splitlines():
        session = line.split()[0]
        try:
            text = command(['loginctl', 'show-session', session, '--no-pager',
                            '--property=Name', '--property=User', '--property=Seat',
                            '--property=Remote', '--property=Active', '--property=Type'])
            props = dict(line.split('=', 1) for line in text.splitlines() if '=' in line)
            if (props.get('Remote') != 'no' or props.get('Active') != 'yes'
                    or props.get('Seat') != 'seat0' or props.get('Type') not in ('wayland', 'x11')):
                continue
            user, uid = props['Name'], props['User']
            if not user or user.startswith('-') or not uid.isdecimal():
                raise RuntimeError('Invalid local session identity')
            prefix = ['runuser', '-u', user, '--', 'busctl',
                      f'--address=unix:path=/run/user/{uid}/bus']
            target = ['org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig',
                      'org.gnome.Mutter.DisplayConfig', 'PowerSaveMode']
            before = command(prefix + ['get-property'] + target)
            changed = before != 'i 3'
            if changed:
                command(prefix + ['set-property'] + target + ['i', '3'])
                if command(prefix + ['get-property'] + target) != 'i 3':
                    raise RuntimeError('Display power-off readback failed')
            rows.append(dict(session=session, user=user, state='off', changed=changed))
        except (RuntimeError, KeyError, subprocess.TimeoutExpired) as error:
            rows.append(dict(session=session, state='error', error=str(error)))
    return rows


if __name__ == '__main__':
    result = run_once()
    # The timer retries sessions that have not finished starting; do not spam idle logs.
    changed = [row for row in result if row.get('changed') or row['state'] == 'error']
    if changed:
        print(json.dumps(changed), flush=True)
    raise SystemExit(int(any(row['state'] == 'error' for row in result)))
