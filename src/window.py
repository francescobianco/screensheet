import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf

from src.canvas import AnnotationCanvas


class ScreensheetWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(900, 600)
        self.set_title("Screensheet")

        self.current_file = None
        self.pixbuf = None

        self._build_ui()
        self._setup_actions()

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        header = Gtk.HeaderBar()

        open_btn = Gtk.Button.new_from_icon_name("document-open-symbolic")
        open_btn.set_tooltip_text("Open Image (Ctrl+O)")
        open_btn.connect("clicked", lambda *args: self.on_open(None, None))
        header.pack_start(open_btn)

        save_btn = Gtk.Button.new_from_icon_name("document-save-symbolic")
        save_btn.set_tooltip_text("Save (Ctrl+S)")
        save_btn.connect("clicked", lambda *args: self.on_save(None, None))
        header.pack_end(save_btn)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        toolbar.add_css_class("linked")

        self.tool_group = Gtk.CheckButton()

        tools = [
            ("go-next-symbolic", "Arrow", "arrow", True),
            ("format-text-direction-symbolic", "Line", "line", False),
            ("draw-rectangle-symbolic", "Rectangle", "rect", False),
            ("tool-pencil-symbolic", "Free Draw", "free", False),
            ("x-office-document-symbolic", "Text", "text", False),
        ]

        for icon, tooltip, tool, active in tools:
            btn = Gtk.CheckButton()
            btn.set_icon_name(icon)
            btn.set_tooltip_text(tooltip)
            btn.set_group(self.tool_group)
            btn.set_active(active)
            btn.connect("toggled", self.on_tool_changed, tool)
            toolbar.append(btn)

        header.set_title_widget(toolbar)

        self.canvas = AnnotationCanvas()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_child(self.canvas)

        main_box.append(header)
        main_box.append(scrolled)

        self.set_child(main_box)

    def _setup_actions(self):
        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.on_open)
        self.add_action(open_action)

        save_action = Gio.SimpleAction(name="save")
        save_action.connect("activate", self.on_save)
        self.add_action(save_action)

        quit_action = Gio.SimpleAction(name="quit")
        quit_action.connect("activate", lambda *args: self.close())
        self.add_action(quit_action)

        self.set_accels_for_action("win.open", ["<Ctrl>o"])
        self.set_accels_for_action("win.save", ["<Ctrl>s"])
        self.set_accels_for_action("win.quit", ["<Ctrl>q"])

    def on_tool_changed(self, btn, tool):
        if btn.get_active():
            self.canvas.set_tool(tool)

    def open_image(self, gfile):
        try:
            path = gfile.get_path()
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
            self.current_file = path
            self.canvas.set_image(self.pixbuf)
            filename = path.split("/")[-1]
            self.set_title(f"Screensheet - {filename}")
        except Exception as e:
            print(f"Error opening image: {e}")

    def on_open(self, action, param):
        dialog = Gtk.FileDialog()
        dialog.open(parent=self, callback=self._on_open_callback)

    def _on_open_callback(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            self.open_image(file)
        except Exception:
            pass

    def on_save(self, action, param):
        if self.current_file:
            self.canvas.save_image(self.current_file)
        else:
            self.on_save_as(action, param)

    def on_save_as(self, action, param):
        dialog = Gtk.FileDialog()
        dialog.save(parent=self, callback=self._on_save_as_callback)

    def _on_save_as_callback(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            path = file.get_path()
            self.canvas.save_image(path)
            self.current_file = path
        except Exception:
            pass
