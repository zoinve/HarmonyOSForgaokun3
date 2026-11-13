"""Local-only, aspect-preserving QEMU viewer; guest resolution stays unchanged."""
import gi
import os
import signal
import socket
import sys
from pathlib import Path

gi.require_version('Gtk', '3.0')
gi.require_version('GtkVnc', '2.0')
from gi.repository import Gtk, GtkVnc, Gdk

endpoint = sys.argv[1]
window = Gtk.Window(title='HarmonyOS QEMU — Ctrl+Alt+F: fullscreen')
display = GtkVnc.Display()
display.set_scaling(True)
display.set_keep_aspect_ratio(True)
display.set_pointer_local(True)
display.set_pointer_force_visible(True)
display.set_pointer_grab(True)
display.set_keyboard_grab(False)
display.set_read_only(False)
window.add(display)
window.connect('destroy', Gtk.main_quit)
full = True

def key(_window, event):
    global full
    mask = Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK
    if event.state & mask == mask and event.keyval in (Gdk.KEY_f, Gdk.KEY_F):
        full = not full
        window.fullscreen() if full else window.unfullscreen()
        return True
    return False

def initialized(*_args):
    print('CONNECTED scaling=True keep_aspect_ratio=True local_pointer=True',
          'absolute_pointer=' + str(display.is_pointer_absolute()), flush=True)
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            args = (proc / 'cmdline').read_bytes().split(b'\0')
            viewer = (proc / 'comm').read_text().strip() == 'vncviewer' or any(
                arg.endswith(b'/scaled-viewer.py') for arg in args)
            if int(proc.name) != os.getpid() and viewer and endpoint.encode() in args:
                os.kill(int(proc.name), signal.SIGTERM)
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    display.grab_focus()

last_size = None
motion_samples = 0
def motion(_display, event):
    global motion_samples
    if motion_samples < 8:
        print('POINTER_MOTION', round(event.x), round(event.y),
              'absolute=' + str(display.is_pointer_absolute()), flush=True)
        motion_samples += 1
    return False  # GTK-VNC continues normal input forwarding.

def allocated(_display, allocation):
    global last_size
    size = (allocation.width, allocation.height)
    if size != last_size:
        print('VIEWPORT', *size, flush=True)
        last_size = size

window.connect('key-press-event', key)
display.connect('vnc-initialized', initialized)
display.connect('vnc-desktop-resize', lambda _d, w, h: print('GUEST', w, h, flush=True))
display.connect('size-allocate', allocated)
display.connect('motion-notify-event', motion)
display.connect('vnc-pointer-grab', lambda *_: print('POINTER_CAPTURED release=Ctrl+Alt', flush=True))
display.connect('vnc-pointer-ungrab', lambda *_: print('POINTER_RELEASED', flush=True))
display.connect('vnc-error', lambda _d, text: print('ERROR', text, flush=True))
display.connect('vnc-disconnected', lambda *_: Gtk.main_quit())
window.show_all()
window.fullscreen()
connection = socket.socket(socket.AF_UNIX)
connection.connect(endpoint)
assert display.open_fd(connection.detach())
Gtk.main()
