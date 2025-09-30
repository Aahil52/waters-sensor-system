# Supabase Schema

This document outlines the schema, access policies, and recommended practices for interfacing with the Supabase backend for the sensor system project. It includes database design, RLS policies, and usage of Edge Functions for secure inserts.

## 📦 Database Schema

### `devices` Table

Stores registered sensing devices.

```sql
create table devices (
  id bigint generated always as identity primary key,
  name text not null,
  location text
);
```

- `id`: Unique identifier for each device (autoincrementing)

- `name`: Human-readable name for the device (required)

- `location`: Optional location description

### `samples` Table

Stores water quality samples from devices with diagnostic data for research quality assurance.

```sql
create table samples (
  id bigint generated always as identity primary key,
  device_id bigint not null references devices (id),
  created_at timestamp not null default now(),
  measured_at timestamp not null,
  uptime float8 not null,
  turbidity float8,
  temperature float8,
  total_dissolved_solids float8,
  ph float8,
  predicted_dissolved_oxygen float8,
  -- Turbidity sensor diagnostics
  turbidity_voltage float8,
  turbidity_rsd float8,
  turbidity_success_rate float8,
  turbidity_attempts integer,
  -- Total dissolved solids sensor diagnostics
  total_dissolved_solids_voltage float8,
  total_dissolved_solids_rsd float8,
  total_dissolved_solids_success_rate float8,
  total_dissolved_solids_attempts integer,
  -- pH sensor diagnostics
  ph_voltage float8,
  ph_rsd float8,
  ph_success_rate float8,
  ph_attempts integer
);
```

#### Core Measurement Columns

- `id`: Unique identifier for each sample (autoincrementing)
- `device_id`: Foreign key referencing `devices.id`
- `created_at`: Time the sample was inserted in UTC (defaults to `now()`)
- `measured_at`: Actual time when the sample was measured in UTC
- `uptime`: Uptime of the device in seconds
- `turbidity`: Turbidity value in NTU
- `temperature`: Temperature value in degrees Celsius
- `total_dissolved_solids`: Total dissolved solids value in ppm
- `ph`: Unitless pH value
- `predicted_dissolved_oxygen`: Machine learning predicted dissolved oxygen in mg/L

#### Diagnostic Columns for Research Quality Assurance

Each ADC-based sensor (turbidity, total_dissolved_solids, pH) includes diagnostic data:

- `{sensor}_voltage`: Raw sensor voltage reading in volts
- `{sensor}_rsd`: Relative standard deviation of measurements (0-1 scale)
- `{sensor}_success_rate`: Proportion of successful ADC readings (0-1 scale)
- `{sensor}_attempts`: Number of measurement attempts before success/failure

#### Constraints and Indexes

```sql
alter table samples
add constraint unique_sample unique (device_id, measured_at);

create index idx_samples_device_id on samples (device_id);
```

- Ensures uniqueness per `device_id` and `measured_at`

- Index accelerates queries filtering by device

## 🔐 Row-Level Security (RLS)

Both tables have RLS enabled.

```sql
alter table devices enable row level security;
alter table samples enable row level security;
```

### Read Policies

```sql
create policy "Allow all users to read devices"
on devices
for select
using (true);

create policy "Allow all users to read samples"
on samples
for select
using (true);
```

- All users are allowed to read from both tables

- Insert/update/delete policies are not enabled. Intended to be handled via Edge Functions
