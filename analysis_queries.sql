-- ============================================================
-- Restaurant Operations Analytics — SQL Analysis
-- Dataset: Food Delivery Dataset (Kaggle, gauravmalik26), cleaned
-- Table: orders (loaded via 01_clean_data.py -> ops_analytics.db)
-- SLA definition: on-time = Time_taken(min) <= 30
-- ============================================================

-- 1. Weekly order volume trend
SELECT
    Order_Week,
    COUNT(*) AS total_orders
FROM orders
GROUP BY Order_Week
ORDER BY Order_Week;


-- 2. Overall SLA compliance
SELECT
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct,
    COUNT(*) AS total_orders,
    ROUND(AVG("Time_taken(min)"), 1) AS avg_delivery_time_min
FROM orders;


-- 3. SLA compliance by city type
SELECT
    City,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct,
    ROUND(AVG("Time_taken(min)"), 1) AS avg_delivery_time_min
FROM orders
WHERE City IS NOT NULL AND City != 'nan'
GROUP BY City
ORDER BY sla_compliance_pct DESC;


-- 4. SLA compliance by road traffic density
SELECT
    Road_traffic_density,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct
FROM orders
WHERE Road_traffic_density IS NOT NULL AND Road_traffic_density != 'nan'
GROUP BY Road_traffic_density
ORDER BY sla_compliance_pct DESC;


-- 5. SLA compliance by weather condition
SELECT
    Weatherconditions,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct
FROM orders
GROUP BY Weatherconditions
ORDER BY sla_compliance_pct ASC;


-- 6. Festival-day impact on delivery performance
SELECT
    Festival,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct,
    ROUND(AVG("Time_taken(min)"), 1) AS avg_delivery_time_min
FROM orders
WHERE Festival IS NOT NULL AND Festival != 'nan'
GROUP BY Festival;


-- 7. Vehicle type performance
SELECT
    Type_of_vehicle,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct,
    ROUND(AVG("Time_taken(min)"), 1) AS avg_delivery_time_min
FROM orders
GROUP BY Type_of_vehicle
ORDER BY sla_compliance_pct DESC;


-- 8. Order volume by day of week (weekday vs weekend demand pattern)
SELECT
    Order_DayOfWeek,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct
FROM orders
GROUP BY Order_DayOfWeek
ORDER BY
    CASE Order_DayOfWeek
        WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7 END;


-- 9. Worst-performing segment: city x traffic combined (where to focus ops improvements)
SELECT
    City,
    Road_traffic_density,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct
FROM orders
WHERE City IS NOT NULL AND City != 'nan'
  AND Road_traffic_density IS NOT NULL AND Road_traffic_density != 'nan'
GROUP BY City, Road_traffic_density
HAVING COUNT(*) >= 100
ORDER BY sla_compliance_pct ASC
LIMIT 10;


-- 10. Impact of multiple concurrent deliveries on SLA (delivery-partner batching)
SELECT
    multiple_deliveries,
    COUNT(*) AS total_orders,
    ROUND(100.0 * SUM(SLA_Met) / COUNT(*), 2) AS sla_compliance_pct
FROM orders
WHERE multiple_deliveries IS NOT NULL AND multiple_deliveries != 'nan'
GROUP BY multiple_deliveries
ORDER BY multiple_deliveries;
