from ntplib import NTPClient
from datetime import datetime

client = NTPClient()
response = client.request('time.google.com')

t1 = response.orig_time
t2 = response.recv_time
t3 = response.tx_time
t4 = response.dest_time
delta = (t4 - t1) - (t3 - t2)
theta = t3 + delta / 2 - t4
current_clock = datetime.now()
adjusted_clock = datetime.fromtimestamp(datetime.timestamp(current_clock) + theta)

print(f't1={t1}')
print(f't2={t2}')
print(f't3={t3}')
print(f't1={t4}')
print(f'delta={delta}')
print(f'theta={theta}')
print(f'Current Clock: {current_clock}')
print(f'NTP Adjusted Clock: {adjusted_clock}')