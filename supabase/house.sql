-- Supabase backend for the house app (shared data per house, gated by a house key)
-- Run once in the SQL editor. Tables live in schema "house" (not exposed by the API);
-- the app only calls the public.house_* RPC functions below.

create schema if not exists house;
revoke all on schema house from public, anon, authenticated;

create table if not exists house.houses (
  id uuid primary key default gen_random_uuid(),
  house_no text not null,
  key_hash text not null unique,          -- sha256(house key), the key itself is never stored
  info jsonb,
  loan jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists house.expenses (
  id uuid primary key,
  house_id uuid not null references house.houses(id) on delete cascade,
  date date not null,
  cat text not null,
  amount numeric not null default 0,
  units numeric,
  part text not null default '',
  note text not null default '',
  updated_at timestamptz not null default now()
);
create index if not exists expenses_house_date on house.expenses(house_id, date);
alter table house.houses enable row level security;
alter table house.expenses enable row level security;

create or replace function house._hid(p_key text) returns uuid
language plpgsql security definer set search_path = '' as $$
declare v uuid;
begin
  select id into v from house.houses where key_hash = encode(extensions.digest(coalesce(p_key,''), 'sha256'), 'hex');
  if v is null then raise exception 'invalid house key'; end if;
  return v;
end $$;

create or replace function public.house_get(p_key text) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare h uuid := house._hid(p_key); r jsonb;
begin
  select jsonb_build_object(
    'house_no', hs.house_no,
    'profile', case when hs.info is null and hs.loan is null then null else jsonb_build_object('info', coalesce(hs.info,'{}'::jsonb), 'loan', coalesce(hs.loan,'{}'::jsonb)) end,
    'expenses', coalesce((select jsonb_agg(jsonb_build_object('id',e.id,'date',e.date,'cat',e.cat,'amount',e.amount,'units',e.units,'part',e.part,'note',e.note) order by e.date desc) from house.expenses e where e.house_id = h), '[]'::jsonb))
  into r from house.houses hs where hs.id = h;
  return r;
end $$;

create or replace function public.house_upsert_expense(p_key text, p_rec jsonb) returns uuid
language plpgsql security definer set search_path = '' as $$
declare h uuid := house._hid(p_key); v uuid := (p_rec->>'id')::uuid;
begin
  insert into house.expenses(id, house_id, date, cat, amount, units, part, note)
  values (v, h, (p_rec->>'date')::date, coalesce(p_rec->>'cat','other'), coalesce((p_rec->>'amount')::numeric,0), nullif(p_rec->>'units','')::numeric, coalesce(p_rec->>'part',''), coalesce(p_rec->>'note',''))
  on conflict (id) do update set date = excluded.date, cat = excluded.cat, amount = excluded.amount, units = excluded.units, part = excluded.part, note = excluded.note, updated_at = now()
  where house.expenses.house_id = h;
  return v;
end $$;

create or replace function public.house_delete_expense(p_key text, p_id uuid) returns void
language plpgsql security definer set search_path = '' as $$
declare h uuid := house._hid(p_key);
begin
  delete from house.expenses where id = p_id and house_id = h;
end $$;

create or replace function public.house_import(p_key text, p_rows jsonb) returns integer
language plpgsql security definer set search_path = '' as $$
declare h uuid := house._hid(p_key); n integer;
begin
  insert into house.expenses(id, house_id, date, cat, amount, units, part, note)
  select case when x->>'id' ~* '^[0-9a-f-]{36}$' then (x->>'id')::uuid else gen_random_uuid() end, h,
         (x->>'date')::date, coalesce(x->>'cat','other'), coalesce((x->>'amount')::numeric,0), nullif(x->>'units','')::numeric, coalesce(x->>'part',''), coalesce(x->>'note','')
  from jsonb_array_elements(coalesce(p_rows,'[]'::jsonb)) x
  where x->>'date' is not null
  on conflict (id) do nothing;
  get diagnostics n = row_count;
  return n;
end $$;

create or replace function public.house_save_profile(p_key text, p_info jsonb, p_loan jsonb) returns void
language plpgsql security definer set search_path = '' as $$
declare h uuid := house._hid(p_key);
begin
  update house.houses set info = p_info, loan = p_loan, updated_at = now() where id = h;
end $$;

revoke all on function house._hid(text) from public, anon, authenticated;
revoke all on function public.house_get(text), public.house_upsert_expense(text, jsonb), public.house_delete_expense(text, uuid), public.house_import(text, jsonb), public.house_save_profile(text, jsonb, jsonb) from public;
grant execute on function public.house_get(text), public.house_upsert_expense(text, jsonb), public.house_delete_expense(text, uuid), public.house_import(text, jsonb), public.house_save_profile(text, jsonb, jsonb) to anon, authenticated;

-- Add a house (replace the key; keep it secret):
-- insert into house.houses(house_no, key_hash, info, loan)
-- values ('92/xxx', encode(extensions.digest('YOUR-HOUSE-KEY', 'sha256'), 'hex'), '{"no":"92/xxx"}', '{}');
