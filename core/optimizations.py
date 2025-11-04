# --- optimizations & visuals ---
print("2 Running Optimizations")
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

# os settings
try:
    os.environ["QT_LOGGING_RULES"] = "*=false"
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    os.environ["QTWEBENGINE_DISABLE_GPU_SANDBOX"] = "1"
    os.environ["QT_OPENGL"] = "desktop"
    os.environ["QSG_RENDER_LOOP"] = "threaded"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "0"  # disables unneeded port listener

    flags = [
        "--enable-gpu-rasterization",
        "--enable-zero-copy",
        "--ignore-gpu-blocklist",
        "--enable-native-gpu-memory-buffers",
        "--enable-accelerated-video-decode",
        "--enable-features=VaapiVideoDecoder,ThreadedCompositing,WebRTCPipeWireCapturer",
        "--use-gl=desktop",
        "--in-process-gpu",
        "--process-per-site-instance",
        "--disk-cache-size=104857600",
        "--enable-smooth-scrolling",
        "--enable-fast-unload",
        "--enable-tile-compression",
        "--enable-partial-raster",
        "--enable-parallel-downloading",
        "--disable-background-timer-throttling --disable-backgrounding-occluded-windows",
        "--enable-quic",
        "--disable-renderer-backgrounding",
        "--disable-background-networking",
        "--disable-ipc-flooding-protection",
        "--enable-tcp-fast-open",
        "--enable-webgl-image-chromium",
        "--enable-gpu-compositing",
        "--enable-oop-rasterization",
        "--enable-accelerated-2d-canvas",
        "--enable-native-gpu-memory-buffers",
        "--enable-vulkan",
        "--enable-webgl2-compute-context",
    ]
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)
except Exception:
    os.environ["QT_QUICK_BACKEND"] = "software"  # optional fallback for hybrid GPUs (helps stability)

# fmt settings
try:
    fmt = QSurfaceFormat()
    QSurfaceFormat.setDefaultFormat(fmt)
    fmt = QSurfaceFormat()
    fmt.setSamples(8)  # anti-aliasing
    fmt.setSwapInterval(1)  # vsync
    fmt.setDepthBufferSize(24)
except Exception:
    pass

# QCoreApplication settings
try:

    try:
        QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    except Exception:
        QApplication.setAttribute(Qt.AA_UseOpenGLES)
    
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QCoreApplication.setAttribute(Qt.WA_TranslucentBackground, True)
    # QApplication.setAttribute(Qt.AA_DontUseNativeMenuBar)
    # QApplication.setAttribute(Qt.AA_DontUseNativeDialogs)
except Exception:
    pass
