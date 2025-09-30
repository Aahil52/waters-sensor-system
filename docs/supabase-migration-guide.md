# Supabase Database Migration Guide

This document outlines the database schema changes needed to support diagnostic data collection for research quality assurance.

## 🔄 Required Database Changes

### Add Diagnostic Columns to `samples` Table

Execute the following SQL in your Supabase SQL editor to add the new diagnostic columns:

```sql
-- Add predicted dissolved oxygen column
ALTER TABLE samples
ADD COLUMN predicted_dissolved_oxygen float8;

-- Add turbidity diagnostic columns
ALTER TABLE samples
ADD COLUMN turbidity_voltage float8,
ADD COLUMN turbidity_rsd float8,
ADD COLUMN turbidity_success_rate float8,
ADD COLUMN turbidity_attempts integer;

-- Add total dissolved solids diagnostic columns
ALTER TABLE samples
ADD COLUMN total_dissolved_solids_voltage float8,
ADD COLUMN total_dissolved_solids_rsd float8,
ADD COLUMN total_dissolved_solids_success_rate float8,
ADD COLUMN total_dissolved_solids_attempts integer;

-- Add pH diagnostic columns
ALTER TABLE samples
ADD COLUMN ph_voltage float8,
ADD COLUMN ph_rsd float8,
ADD COLUMN ph_success_rate float8,
ADD COLUMN ph_attempts integer;
```

### Optional: Add Comments for Documentation

```sql
-- Add column comments for clarity
COMMENT ON COLUMN samples.predicted_dissolved_oxygen IS 'Machine learning predicted dissolved oxygen in mg/L';
COMMENT ON COLUMN samples.turbidity_voltage IS 'Raw turbidity sensor voltage reading in volts';
COMMENT ON COLUMN samples.turbidity_rsd IS 'Turbidity measurement relative standard deviation (0-1)';
COMMENT ON COLUMN samples.turbidity_success_rate IS 'Turbidity ADC reading success rate (0-1)';
COMMENT ON COLUMN samples.turbidity_attempts IS 'Number of turbidity measurement attempts';
COMMENT ON COLUMN samples.total_dissolved_solids_voltage IS 'Raw total dissolved solids sensor voltage reading in volts';
COMMENT ON COLUMN samples.total_dissolved_solids_rsd IS 'Total dissolved solids measurement relative standard deviation (0-1)';
COMMENT ON COLUMN samples.total_dissolved_solids_success_rate IS 'Total dissolved solids ADC reading success rate (0-1)';
COMMENT ON COLUMN samples.total_dissolved_solids_attempts IS 'Number of total dissolved solids measurement attempts';
COMMENT ON COLUMN samples.ph_voltage IS 'Raw pH sensor voltage reading in volts';
COMMENT ON COLUMN samples.ph_rsd IS 'pH measurement relative standard deviation (0-1)';
COMMENT ON COLUMN samples.ph_success_rate IS 'pH ADC reading success rate (0-1)';
COMMENT ON COLUMN samples.ph_attempts IS 'Number of pH measurement attempts';
```

## 📝 Edge Function Update

Update your `insert-sample` edge function with the new code provided in [`supabase-interface.md`](./supabase-interface.md).

## 🔍 Data Quality Queries for Research

### Filter High-Quality Measurements
```sql
SELECT * FROM samples
WHERE turbidity_rsd < 0.05
  AND total_dissolved_solids_rsd < 0.05
  AND ph_rsd < 0.05
  AND turbidity_success_rate > 0.8
  AND total_dissolved_solids_success_rate > 0.8
  AND ph_success_rate > 0.8;
```

### Sensor Performance Analysis
```sql
SELECT
  device_id,
  AVG(turbidity_rsd) as avg_turbidity_rsd,
  AVG(total_dissolved_solids_rsd) as avg_total_dissolved_solids_rsd,
  AVG(ph_rsd) as avg_ph_rsd,
  AVG(turbidity_attempts) as avg_turbidity_attempts,
  AVG(total_dissolved_solids_attempts) as avg_total_dissolved_solids_attempts,
  AVG(ph_attempts) as avg_ph_attempts
FROM samples
GROUP BY device_id;
```

### Identify Problematic Measurements
```sql
SELECT * FROM samples
WHERE turbidity_attempts > 2
   OR total_dissolved_solids_attempts > 2
   OR ph_attempts > 2
   OR turbidity_rsd > 0.1
   OR total_dissolved_solids_rsd > 0.1
   OR ph_rsd > 0.1;
```

## 🧪 Research Benefits

The diagnostic data enables:

- **Quality Control**: Filter measurements by RSD and success rate thresholds
- **Sensor Health Monitoring**: Track sensor performance over time
- **Uncertainty Quantification**: Include measurement uncertainty in analysis
- **Troubleshooting**: Identify environmental or hardware issues
- **Publication Quality**: Demonstrate measurement rigor and reliability
