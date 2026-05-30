#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة البداية الرئيسية للتطبيق
"""

import tkinter as tk

from welcome import MainWindow


if __name__ == "__main__":
    root = tk.Tk()
    main_window = MainWindow(root)
    root.mainloop()
