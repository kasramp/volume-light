from pulsectl import Pulse
# gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Keybinder": "3.0"})
# from gi.repository import Gtk

from pynput import keyboard


def main():
    pulse = Pulse('volume-light')
    volume_keys = ['media_volume_up', 'media_volume_down', 'media_volume_mute']
    devices = list(map(lambda sink: sink.description, pulse.sink_list()))
    print(devices)

    def on_press(key):
        try:
            key.char
        except AttributeError:
            if key.name in volume_keys:
                sink = pulse.get_sink_by_name(pulse.server_info().default_sink_name)
                if key.name == volume_keys[0]:
                    increased_volume = sink.volume.value_flat + 0.02
                    if increased_volume > sink.base_volume:
                        increased_volume = 1
                    pulse.volume_set_all_chans(sink, increased_volume)
                if key.name == volume_keys[1]:
                    decreased_volume = sink.volume.value_flat - 0.02
                    if decreased_volume < 0:
                        decreased_volume = 0
                    pulse.volume_set_all_chans(sink, decreased_volume)
                if key.name == volume_keys[2]:
                    pulse.mute(sink, sink.mute == 0)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()

    # def print_events(ev):
    #     print('Pulse event:', ev)
    #     # ev.t == 'remove' or ev.t == 'new' (update the profile)
    #     ### Raise PulseLoopStop for event_listen() to return before timeout (if any)
    #     # raise pulsectl.PulseLoopStop

    # pulse.event_mask_set('all')
    # pulse.event_callback_set(print_events)
    # pulse.event_listen()
    # timeout=100


if __name__ == '__main__':
    main()
