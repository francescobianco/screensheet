import math
import cairo
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject


class AnnotationCanvas(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.pixbuf = None
        self.annotations = []
        self.current_tool = "arrow"
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_path = []
        self.stroke_color = (1.0, 0.2, 0.2, 1.0)
        self.stroke_width = 3

        self.set_draw_func(self.do_draw, None)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self.on_button_press)
        gesture.connect("released", self.on_button_release)
        self.add_controller(gesture)

        motion = Gtk.EventControllerMotion()
        motion.connect("motion", self.on_motion)
        self.add_controller(motion)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

    def set_image(self, pixbuf):
        self.pixbuf = pixbuf
        self.annotations = []
        self.queue_draw()

    def set_tool(self, tool):
        self.current_tool = tool

    def set_color(self, rgba):
        self.stroke_color = rgba

    def set_width(self, width):
        self.stroke_width = width

    def _get_image_coords(self, x, y):
        alloc = self.get_allocation()
        if self.pixbuf is None:
            return x, y
        img_scale = min(alloc.width / self.pixbuf.get_width(), alloc.height / self.pixbuf.get_height())
        offset_x = (alloc.width - self.pixbuf.get_width() * img_scale) / 2
        offset_y = (alloc.height - self.pixbuf.get_height() * img_scale) / 2
        img_x = (x - offset_x) / img_scale
        img_y = (y - offset_y) / img_scale
        return img_x, img_y

    def do_draw(self, area, cr, data, width, height):
        cr.set_source_rgba(0.5, 0.5, 0.5, 1)
        cr.paint()

        if self.pixbuf:
            alloc = self.get_allocation()
            scale = min(alloc.width / self.pixbuf.get_width(), alloc.height / self.pixbuf.get_height())
            img_w = self.pixbuf.get_width() * scale
            img_h = self.pixbuf.get_height() * scale
            offset_x = (alloc.width - img_w) / 2
            offset_y = (alloc.height - img_h) / 2

            cr.save()
            cr.translate(offset_x, offset_y)
            cr.scale(scale, scale)
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
            cr.paint()
            cr.restore()

            cr.save()
            cr.translate(offset_x, offset_y)
            cr.scale(scale, scale)

            for annotation in self.annotations:
                self._draw_annotation(cr, annotation)

            if self.drawing and self.current_path:
                self._draw_current(cr)

            cr.restore()

    def _draw_annotation(self, cr, annotation):
        cr.save()
        cr.set_source_rgba(*self.stroke_color)
        cr.set_line_width(self.stroke_width)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        ann_type = annotation["type"]

        if ann_type == "arrow":
            self._draw_arrow(cr, annotation)
        elif ann_type == "line":
            cr.move_to(annotation["x1"], annotation["y1"])
            cr.line_to(annotation["x2"], annotation["y2"])
            cr.stroke()
        elif ann_type == "rect":
            x = min(annotation["x1"], annotation["x2"])
            y = min(annotation["y1"], annotation["y2"])
            w = abs(annotation["x2"] - annotation["x1"])
            h = abs(annotation["y2"] - annotation["y1"])
            cr.rectangle(x, y, w, h)
            cr.stroke()
        elif ann_type == "free":
            if annotation["points"]:
                cr.move_to(annotation["points"][0][0], annotation["points"][0][1])
                for point in annotation["points"][1:]:
                    cr.line_to(point[0], point[1])
                cr.stroke()
        elif ann_type == "text":
            cr.set_font_size(16)
            cr.move_to(annotation["x1"], annotation["y1"])
            cr.show_text(annotation.get("text", ""))

        cr.restore()

    def _draw_arrow(self, cr, ann):
        x1, y1 = ann["x1"], ann["y1"]
        x2, y2 = ann["x2"], ann["y2"]

        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()

        angle = 0.4
        size = 15
        dx = x2 - x1
        dy = y2 - y1
        base_angle = math.atan2(dy, dx)

        cr.move_to(x2, y2)
        cr.line_to(
            x2 - size * math.cos(base_angle - angle),
            y2 - size * math.sin(base_angle - angle),
        )
        cr.move_to(x2, y2)
        cr.line_to(
            x2 - size * math.cos(base_angle + angle),
            y2 - size * math.sin(base_angle + angle),
        )
        cr.stroke()

    def _draw_current(self, cr):
        cr.save()
        cr.set_source_rgba(*self.stroke_color)
        cr.set_line_width(self.stroke_width)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)

        if self.current_tool == "free" and len(self.current_path) > 1:
            cr.move_to(self.current_path[0][0], self.current_path[0][1])
            for point in self.current_path[1:]:
                cr.line_to(point[0], point[1])
            cr.stroke()
        elif self.current_tool in ("arrow", "line"):
            end = self.current_path[-1]
            cr.move_to(self.start_x, self.start_y)
            cr.line_to(end[0], end[1])
            cr.stroke()
            if self.current_tool == "arrow":
                self._draw_arrow(cr, {
                    "x1": self.start_x,
                    "y1": self.start_y,
                    "x2": end[0],
                    "y2": end[1],
                })
        elif self.current_tool == "rect":
            end = self.current_path[-1]
            x = min(self.start_x, end[0])
            y = min(self.start_y, end[1])
            w = abs(end[0] - self.start_x)
            h = abs(end[1] - self.start_y)
            cr.rectangle(x, y, w, h)
            cr.stroke()

        cr.restore()

    def on_button_press(self, gesture, n_press, x, y):
        if self.pixbuf is None:
            return

        img_x, img_y = self._get_image_coords(x, y)

        if self.current_tool == "text":
            self._add_text(img_x, img_y)
            return

        self.drawing = True
        self.start_x = img_x
        self.start_y = img_y
        self.current_path = [(img_x, img_y)]

    def on_button_release(self, gesture, n_press, x, y):
        if not self.drawing:
            return

        img_x, img_y = self._get_image_coords(x, y)

        if self.current_tool == "free":
            self.annotations.append({
                "type": "free",
                "points": list(self.current_path),
            })
        elif self.current_tool in ("arrow", "line"):
            self.annotations.append({
                "type": self.current_tool,
                "x1": self.start_x,
                "y1": self.start_y,
                "x2": img_x,
                "y2": img_y,
            })
        elif self.current_tool == "rect":
            self.annotations.append({
                "type": "rect",
                "x1": self.start_x,
                "y1": self.start_y,
                "x2": img_x,
                "y2": img_y,
            })

        self.drawing = False
        self.current_path = []
        self.queue_draw()

    def on_motion(self, controller, x, y):
        if not self.drawing:
            return

        img_x, img_y = self._get_image_coords(x, y)
        self.current_path.append((img_x, img_y))
        self.queue_draw()

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_z and state & Gdk.ModifierType.CONTROL_MASK:
            if self.annotations:
                self.annotations.pop()
                self.queue_draw()
            return True
        return False

    def _add_text(self, x, y):
        toplevel = self.get_root()
        if not isinstance(toplevel, Gtk.Window):
            return

        dialog = Gtk.Dialog(
            title="Add Text",
            transient_for=toplevel,
            modal=True,
        )

        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("OK", Gtk.ResponseType.OK)

        entry = Gtk.Entry()
        entry.set_margin_start(10)
        entry.set_margin_end(10)
        entry.set_margin_top(10)
        entry.set_margin_bottom(10)
        entry.set_activates_default(True)

        content_area = dialog.get_content_area()
        content_area.append(entry)

        dialog.set_default_response(Gtk.ResponseType.OK)

        def on_response(d, response):
            if response == Gtk.ResponseType.OK and entry.get_text():
                self.annotations.append({
                    "type": "text",
                    "x1": x,
                    "y1": y,
                    "text": entry.get_text(),
                })
                self.queue_draw()
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def save_image(self, path):
        if self.pixbuf is None:
            return

        width = self.pixbuf.get_width()
        height = self.pixbuf.get_height()

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(surface)

        Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
        cr.paint()

        for annotation in self.annotations:
            self._draw_annotation(cr, annotation)

        surface.write_to_png(path)
