import gi

gi.require_versions({'Notify': '0.7', 'Gio': '2.0', 'GLib': '2.0', 'AppIndicator3': '0.1', 'Gtk': '3.0'})
from pulsectl import Pulse
from pynput import keyboard
from gi.repository import Notify, GLib, Gtk, AppIndicator3


def main():
    pulse = Pulse('volume-light')
    volume_keys = ['media_volume_up', 'media_volume_down', 'media_volume_mute']
    devices = list(map(lambda sink: sink.description, pulse.sink_list()))
    print(devices)
    Notify.init('volume-light')
    notification = Notify.Notification.new('')
    notification.set_timeout(Notify.EXPIRES_DEFAULT)
    notification.set_hint("synchronous", GLib.Variant.new_strv("volume"))

    indicator = AppIndicator3.Indicator.new('volume-light', 'volume-light', AppIndicator3.IndicatorCategory.OTHER)
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    sink = pulse.get_sink_by_name(pulse.server_info().default_sink_name)

    indicator.set_icon(get_volume_icon(sink.volume.value_flat*100, sink.mute != 0))

    # tray = Gtk.StatusIcon()
    # tray.set_from_icon_name("audio-volume-low")
    # tray.set_tooltip_text("Test")

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
                    indicator.set_icon(get_volume_icon(sink.volume.value_flat * 100, sink.mute != 0))
                if key.name == volume_keys[1]:
                    decreased_volume = sink.volume.value_flat - 0.02
                    if decreased_volume < 0:
                        decreased_volume = 0
                    pulse.volume_set_all_chans(sink, decreased_volume)
                    # notification
                    notification.set_hint("value", GLib.Variant.new_int32(decreased_volume * 100))
                    notification.update("light-volume", None, "")
                    notification.show()
                    indicator.set_icon(get_volume_icon(sink.volume.value_flat * 100, sink.mute != 0))
                if key.name == volume_keys[2]:
                    pulse.mute(sink, sink.mute == 0)
                    notification.set_hint("value", None)
                    notification.update("light-volume " + ("unmuted" if sink.mute == 0 else "muted"), None, "")
                    notification.show()
                    indicator.set_icon(get_volume_icon(sink.volume.value_flat * 100, sink.mute != 0))

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # UI
    menu = Gtk.Menu()
    quit_item = Gtk.MenuItem(label="Quit")
    quit_item.connect("activate", quit)
    quit_item.show()
    menu.append(quit_item)
    separator = Gtk.SeparatorMenuItem()
    separator.show()
    menu.append(separator)
    indicator.set_menu(menu)

    Gtk.main()
    Notify.uninit()


def get_volume_icon(volume, is_muted):
    if is_muted:
        return 'audio-volume-muted'
    if volume < 100.0 / 3:
        icon_name = 'audio-volume-low'
    elif volume < 100.0 / 3 * 2:
        icon_name = 'audio-volume-medium'
    else:
        icon_name = 'audio-volume-high'
    return icon_name


if __name__ == '__main__':
    main()

# docs:
## file:///usr/share/gtk-doc/html/libnotify/index.html
## http://lazka.github.io/pgi-docs/#Notify-0.7/classes/Notification.html#Notify.Notification.set_hint
## http://lazka.github.io/pgi-docs/GLib-2.0/classes/Variant.html#GLib.Variant.new_string