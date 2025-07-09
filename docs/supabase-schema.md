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

Stores water quality samples from devices.

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
  ph float8
);
```

- `id`: Unique identifier for each sample (autoincrementing)

- `device_id`: Foreign key referencing `devices.id`

- `created_at`: Time the sample was inserted in UTC (defaults to `now()`)

- `measured_at`: Actual time when the sample was measured in UTC

- `uptime`: Uptime of the device in seconds

- `turbidity`: Turbidity value in NTU

- `temperature`: Temperature value in degrees Celsius

- `total_dissolved_solids`: Total dissolved solids value in ppm

- `ph`: Unitless pH value 

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