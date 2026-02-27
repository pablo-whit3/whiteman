from datetime import datetime, timedelta
now=datetime.now()
d=input()
dt=datetime.strptime(d,"%Y-%m-%d %H:%M:%S.%f")
print(now.strftime("%Y-%m-%d %H:%M:%S"))
print(dt.strftime("%Y-%m-%d %H:%M:%S"))