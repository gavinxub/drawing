# crop.py
#
# Copyright 2018 Romain F. T.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gdk, Gio, GLib

from .tools import ToolTemplate

class ToolRotate(ToolTemplate):
	__gtype_name__ = 'ModeRotate'

	implements_panel = True

	def __init__(self, window):
		super().__init__('rotate', _("Rotate"), 'view-refresh-symbolic', window)
		self.need_temp_pixbuf = True

		self.add_tool_action_simple('rotate_apply', self.on_apply)

		builder = Gtk.Builder.new_from_resource('/com/github/maoschanz/Drawing/tools/ui/tool_rotate.ui')
		self.bottom_panel = builder.get_object('bottom-panel')
		self.angle_btn = builder.get_object('angle_btn')
		self.angle_btn.connect('value-changed', self.on_angle_changed)

		self.window.bottom_panel_box.add(self.bottom_panel)

	def get_panel(self):
		return self.bottom_panel

	def get_edition_status(self):
		if self.rotate_selection:
			return _("Rotating the selection")
		else:
			return _("Rotating the canvas")

	def on_tool_selected(self, *args):
		self.rotate_selection = (self.window.hijacker_id is not None)
		self.angle_btn.set_value(0.0)
		self.update_temp_pixbuf()

	def on_apply(self, *args):
		if self.rotate_selection:
			self.get_image().selection_pixbuf = self.get_selection_pixbuf().rotate_simple(self.get_angle())
			self.window.former_tool().on_confirm_hijacked_modif()
		else:
			self.get_image().rotate_pixbuf(self.get_angle())
			self.window.back_to_former_tool()

	def get_angle(self):
		return self.angle_btn.get_value_as_int()

	def on_draw(self, area, cairo_context, main_x, main_y):
		if self.rotate_selection:
			self.window.use_stable_pixbuf()
			self.window.former_tool().delete_temp()
			self.non_destructive_show_pixbufs(True)
			super().on_draw(area, cairo_context, main_x, main_y)
		else:
			Gdk.cairo_set_source_pixbuf(cairo_context, self.window.temporary_pixbuf, 0, 0) # XXX c'est là pour le zoom non ? en négatif
			cairo_context.paint()

	def update_temp_pixbuf(self):
		angle = self.get_angle()
		if self.rotate_selection:
			self.get_image().set_temp_pixbuf(self.get_selection_pixbuf().rotate_simple(angle))
		else:
			self.get_image().set_temp_pixbuf(self.get_main_pixbuf().rotate_simple(angle))

	def on_angle_changed(self, *args):
		if self.get_angle() % 90 != 0:
			self.angle_btn.set_value(int(self.get_angle() / 90) * 90)
		self.update_temp_pixbuf()
		self.non_destructive_show_modif()