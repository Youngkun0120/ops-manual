-- 월 정산 워크벤치 서버 저장 (2026-09-30)
-- Supabase 프로젝트 moizzusdaeerswjbnini › SQL Editor 에 붙여넣고 한 번 실행한다.
-- 사용자 결정: 접근 제한 없음 — 사이트 링크를 아는 사람은 누구나 읽고 쓸 수 있다.

-- 1) 입력값·설정 문서 (stl.settings.v1, stl.m.<YYYY-MM>)
create table if not exists public.stl_docs (
  key        text primary key,
  data       jsonb       not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  updated_by text
);

create or replace function public.stl_touch() returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists stl_docs_touch on public.stl_docs;
create trigger stl_docs_touch before update on public.stl_docs
  for each row execute function public.stl_touch();

alter table public.stl_docs enable row level security;

drop policy if exists stl_docs_read  on public.stl_docs;
drop policy if exists stl_docs_write on public.stl_docs;
create policy stl_docs_read  on public.stl_docs for select to anon using (true);
create policy stl_docs_write on public.stl_docs for all    to anon using (true) with check (true);

-- 2) 기존 양식 엑셀 · CTN 증빙 파일
insert into storage.buckets (id, name, public)
values ('stl-files', 'stl-files', true)
on conflict (id) do nothing;

drop policy if exists stl_files_read  on storage.objects;
drop policy if exists stl_files_write on storage.objects;
create policy stl_files_read  on storage.objects for select to anon
  using (bucket_id = 'stl-files');
create policy stl_files_write on storage.objects for all to anon
  using (bucket_id = 'stl-files') with check (bucket_id = 'stl-files');
