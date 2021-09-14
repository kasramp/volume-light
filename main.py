import gi

gi.require_versions({'Notify': '0.7', 'Gio': '2.0', 'GLib': '2.0'})
from pulsectl import Pulse
from pynput import keyboard
from gi.repository import Notify, GLib


def main():
    pulse = Pulse('volume-light')
    volume_keys = ['media_volume_up', 'media_volume_down', 'media_volume_mute']
    devices = list(map(lambda sink: sink.description, pulse.sink_list()))
    print(devices)

    Notify.init('volume-light')
    notification = Notify.Notification.new('')
    notification.set_timeout(Notify.EXPIRES_DEFAULT)
    notification.set_hint("synchronous", GLib.Variant.new_strv("volume"))

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
                    # notification
                    notification.set_hint("value", GLib.Variant.new_int32(increased_volume * 100))
                    notification.update("light-volume", None, "")
                    notification.show()
                if key.name == volume_keys[1]:
                    decreased_volume = sink.volume.value_flat - 0.02
                    if decreased_volume < 0:
                        decreased_volume = 0
                    pulse.volume_set_all_chans(sink, decreased_volume)
                    # notification
                    notification.set_hint("value", GLib.Variant.new_int32(decreased_volume * 100))
                    notification.update("light-volume", None, "")
                    notification.show()
                if key.name == volume_keys[2]:
                    pulse.mute(sink, sink.mute == 0)
                    notification.set_hint("value", None)
                    notification.update("light-volume " + ("unmuted" if sink.mute == 0 else "muted"), None, "")
                    notification.show()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()

    Notify.uninit()


if __name__ == '__main__':
    main()
