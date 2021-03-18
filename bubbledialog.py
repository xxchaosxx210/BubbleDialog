import wx
import time
import random
from collections import namedtuple

from geometry.vector import Vector

_MAX_VELOCITY = 40

_MIN_BUBBLE_SIZE = 2
_MAX_BUBBLE_SIZE = 10

_MIN_BUBBLE_AMOUNT = 100
_MAX_BUBBLE_AMOUNT = 200

_DCColour = namedtuple("Colour", ["pen", "brush"])


def get_display_rate():
    video_mode = wx.Display().GetCurrentMode()
    return 1 / video_mode.refresh


def _random_velocity(_max=_MAX_VELOCITY):
    return random.randint(2, _max)


def generate_random_bubble(rect: wx.Rect):
    start_x = random.randint(0, int(round(rect.width)))
    start_y = random.randint(rect.height, rect.height + 100)
    radius = random.randint(3, 17)
    return Bubble(start_x, start_y, radius)


class BubbleDialog(wx.Dialog):

    def __init__(self, parent, _id, title, message, size=wx.DefaultSize, pos=wx.DefaultPosition):
        super().__init__()
        self.Create(parent=parent, id=_id, title=title, size=size, pos=pos, style=wx.DEFAULT_DIALOG_STYLE)

        self.canvas = Canvas(self, -1, message)

        gs = wx.GridSizer(cols=1, rows=1, hgap=0, vgap=0)
        gs.Add(self.canvas, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(gs)

        self.Bind(wx.EVT_INIT_DIALOG, self.canvas.start_frame_loop, self)
        self.Bind(wx.EVT_CLOSE, self._on_close, self)
        self.SetSize(size)

        self.default_size = wx.Rect(0, 0, *size)

    def _on_close(self, evt):
        self.canvas.timer.Stop()
        evt.Skip()


class Bubble:

    def __init__(self, x, y, radius):
        self.diameter = radius * 2
        self.radius = radius
        self.position = Vector(x, y)
        self.velocity = Vector(x, y)
        self.velocity.y = _random_velocity()
        self.off_screen = False
        self.brush = wx.Brush(wx.Colour(255, 255, 255))
        self.pen = wx.Pen(wx.Colour(0, 0, 0), 2)

    def update(self, dt: float):
        self.position.y = self.position.y - self.velocity.y * dt
        self.check_bounds()

    def check_bounds(self):
        if self.position.y <= 0:
            self.off_screen = True


class Canvas(wx.Panel):

    def __init__(self, parent, _id, text):
        super().__init__(parent, _id)
        self.SetDoubleBuffered(True)
        self._bitmap = wx.Bitmap()
        self.dc_bck = _DCColour(wx.Pen(wx.Colour(255, 255, 255)),
                                wx.Brush(wx.Colour(255, 255, 255)))
        self.text = text
        self.timer = wx.Timer(self)
        self.bubbles = []
        self.Bind(wx.EVT_TIMER, self.loop)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def _on_size(self, evt):
        self._bitmap = wx.Bitmap()
        self._bitmap.Create(evt.GetSize())

    def start_frame_loop(self, evt):
        rect = self.GetParent().default_size
        for i in range(random.randint(_MIN_BUBBLE_AMOUNT, _MAX_BUBBLE_AMOUNT)):
            start_x = random.randint(0, int(round(rect.width)))
            start_y = random.randint(int(round(rect.height / 2)), rect.height + 100)
            radius = random.randint(_MIN_BUBBLE_SIZE, _MAX_BUBBLE_SIZE)
            self.bubbles.append(Bubble(start_x, start_y, radius))
        frame_rate = get_display_rate()
        self.timer.Start(frame_rate)

    def loop(self, evt):
        dt = time.monotonic() / 1000000
        for bubble in self.bubbles:
            bubble.update(dt)
        for bubble in reversed(self.bubbles):
            if bubble.off_screen:
                self.bubbles.remove(bubble)
                self.bubbles.append(generate_random_bubble(self.GetRect()))
        self.Refresh()

    def _on_paint(self, evt):
        dc = wx.BufferedPaintDC(self, self._bitmap)
        dc.Clear()
        dc.SetPen(self.dc_bck.pen)
        dc.SetBrush(self.dc_bck.brush)
        dc.DrawRectangle(0, 0, *self.GetSize())
        for bubble in self.bubbles:
            dc.SetPen(bubble.pen)
            dc.SetBrush(bubble.brush)
            dc.DrawCircle(bubble.position.x, bubble.position.y, bubble.radius)

