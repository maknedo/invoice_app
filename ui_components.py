#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مكونات الواجهة المخصصة
"""

import tkinter as tk

class AnimatedButton(tk.Canvas):
    """زر متحرك مع تأثيرات Hover"""
    
    def __init__(self, parent, text, command, bg_color='#4CAF50', hover_color='#45a049', 
                 text_color='white', width=200, height=50, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, 
                        bg=kwargs.get('bg', parent['bg'] if isinstance(parent, tk.Frame) else '#F1F8E9'))
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        
        # Draw button with rounded corners
        self.button_id = self.create_rounded_rect(5, 5, width-5, height-5, 
                                                   radius=12, fill=bg_color, outline='')
        self.text_id = self.create_text(width/2, height/2, 
                                        text=text, fill=text_color, 
                                        font=('Segoe UI', 11, 'bold'))
        
        # Bind events
        self.tag_bind(self.button_id, '<Enter>', self.on_enter)
        self.tag_bind(self.button_id, '<Leave>', self.on_leave)
        self.tag_bind(self.button_id, '<Button-1>', self.on_click)
        self.tag_bind(self.text_id, '<Enter>', self.on_enter)
        self.tag_bind(self.text_id, '<Leave>', self.on_leave)
        self.tag_bind(self.text_id, '<Button-1>', self.on_click)
        
        self.configure(cursor='hand2')
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        self.itemconfig(self.button_id, fill=self.hover_color)
        
    def on_leave(self, event):
        self.itemconfig(self.button_id, fill=self.bg_color)
        
    def on_click(self, event):
        self.after(100, self.command)
        
