#!/usr/bin/env python3

import sys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from src.window import ScreensheetWindow


APP_ID = "io.github.yafb.screensheet"


class ScreensheetApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = ScreensheetWindow(application=self)
        win.present()

    def do_open(self, files, n_files, hint):
        win = self.props.active_window
        if not win:
            win = ScreensheetWindow(application=self)
        for file in files:
            win.open_image(file)
        win.present()


def main(version):
    app = ScreensheetApplication()
    return app.run(sys.argv)
