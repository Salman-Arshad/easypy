from django.urls import re_path
from . import consumers

# noinspection SpellCheckingInspection
websocket_urlpatterns = [
    re_path(r'ws/tradingview/$', consumers.TradingViewConsumer),
    re_path(r'ws/execution/$', consumers.PIDConsumer),
]
