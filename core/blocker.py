# --- Blocker & Interceptor ---
print("4 Running Blocker")
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


class Blocker(QWebEngineUrlRequestInterceptor):
    BLOCK_LIST = [
        # Original common ad networks
        "doubleclick.net", "googlesyndication.com", "adservice.google.com",
        "googletagmanager.com", "googletagservices.com", "taboola.com",
        "outbrain.com", "criteo.net", "adroll.com", "scorecardresearch.com",
        # New expanded list
        "adservetx.media.net", "events.hotjar.io", "data.mistat.rus.xiaomi.com",
        "metrics.mzstatic.com", "data.mistat.india.xiaomi.com", "api.ad.xiaomi.com",
        "google-analytics.com", "adm.hotjar.com", "freshmarketer.com",
        "claritybt.freshmarketer.com", "m.doubleclick.net", "identify.hotjar.com",
        "cs.luckyorange.net", "ads.yahoo.com", "cdn-test.mouseflow.com",
        "cdn.mouseflow.com", "upload.luckyorange.net", "metrics.icloud.com",
        "smetrics.samsung.com", "metrics2.data.hicloud.com", "logbak.hicloud.com",
        "log.fc.yahoo.com", "iot-eu-logser.realme.com", "grs.hicloud.com",
        "wd.adcolony.com", "script.hotjar.com", "api.mouseflow.com",
        "sdkconfig.ad.xiaomi.com", "fwtracks.freshmarketer.com",
        "analytics.query.yahoo.com", "geo.yahoo.com", "ads30.adcolony.com",
        "adc3-launch.adcolony.com", "events3alt.adcolony.com", "surveys.hotjar.com",
        "afs.googlesyndication.com", "realtime.luckyorange.com", "click.googleanalytics.com",
        "static.doubleclick.net", "analytics.google.com", "insights.hotjar.com",
        "static.media.net", "notify.bugsnag.com", "logservice1.hicloud.com",
        "auction.unityads.unity3d.com", "appmetrica.yandex.ru",
        "webview.unityads.unity3d.com", "cdn.luckyorange.com", "metrika.yandex.ru",
        "w1.luckyorange.com", "api.luckyorange.com", "bdapi-in-ads.realmemobile.com",
        "adserver.unityads.unity3d.com", "config.unityads.unity3d.com",
        "bdapi-ads.realmemobile.com", "log.pinterest.com",
        "weather-analytics-events.apple.com", "adx.ads.oppomobile.com",
        "ads.pinterest.com", "notes-analytics-events.apple.com",
        "books-analytics-events.apple.com", "logservice.hicloud.com",
        "api-adservices.apple.com", "ck.ads.oppomobile.com",
        "data.ads.oppomobile.com", "gtm.mouseflow.com",
        "analytics-api.samsunghealthcn.com", "metrics.data.hicloud.com",
        "samsung-com.112.2o7.net", "sdkconfig.ad.intl.xiaomi.com",
        "sessions.bugsnag.com", "nmetrics.samsung.com", "adfstat.yandex.ru",
        "adsfs.oppomobile.com", "partnerads.ysm.yahoo.com", "api.bugsnag.com",
        "browser.sentry-cdn.com", "advice-ads.s3.amazonaws.com",
        "adtago.s3.amazonaws.com", "adfox.yandex.ru", "analytics.yahoo.com",
        "analytics.s3.amazonaws.com", "o2.mouseflow.com", "luckyorange.com",
        "tools.mouseflow.com", "analytics.pointdrive.linkedin.com",
        "settings.luckyorange.net", "media.net", "data.mistat.xiaomi.com",
        "analyticsengine.s3.amazonaws.com", "trk.pinterest.com", "iadsdk.apple.com",
        "events.redditmedia.com", "open.oneplus.net", "tracking.rus.miui.com",
        "analytics.pinterest.com", "ssl.google-analytics.com",
        "mediavisor.doubleclick.net", "samsungads.com", "gemini.yahoo.com",
        "udcm.yahoo.com", "app.bugsnag.com", "app.getsentry.com",
        "adtech.yahooinc.com", "iot-logser.realme.com", "mouseflow.com",
        "ads.linkedin.com", "careers.hotjar.com"
    ]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if any(b in url for b in self.BLOCK_LIST):
            info.block(True)