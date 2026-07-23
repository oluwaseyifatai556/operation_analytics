import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

plt.rcParams['figure.dpi'] = 120
NAVY = '#1A3C5E'
ACCENT = '#E8833A'

df = pd.read_csv("train_cleaned.csv", parse_dates=['Order_Date'])


# ---------- 1. Order volume over time (weekly) ----------
weekly = df.groupby('Order_Week').size().reset_index(name='orders')
weekly = weekly.sort_values('Order_Week')

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(weekly['Order_Week'], weekly['orders'], marker='o', color=NAVY, linewidth=2)
ax.set_title('Weekly Order Volume', fontsize=13, fontweight='bold', color=NAVY)
ax.set_ylabel('Orders')
ax.set_xlabel('Week')
plt.xticks(rotation=45, ha='right', fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# ---------- 2. SLA compliance overall + by City ----------
sla_by_city = df.groupby('City')['SLA_Met'].mean().sort_values(ascending=False) * 100
fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(sla_by_city.index, sla_by_city.values, color=[NAVY, ACCENT, '#7A9CC6'])
ax.axhline(df['SLA_Met'].mean()*100, color='gray', linestyle='--', linewidth=1, label=f"Overall avg ({df['SLA_Met'].mean()*100:.1f}%)")
ax.set_title('SLA Compliance by City Type (\u226430 min)', fontsize=13, fontweight='bold', color=NAVY)
ax.set_ylabel('% Orders On-Time')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.legend()
for b in bars:
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f"{b.get_height():.1f}%", ha='center', fontsize=9)
plt.tight_layout()
plt.show()

# ---------- 3. SLA compliance by traffic density ----------
order = ['Low', 'Medium', 'High', 'Jam']
sla_traffic = df.groupby('Road_traffic_density')['SLA_Met'].mean().reindex(order) * 100
fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(sla_traffic.index, sla_traffic.values, color=NAVY)
ax.set_title('SLA Compliance by Road Traffic Density', fontsize=13, fontweight='bold', color=NAVY)
ax.set_ylabel('% Orders On-Time')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
for b in bars:
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f"{b.get_height():.1f}%", ha='center', fontsize=9)
plt.tight_layout()
plt.show()

# ---------- 4. Delivery time distribution ----------
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.hist(df['Time_taken(min)'], bins=30, color=NAVY, alpha=0.85)
ax.axvline(30, color=ACCENT, linestyle='--', linewidth=2, label='SLA threshold (30 min)')
ax.set_title('Delivery Time Distribution', fontsize=13, fontweight='bold', color=NAVY)
ax.set_xlabel('Minutes')
ax.set_ylabel('Number of Orders')
ax.legend()
plt.tight_layout()
plt.show()

# ---------- 5. SLA compliance by weather ----------
sla_weather = df.groupby('Weatherconditions')['SLA_Met'].mean().sort_values() * 100
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.barh(sla_weather.index, sla_weather.values, color=NAVY)
ax.set_title('SLA Compliance by Weather Condition', fontsize=13, fontweight='bold', color=NAVY)
ax.set_xlabel('% Orders On-Time')
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
for b in bars:
    ax.text(b.get_width()+0.5, b.get_y()+b.get_height()/2, f"{b.get_width():.1f}%", va='center', fontsize=9)
plt.tight_layout()
plt.show()

# ---------- 6. Order volume by day of week (weekday vs weekend pattern) ----------
dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
dow = df.groupby('Order_DayOfWeek').size().reindex(dow_order)
fig, ax = plt.subplots(figsize=(8, 4.5))
colors = ['#7A9CC6' if d in ('Saturday','Sunday') else NAVY for d in dow_order]
ax.bar(dow.index, dow.values, color=colors)
ax.set_title('Order Volume by Day of Week', fontsize=13, fontweight='bold', color=NAVY)
ax.set_ylabel('Total Orders')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.show()

# ---------- Print summary stats for write-up ----------
print("=== SUMMARY STATS ===")
print(f"Total orders analyzed: {len(df):,}")
print(f"Date range: {df['Order_Date'].min().date()} to {df['Order_Date'].max().date()}")
print(f"Overall SLA compliance (<=30min): {df['SLA_Met'].mean()*100:.2f}%")
print(f"Avg delivery time: {df['Time_taken(min)'].mean():.1f} min | Median: {df['Time_taken(min)'].median():.1f} min")
print()
print("-- SLA compliance by City --")
print(sla_by_city.round(1))
print()
print("-- SLA compliance by Traffic --")
print(sla_traffic.round(1))
print()
print("-- SLA compliance by Weather --")
print(sla_weather.round(1))
print()
print("-- Orders by day of week --")
print(dow)
print()
print("-- Vehicle type SLA --")
print((df.groupby('Type_of_vehicle')['SLA_Met'].mean()*100).round(1))
print()
print("-- Festival impact on SLA --")
print((df.groupby('Festival')['SLA_Met'].mean()*100).round(1))
print()
print("-- Multiple deliveries impact on SLA --")
print((df.groupby('multiple_deliveries')['SLA_Met'].mean()*100).round(1))

