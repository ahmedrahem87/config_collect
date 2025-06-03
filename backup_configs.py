from netmiko import ConnectHandler
from datetime import datetime
import smtplib
import os
from email.mime.text import MIMEText
import yaml
# Devices and their associated commands
with open("inventory.yml") as f:
    data = yaml.safe_load(f)
    devices = data["devices"]

success = []
failures = []

now = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_dir = os.path.expanduser("~/router_backups")
os.makedirs(backup_dir, exist_ok=True)

for entry in devices:
    device = entry['device']
    cmd = entry['cmd']
    hostname = entry['hostname']
    try:
        conn = ConnectHandler(**device)
        config = conn.send_command(cmd)
        filename = f"{backup_dir}/{hostname}_config_{now}.txt"
        with open(filename, 'w') as f:
            f.write(config)
        conn.disconnect()
        success.append(hostname)
    except Exception as e:
        failures.append(f"{hostname}: {e}")

# Prepare the email content
subject = f"Router Backup Report - {now}"
body = f"✅ Success:\n" + "\n".join(success) + "\n\n❌ Failures:\n" + ("\n".join(failures) if failures else "None")

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = "prometheus.alerts1@gmail.com"
msg["To"] = "ahmadrahem1798@gmail.com"

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("prometheus.alerts1@gmail.com", "dasz ykay upja pixb")
        server.send_message(msg)
except Exception as mail_err:
    print("Email send failed:", mail_err)

