# haconiwa/watch/__init__.py

class Watch:
    def __init__(self):
        self.metrics = {}
        self.alerts = []

    def add_metric(self, name, value):
        self.metrics[name] = value

    def trigger_alert(self, message):
        self.alerts.append(message)

    def get_metrics(self):
        return self.metrics

    def get_alerts(self):
        return self.alerts

# モジュールの初期化処理
watch = Watch();