"""
Data cleaning: Food Delivery Dataset (Kaggle - gauravmalik26/food-delivery-dataset)
Restructured as a restaurant-operations analytics project
(order volume, SLA compliance, delivery performance)
"""
import pandas as pd
import numpy as np

df = pd.read_csv('train.csv')

# 1. Strip whitespace from all string/object columns
str_cols = df.select_dtypes(include='object').columns.tolist()
for c in str_cols:
    df[c] = df[c].astype(str).str.strip()

# 2. Replace literal "NaN" strings with real NaN
df = df.replace({'NaN': np.nan, 'nan': np.nan})

# 3. Clean prefixed/text-in-numeric fields
df['Weatherconditions'] = df['Weatherconditions'].str.replace('conditions ', '', regex=False)
df['Time_taken(min)'] = df['Time_taken(min)'].str.replace('(min) ', '', regex=False).astype(float)

# 4. Numeric conversions
df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'], errors='coerce')
df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')
df['multiple_deliveries'] = pd.to_numeric(df['multiple_deliveries'], errors='coerce')

# 5. Date parsing: two formats present in this file, both day-first:
#    "dd-mm-yyyy" (dash) and "d/m/yyyy" (slash). Parsing them together
#    with a single pd.to_datetime call causes pandas to lock onto one
#    format and silently NaT the other, so they're parsed separately.
is_dash = df['Order_Date'].str.contains('-', na=False)
is_slash = df['Order_Date'].str.contains('/', na=False)
parsed_dash = pd.to_datetime(df.loc[is_dash, 'Order_Date'], format='%d-%m-%Y', errors='coerce')
parsed_slash = pd.to_datetime(df.loc[is_slash, 'Order_Date'], format='%d/%m/%Y', errors='coerce')
df['Order_Date'] = pd.NaT
df.loc[is_dash, 'Order_Date'] = parsed_dash
df.loc[is_slash, 'Order_Date'] = parsed_slash

# 6. Time parsing
df['Time_Orderd'] = pd.to_datetime(df['Time_Orderd'], format='%H:%M:%S', errors='coerce').dt.time
df['Time_Order_picked'] = pd.to_datetime(df['Time_Order_picked'], format='%H:%M:%S', errors='coerce').dt.time

# 7. Drop rows with no usable Time_taken (target metric) or Order_Date
df = df.dropna(subset=['Time_taken(min)', 'Order_Date'])

# 8. Sanity-clip: ratings should be 1-5, age should be realistic (18-65)
df.loc[(df['Delivery_person_Ratings'] < 1) | (df['Delivery_person_Ratings'] > 5), 'Delivery_person_Ratings'] = np.nan
df.loc[(df['Delivery_person_Age'] < 18) | (df['Delivery_person_Age'] > 65), 'Delivery_person_Age'] = np.nan

# 9. Derived fields
df['Order_Month'] = df['Order_Date'].dt.to_period('M').astype(str)
df['Order_Week'] = df['Order_Date'].dt.to_period('W').astype(str)
df['Order_DayOfWeek'] = df['Order_Date'].dt.day_name()
df['Is_Weekend'] = df['Order_Date'].dt.dayofweek >= 5

# SLA threshold: define "on-time" as delivery within 30 minutes
# (30 min is a standard food-delivery SLA benchmark; documented assumption)
SLA_THRESHOLD_MIN = 30
df['SLA_Met'] = df['Time_taken(min)'] <= SLA_THRESHOLD_MIN

print("Rows after cleaning:", len(df))
print("\nMissing values per column:")
print(df.isna().sum())
print("\nDate range:", df['Order_Date'].min(), "to", df['Order_Date'].max())
print("\nTime_taken(min) stats:")
print(df['Time_taken(min)'].describe())
print("\nOverall SLA compliance (<=30 min):", round(df['SLA_Met'].mean() * 100, 2), "%")

df.to_csv("train_cleaned.csv", index=False)
print("\nSaved cleaned dataset as train_cleaned")
