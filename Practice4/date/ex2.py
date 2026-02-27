from datetime import datetime, timedelta
now=datetime.today()

tom=now + timedelta(days=1)
yest=now - timedelta(days=1)
print(yest.date())
print(now.date())
print(tom.date())