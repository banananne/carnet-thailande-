-- Reportage photo : script à coller UNE FOIS dans Supabase (SQL Editor). Ne contient aucun secret.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('reportage', 'reportage', true, 2097152, array['application/octet-stream'])
on conflict (id) do nothing;

drop policy if exists "reportage_ajout" on storage.objects;
create policy "reportage_ajout" on storage.objects
  for insert to anon with check (bucket_id = 'reportage');

create table if not exists public.reportage (
  id uuid primary key default gen_random_uuid(),
  f text not null unique check (f ~ '^p[0-9a-f]{12}$'),
  meta text not null check (length(meta) < 4000),
  del_hash text not null check (del_hash ~ '^[0-9a-f]{64}$'),
  created_at timestamptz not null default now()
);
alter table public.reportage enable row level security;
drop policy if exists "reportage_lecture" on public.reportage;
create policy "reportage_lecture" on public.reportage for select to anon using (true);
drop policy if exists "reportage_ajout" on public.reportage;
create policy "reportage_ajout" on public.reportage for insert to anon with check (true);
grant select, insert on public.reportage to anon;

create or replace function public.retirer_photo(p_id uuid, p_token text)
returns boolean language plpgsql security definer set search_path = public as $$
declare n integer;
begin
  delete from public.reportage
   where id = p_id and del_hash = encode(sha256(convert_to(p_token, 'utf8')), 'hex');
  get diagnostics n = row_count;
  return n > 0;
end $$;
revoke all on function public.retirer_photo(uuid, text) from public;
grant execute on function public.retirer_photo(uuid, text) to anon;
