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

    def do_startup(self):
        Gtk.Application.do_startup(self)

        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self._on_open)
        self.add_action(open_action)

        save_action = Gio.SimpleAction(name="save")
        save_action.connect("activate", self._on_save)
        self.add_action(save_action)

        quit_action = Gio.SimpleAction(name="quit")
        quit_action.connect("activate", lambda *args: self.quit())
        self.add_action(quit_action)

        self.set_accels_for_action("app.open", ["<Ctrl>o"])
        self.set_accels_for_action("app.save", ["<Ctrl>s"])
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])

    def _on_open(self, action, param):
        win = self.props.active_window
        if win:
            win.on_open(action, param)

    def _on_save(self, action, param):
        win = self.props.active_window
        if win:
            win.on_save(action, param)

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
