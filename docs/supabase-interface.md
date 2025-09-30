# Supabase Interface Guide

This document outlines how the sensor system interfaces with Supabase for device registration, data ingestion, and dashboard access.

## ⚙️ Interface Workflow

1. Device is registered in the `devices` table

2. Device sends sample via request to `insert-sample` edge function

3. Edge function inserts sample into samples table, ignoring duplicates

4. Client-side dashboard reads `devices` and `samples` with SELECT-only access

## 🔗 Interfacing with Supabase

Supabase provides a URL and an anon key that can be used in client-side applications with the appropriate RLS policies enabled. These can be used to interface with the database (read-only) and edge functions via the REST API or the Supabase Client libraries.

### Environment Variables

```env
SUPABASE_URL = "https://acghrhniyfrkusndclfq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjZ2hyaG5peWZya3VzbmRjbGZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1NzEyODEsImV4cCI6MjA2NzE0NzI4MX0.2lg2O1sy07xZ07HfNcPJ9vRJ4PS26Mh0g5shs-dmvvI"
```

⚠️ Do not commit your `.env` file. Commit an example file instead (e.g [`.env.example`](../.env.example)).

### Using the Python Client

```python
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

samples = supabase.table("samples")
    .select("*")
    .eq("device_id", 1)
    .order("measured_at", desc=True)
    .execute()
    .data
```

## 📤 Querying the Data

### Get All Devices

```sql
select *
from devices;
```

### Get All Samples for a Device

```sql
select *
from samples
where device_id = 1
order by measured_at desc;
```

### Get Recent Samples for a Device (e.g. Last 24h)

```sql
select *
from samples
where device_id = 1
    and measured_at >= now() - interval '1 day'
order by measured_at desc;
```

## 🚦 Inserting Data via Edge Function

Write access (e.g., sensor sample inserts) should be routed through a Supabase Edge Function, not done directly on the device. This is to prevent unauthorized database modifications via exposed credentials on the client.

### `insert-sample` Edge Function

This edge function is hosted in Supabase and uses the Service Role Key to bypass the read-only RLS policy. It uses UPSERT to ignore duplicate samples. A sample can be sent using the `/functions/v1/insert-sample` endpoint as implemented in the `send_sample()` function in [`sampler.py`](../sampler.py).

The function accepts sensor measurements along with diagnostic data for research quality assurance, including predicted dissolved oxygen from machine learning models.

```ts
import { createClient } from 'npm:@supabase/supabase-js@2';
const supabase = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'));
Deno.serve(async (req)=>{
  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', {
      status: 405
    });
  }
  try {
    // Extract JSON payload with diagnostic data
    const { 
      device_id, 
      measured_at, 
      uptime, 
      turbidity, 
      temperature, 
      total_dissolved_solids, 
      ph,
      predicted_dissolved_oxygen,
      // Turbidity diagnostics
      turbidity_voltage,
      turbidity_rsd,
      turbidity_success_rate,
      turbidity_attempts,
      // Total dissolved solids diagnostics
      total_dissolved_solids_voltage,
      total_dissolved_solids_rsd,
      total_dissolved_solids_success_rate,
      total_dissolved_solids_attempts,
      // pH diagnostics
      ph_voltage,
      ph_rsd,
      ph_success_rate,
      ph_attempts
    } = await req.json();
    
    if (!device_id || !measured_at || !uptime) {
      return new Response(JSON.stringify({
        error: 'Missing required fields'
      }), {
        status: 400
      });
    }
    
    // Insert new sample with diagnostic data, ignoring duplicates
    const { error: insertError } = await supabase.from('samples').upsert({
      device_id,
      measured_at,
      uptime,
      turbidity,
      temperature,
      total_dissolved_solids,
      ph,
      predicted_dissolved_oxygen,
      turbidity_voltage,
      turbidity_rsd,
      turbidity_success_rate,
      turbidity_attempts,
      total_dissolved_solids_voltage,
      total_dissolved_solids_rsd,
      total_dissolved_solids_success_rate,
      total_dissolved_solids_attempts,
      ph_voltage,
      ph_rsd,
      ph_success_rate,
      ph_attempts
    }, {
      onConflict: 'device_id,measured_at',
      ignoreDuplicates: true
    });
    
    if (insertError) {
      return new Response(JSON.stringify({
        error: insertError.message
      }), {
        status: 400
      });
    }
    
    return new Response(JSON.stringify({
      success: true
    }), {
      status: 200
    });
  } catch (err) {
    return new Response(JSON.stringify({
      error: 'Invalid request'
    }), {
      status: 400
    });
  }
});
```