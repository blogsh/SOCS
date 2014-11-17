from gi.repository import Gtk, Gdk, GLib, GObject
import cairo
import util
import numpy as np

class RenderArea(Gtk.DrawingArea):
	def __init__(self):
		Gtk.DrawingArea.__init__(self)
		self.connect("draw", self.draw)
		self.renderer = None
		self.context = None

	def draw(self, widget, ctx):
		if self.renderer is not None:
			self.renderer(ctx, self.get_allocation())

		return False

class MainWindow(Gtk.Window):
	def __init__(self, worldSettingsResolver, rendererSettingsResolver):
		Gtk.Window.__init__(self, title='SOCS Project')

		self.worldSettingsResolver = worldSettingsResolver
		self.rendererSettingsResolver = rendererSettingsResolver

		self.worldSettingsStore = Gtk.ListStore(str, str, str)
		self.rendererSettingsStore = Gtk.ListStore(str, str, str)

		self.setup_layout()

		self.update_settings()

		self.show_all()

	def update_settings(self):
		self.worldSettingsStore.clear()
		self.rendererSettingsStore.clear()

		for name in self.worldSettingsResolver.definitions:
			definition = self.worldSettingsResolver.definitions[name]
			value = self.worldSettingsResolver.settings[name]

			self.worldSettingsStore.append([
				definition.title,
				definition.transformToString(value),
				definition.name 
			])

		for name in self.rendererSettingsResolver.definitions:
			definition = self.rendererSettingsResolver.definitions[name]
			value = self.rendererSettingsResolver.settings[name]

			self.rendererSettingsStore.append([
				definition.title,
				definition.transformToString(value),
				definition.name 
			])

	def setup_layout(self):
		self.setup_treeview_panel()
		self.setup_canvas_panel()
		self.setup_control_panel()

		self.canvas.set_size_request(400, 400)

		rightBox = Gtk.VBox()
		rightBox.pack_start(self.controlPanel, False, True, 0)
		rightBox.pack_start(self.treeviewNotebook, True, True, 0)

		layoutBox = Gtk.Paned()
		layoutBox.pack1(self.canvas, True)
		layoutBox.pack2(rightBox, False)

		self.add(layoutBox)

	def setup_control_panel(self):
		self.startStopButton = Gtk.Button('Run')
		self.resetWorldButton = Gtk.Button('Reset World')
		self.resetSettingsButton = Gtk.Button('Reset Settings')

		self.controlPanel = Gtk.VBox()
		self.controlPanel.pack_start(self.startStopButton, True, True, 0)
		self.controlPanel.pack_start(self.resetWorldButton, True, True, 0)
		self.controlPanel.pack_start(self.resetSettingsButton, True, True, 0)

	def setup_canvas_panel(self):
		self.canvas = RenderArea()

	def setup_treeview_panel(self):
		self.setup_treeviews()

		worldLabel = Gtk.Label("World")
		rendererLabel = Gtk.Label("Renderer")

		self.treeviewNotebook = Gtk.Notebook()
		self.treeviewNotebook.append_page(self.worldSettingsTree, worldLabel)
		self.treeviewNotebook.append_page(self.rendererSettingsTree, rendererLabel)

	def create_treeview_renderer(self, purpose):
		renderer = Gtk.CellRendererText(editable = True)
		renderer.connect("edited", self.on_treeview_edit, purpose)
		return renderer

	def setup_treeviews(self):
		self.worldSettingsTree = Gtk.TreeView(self.worldSettingsStore)
		self.rendererSettingsTree = Gtk.TreeView(self.rendererSettingsStore)

		column = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text = 0,)
		self.worldSettingsTree.append_column(column = column)

		column = Gtk.TreeViewColumn("Value", self.create_treeview_renderer("world"), text = 1)
		self.worldSettingsTree.append_column(column = column)

		column = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text = 0)
		self.rendererSettingsTree.append_column(column = column)

		column = Gtk.TreeViewColumn("Value", self.create_treeview_renderer("renderer"), text = 1)
		self.rendererSettingsTree.append_column(column = column)

	def on_treeview_edit(self, widget, path, value, purpose):
		if purpose == "world":
			resolver = self.worldSettingsResolver
			item = self.worldSettingsStore[path]
		else:
			resolver = self.rendererSettingsResolver
			item = self.rendererSettingsStore[path]

		name = item[2]
		resolver.resolve({name : value})

		definition = resolver.definitions[name]
		item[1] = definition.transformToString(resolver.settings[name])

class CairoRenderer:
	def __init__(self, worldRenderer):
		self.size = (100, 100)
		self.worldRenderer = worldRenderer
		self.sx = 1.0
		self.sy = 1.0
		self.ctx = None

	def agent(self, position, color):
		self.ctx.set_source_rgb(color[0], color[1], color[2])
		self.ctx.arc(
			position[0] * self.sx, 
			position[1] * self.sy,
			self.sx, 0, 2 * np.pi
		)
		self.ctx.fill()

	def field(self, field, color):
		for x in range(self.size[0]):
			for y in range(self.size[1]):
				self.ctx.set_source_rgba(
					color[0],
					color[1],
					color[2],
					1.0 - field[x, y]
				)
				self.ctx.rectangle(
					x * self.sx, y * self.sy,
					self.sx, self.sy
				)
				self.ctx.fill()

	def set_size(self, size):
		self.size = size

	def render(self, ctx, rect):
		self.sx = rect.width / self.size[0]
		self.sy = rect.height / self.size[1]
		self.ctx = ctx

		self.ctx.rectangle(0, 0, rect.width, rect.height)
		self.ctx.set_source_rgb(1.0, 1.0, 1.0)
		self.ctx.fill()

		self.worldRenderer.render(self)

class Environment:
	def __init__(self, World, WorldRenderer, settings = dict()):
		self.worldSettingsResolver = util.SettingsResolver(World.SETTINGS)
		self.rendererSettingsResolver = util.SettingsResolver(WorldRenderer.SETTINGS)

		self.defaultSettings = settings

		self.worldSettingsResolver.resolve(settings)
		self.rendererSettingsResolver.resolve(settings)

		self.mainWindow = MainWindow(
			self.worldSettingsResolver,
			self.rendererSettingsResolver
		)
		self.mainWindow.connect("delete-event", self.stop)

		self.World = World
		self.worldInstance = World(self.worldSettingsResolver.settings)
		self.worldRendererInstance = WorldRenderer(self.worldInstance, self.rendererSettingsResolver.settings)

		self.cairoRenderer = CairoRenderer(self.worldRendererInstance)
		self.mainWindow.canvas.renderer = self.cairoRenderer.render

		self.workerInstance = None
		self.started = False
		self.running = False

		self.mainWindow.startStopButton.connect("clicked", self.on_start_stop)
		self.mainWindow.resetWorldButton.connect("clicked", self.on_reset_world)
		self.mainWindow.resetSettingsButton.connect("clicked", self.on_reset_settings)

	def worker(self):
		self.mainWindow.canvas.queue_draw()
		self.worldInstance.step()
		return self.running

	def start_worker(self):
		if not self.running:
			self.workerInstance = GObject.timeout_add(1, self.worker)
			self.running = True

	def stop_worker(self):
		if self.running:
			self.running = False
			GObject.source_remove(self.workerInstance)
			self.workerInstance = None

	def on_start_stop(self, widget):
		if not self.started:
			self.start_worker()
			self.started = True
			widget.set_label('Pause')
		else:
			self.stop_worker()
			self.started = False
			widget.set_label('Run')

	def on_reset_world(self, widget):
		self.worldRendererInstance = WorldRenderer(self.worldInstance, self.rendererSettingsResolver.settings)
		self.worldInstance = self.World(self.worldSettingsResolver.settings)

	def on_reset_settings(self, widget):
		self.worldSettingsResolver.resolve(self.defaultSettings, True)
		self.rendererSettingsResolver.resolve(self.defaultSettings, True)
		#self.mainWindow.update_settings()

	def stop(self, widget = None, data = None):
		Gtk.main_quit()

	def run(self):
		Gtk.main()
