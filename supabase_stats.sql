-- Run once in the Supabase SQL editor for the global games-played counter.

create table if not exists public.asteroids_stats (
  id text primary key,
  games_played bigint not null default 0
);

insert into public.asteroids_stats (id, games_played)
values ('global', 0)
on conflict (id) do nothing;

alter table public.asteroids_stats enable row level security;

create policy "asteroids_stats_select"
  on public.asteroids_stats for select
  using (true);

create policy "asteroids_stats_insert"
  on public.asteroids_stats for insert
  with check (true);

create policy "asteroids_stats_update"
  on public.asteroids_stats for update
  using (true);
