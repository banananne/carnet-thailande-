-- Messages des invité·e·s aux voyageurs : script à coller UNE FOIS dans Supabase (SQL Editor). Ne contient aucun secret.
-- Chaque message est chiffré sur le téléphone de celui qui l'écrit (avec le code des invités) : Supabase ne voit que du texte illisible.
create table if not exists public.messages (
  id uuid primary key,
  c text not null check (length(c) < 6000),
  del_hash text not null check (del_hash ~ '^[0-9a-f]{64}$'),
  created_at timestamptz not null default now()
);
alter table public.messages enable row level security;
drop policy if exists "messages_lecture" on public.messages;
create policy "messages_lecture" on public.messages for select to anon using (true);
drop policy if exists "messages_ajout" on public.messages;
create policy "messages_ajout" on public.messages for insert to anon with check (true);
grant select, insert on public.messages to anon;

create or replace function public.retirer_message(p_id uuid, p_token text)
returns boolean language plpgsql security definer set search_path = public as $$
declare n integer;
begin
  delete from public.messages
   where id = p_id and del_hash = encode(sha256(convert_to(p_token, 'utf8')), 'hex');
  get diagnostics n = row_count;
  return n > 0;
end $$;
revoke all on function public.retirer_message(uuid, text) from public;
grant execute on function public.retirer_message(uuid, text) to anon;
