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
        url = info.requestUrl().toString()
        parsed = urlparse(url)
        domain = parsed.hostname
        if not domain:
            return

        domain = domain.lower()
        parts = domain.split('.')

        for i in range(len(parts) - 1):
            suffix = '.'.join(parts[i:])
            if suffix in self.blocked_domains:
                # Optional: be more selective on what you block
                if info.resourceType() in [
                    QWebEngineUrlRequestInfo.ResourceTypeScript,
                    QWebEngineUrlRequestInfo.ResourceTypeStylesheet,
                    QWebEngineUrlRequestInfo.ResourceTypeImage,
                    QWebEngineUrlRequestInfo.ResourceTypeFontResource,
                    QWebEngineUrlRequestInfo.ResourceTypeSubResource,
                ]:
                    if __debug__:
                        print(f"Blocked {info.resourceType().name}: {suffix} in {domain} → {url[:120]}...")
                    info.block(True)
                return  # early exit even if not blocked — no need to check further