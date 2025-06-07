import psutil
from prometheus_client import Gauge, start_http_server
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from haconiwa.core.config import Config
from haconiwa.core.logging import get_logger

class Monitor:
    def __init__(self):
        self.config = Config()
        self.logger = get_logger(__name__)
        self.cpu_usage_gauge = Gauge('cpu_usage', 'CPU Usage')
        self.memory_usage_gauge = Gauge('memory_usage', 'Memory Usage')
        start_http_server(8000)

    def collect_metrics(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        self.cpu_usage_gauge.set(cpu_usage)
        self.memory_usage_gauge.set(memory_info.percent)
        self.logger.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_info.percent}%")

    def generate_dashboard(self):
        cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
        plt.figure(figsize=(10, 5))
        plt.plot(cpu_usage, label='CPU Usage')
        plt.title('CPU Usage Over Time')
        plt.xlabel('Time')
        plt.ylabel('CPU Usage (%)')
        plt.legend()
        plt.savefig('cpu_usage_dashboard.png')
        plt.close()

    def send_alert(self, message):
        email_config = self.config.get_email_config()
        msg = MIMEMultipart()
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        msg['Subject'] = 'Alert: System Metrics'
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['from'], email_config['password'])
        server.send_message(msg)
        server.quit()

    def check_alert_conditions(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > self.config.get_alert_threshold('cpu'):
            self.send_alert(f"High CPU usage detected: {cpu_usage}%")

    def run(self):
        while True:
            self.collect_metrics()
            self.check_alert_conditions()
            self.generate_dashboard()

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()