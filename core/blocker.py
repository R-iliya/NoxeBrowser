from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from urllib.parse import urlparse

class Blocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.blocked_domains = {
            "doubleclick.net",
            "googlesyndication.com",
            "adservice.google.com",
            "googletagmanager.com",
            "googletagservices.com",
            "google-analytics.com",
            "googleadservices.com",
            "taboola.com",
            "outbrain.com",
            "criteo.net",
            "scorecardresearch.com",
            "hotjar.com",
            "luckyorange.com",
            "mouseflow.com",
            "freshmarketer.com",
            "bugsnag.com",
            "sentry-cdn.com",
            "yandex.ru",
            "yandex.com",
            "connect.facebook.net",
            "facebook.com",
            "analytics.tiktok.com",
            "bat.bing.com",
            "clarity.ms",
            # Xiaomi/Samsung/Apple telemetry
            "mistat.xiaomi.com",
            "hicloud.com",
            "samsungads.com",
            "adcolony.com",
            "unityads.unity3d.com",
            # Add more as you spot them
        }

    def interceptRequest(self, info):
        url_str = info.requestUrl().toString().lower()
        parsed = urlparse(url_str)
        if not parsed.hostname:
            return

        domain = parsed.hostname.lower()
        parts = domain.split('.')

        blocked = False
        for i in range(len(parts) - 1):
            suffix = '.'.join(parts[i:])
            if suffix in self.blocked_domains:
                blocked = True
                break

        if blocked:
            # Your existing resource type filter
            if info.resourceType() in [
                QWebEngineUrlRequestInfo.ResourceTypeScript,
                QWebEngineUrlRequestInfo.ResourceTypeStylesheet,
                QWebEngineUrlRequestInfo.ResourceTypeImage,
                QWebEngineUrlRequestInfo.ResourceTypeFontResource,
                QWebEngineUrlRequestInfo.ResourceTypeSubResource,
            ]:
                if __debug__:
                    print(f"Blocked {info.resourceType().name}: {suffix} → {url_str[:120]}")
                info.block(True)
            return

        # Block data: URIs for scripts / objects
        if url_str.startswith("data:") and info.resourceType() in [
            QWebEngineUrlRequestInfo.ResourceTypeScript,
            QWebEngineUrlRequestInfo.ResourceTypeObject,
        ]:
            if __debug__:
                print(f"Blocked dangerous data: URI → {url_str[:80]}")
            info.block(True)
            return

        # Block known tracking pixels / beacons that slip through
        if "pixel" in url_str or "beacon" in url_str or "track" in url_str:
            if info.resourceType() == QWebEngineUrlRequestInfo.ResourceTypeImage:
                if __debug__:
                    print(f"Blocked tracking pixel/beacon → {url_str[:120]}")
                info.block(True)