"""
Utility functions for the GUI.
"""

import tkinter as tk

def draw_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)