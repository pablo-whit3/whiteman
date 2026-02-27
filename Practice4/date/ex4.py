from datetime import datetime
d1=input()
d2=input()
dt1=datetime.strptime(d1,"%Y-%m-%d %H:%M:%S")
dt2=datetime.strptime(d2,"%Y-%m-%d %H:%M:%S")
diff=dt1-dt2
print(int(diff.total_seconds()))