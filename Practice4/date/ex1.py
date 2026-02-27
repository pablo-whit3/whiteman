from datetime import datetime, timedelta
now=datetime.today()

new_d=now - timedelta(days=5)

print(new_d.date())