# --- local scheme & Paths ---
print("5 Running Scheme")
# importing required libraries
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
import winreg
import ctypes
import json
import sys
import os
from PyQt5.QtWebEngineCore import (
    QWebEngineUrlRequestInterceptor,
    QWebEngineUrlSchemeHandler,
    QWebEngineUrlScheme,
)

class LocalScheme(QWebEngineUrlSchemeHandler):
    def __init__(self):
        super().__init__()
        self.buffers = []

    def requestStarted(self, job):
        # Robust local:// file loader with .html fallback and correct mime mapx
        url = job.requestUrl().toString()
        path = url.replace("local://", "").lstrip("/")
        base_dir = os.path.dirname(__file__)
        file_path = os.path.normpath(os.path.join(base_dir, path))
        if not file_path.startswith(base_dir):
            buf = QBuffer()
            buf.setData(QByteArray(b"<html><body><h1>Access Denied</h1></body></html>"))
            buf.open(QIODevice.ReadOnly)
            job.reply(b"text/html", buf)
            return

        # fallback to .html if not found
        if not os.path.exists(file_path) and not file_path.endswith(".html"):
            file_path += ".html"

        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                data = f.read()
            ext = os.path.splitext(file_path)[1].lower()
            mime_map = {
                ".png": b"image/png", ".jpg": b"image/jpeg", ".jpeg": b"image/jpeg",
                ".gif": b"image/gif", ".bmp": b"image/bmp", ".webp": b"image/webp",
                ".css": b"text/css", ".js": b"application/javascript",
            }
            mime = mime_map.get(ext, b"text/html")
        else:
            data = b"<html><body><h1>404 Not Found</h1></body></html>"
            mime = b"text/html"

        buf = QBuffer()
        buf.setData(QByteArray(data))
        buf.open(QIODevice.ReadOnly)
        self.buffers.append(buf)  # keep alive while job uses it
        job.reply(mime, buf)
        try:
            job.finished.connect(partial(self._remove_buffer, buf))
        except Exception:
            pass

    def _remove_buffer(self, buf):
        if buf in self.buffers:
            self.buffers.remove(buf)

# --- register custom 'local' scheme BEFORE any QWebEngineProfile is created ---
scheme = QWebEngineUrlScheme(b"local")
scheme.setFlags(QWebEngineUrlScheme.LocalScheme | QWebEngineUrlScheme.LocalAccessAllowed)
scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
QWebEngineUrlScheme.registerScheme(scheme)