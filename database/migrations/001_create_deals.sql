-- Run once in Supabase SQL Editor. Never expose the service-role key.
create table if not exists public.deals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists deals_user_created_idx on public.deals(user_id, created_at desc);
alter table public.deals enable row level security;
create policy "owners can read their deals" on public.deals for select to authenticated using ((select auth.uid()) = user_id);
create policy "owners can create their deals" on public.deals for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "owners can update their deals" on public.deals for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "owners can delete their deals" on public.deals for delete to authenticated using ((select auth.uid()) = user_id);
