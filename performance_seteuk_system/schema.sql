-- ==========================================
-- 1. 테이블 정의 (Tables)
-- ==========================================

-- 교사 프로필 테이블 (auth.users와 1:1 관계)
create table if not exists public.teachers (
  id uuid references auth.users on delete cascade primary key,
  name text not null,
  role text not null check (role in ('admin', 'teacher')),
  created_at timestamptz default now()
);

-- 학생 정보 테이블
create table if not exists public.students (
  id uuid default gen_random_uuid() primary key,
  hakbun varchar(5) unique not null, -- 예: '30212'
  grade int2 not null,
  class int2 not null,
  number int2 not null,
  name text not null,
  created_at timestamptz default now()
);

-- 교과 과목 테이블
create table if not exists public.subjects (
  id uuid default gen_random_uuid() primary key,
  name text not null, -- 예: '화법과 작문', '문학'
  grade int2 not null,
  teacher_id uuid references public.teachers(id) on delete set null,
  created_at timestamptz default now()
);

-- 수행평가 항목 테이블
create table if not exists public.assessments (
  id uuid default gen_random_uuid() primary key,
  subject_id uuid references public.subjects(id) on delete cascade not null,
  name text not null, -- 예: '1차 포트폴리오 논술'
  max_score numeric not null default 100,
  due_date date,
  created_at timestamptz default now()
);

-- 학생별 수행평가 응시 기록 테이블
create table if not exists public.submissions (
  id uuid default gen_random_uuid() primary key,
  assessment_id uuid references public.assessments(id) on delete cascade not null,
  student_id uuid references public.students(id) on delete cascade not null,
  status text not null check (status in ('응시 완료', '미응시', '예외(위탁)', '예외(자퇴)', '예외(전출)')),
  score numeric,
  submitted_content text, -- 학생이 제출한 원본 텍스트/답안
  teacher_notes text, -- 교사 비고 (수기 입력 사항, 예외 사유 등)
  updated_by uuid references public.teachers(id),
  updated_at timestamptz default now(),
  unique (assessment_id, student_id)
);

-- 세특 작성 및 Gemini 초안 테이블
create table if not exists public.seteuk_drafts (
  id uuid default gen_random_uuid() primary key,
  student_id uuid references public.students(id) on delete cascade not null,
  subject_id uuid references public.subjects(id) on delete cascade not null,
  raw_content text, -- 세특 생성을 위한 기초 학생 답변/활동 자료
  gemini_draft text, -- 생성된 세특 초안 (NEIS 바이트 최적화)
  gemini_summary text, -- 타 교사용 진로 중심 2줄 요약
  final_content text, -- 담당교사가 최종 편집한 세특 내용
  status text not null check (status in ('waiting', 'generating', 'completed', 'failed')),
  updated_at timestamptz default now(),
  unique (student_id, subject_id)
);

-- ==========================================
-- 2. Row Level Security (RLS) 활성화
-- ==========================================
alter table public.teachers enable row level security;
alter table public.students enable row level security;
alter table public.subjects enable row level security;
alter table public.assessments enable row level security;
alter table public.submissions enable row level security;
alter table public.seteuk_drafts enable row level security;

-- ==========================================
-- 3. RLS 보안 정책 (Policies)
-- ==========================================

-- 3.1. 교사 테이블 (teachers)
create policy "인증된 사용자는 모든 교과 교사의 프로필 조회 가능"
  on public.teachers for select
  using (auth.role() = 'authenticated');

create policy "교사 본인은 자신의 프로필 수정 가능"
  on public.teachers for update
  using (auth.uid() = id);

-- 3.2. 학생 테이블 (students)
create policy "인증된 교사는 전체 학생 정보 조회 가능"
  on public.students for select
  using (auth.role() = 'authenticated');

create policy "관리자만 학생 정보 수정/추가/삭제 가능"
  on public.students for all
  using (
    exists (
      select 1 from public.teachers
      where id = auth.uid() and role = 'admin'
    )
  );

-- 3.3. 과목 테이블 (subjects)
create policy "인증된 교사는 전체 과목 조회 가능"
  on public.subjects for select
  using (auth.role() = 'authenticated');

create policy "관리자만 과목 추가/수정/삭제 가능"
  on public.subjects for all
  using (
    exists (
      select 1 from public.teachers
      where id = auth.uid() and role = 'admin'
    )
  );

-- 3.4. 수행평가 항목 테이블 (assessments)
create policy "인증된 교사는 수행평가 항목 조회 가능"
  on public.assessments for select
  using (auth.role() = 'authenticated');

create policy "담당 교사 또는 관리자만 수행평가 항목 변경 가능"
  on public.assessments for all
  using (
    exists (
      select 1 from public.subjects
      where id = assessments.subject_id and (teacher_id = auth.uid() or exists (
        select 1 from public.teachers where id = auth.uid() and role = 'admin'
      ))
    )
  );

-- 3.5. 수행평가 응시 기록 테이블 (submissions)
create policy "인증된 교사는 모든 응시 기록 조회 가능"
  on public.submissions for select
  using (auth.role() = 'authenticated');

create policy "담당 교사 또는 관리자만 응시 기록 수정/추가 가능"
  on public.submissions for all
  using (
    exists (
      select 1 from public.assessments a
      join public.subjects s on a.subject_id = s.id
      where a.id = submissions.assessment_id and (s.teacher_id = auth.uid() or exists (
        select 1 from public.teachers where id = auth.uid() and role = 'admin'
      ))
    )
  );

-- 3.6. 세특 테이블 (seteuk_drafts)
create policy "담당 교사만 본인 과목 세특 전체 권한 허용"
  on public.seteuk_drafts for all
  using (
    exists (
      select 1 from public.subjects
      where id = seteuk_drafts.subject_id and teacher_id = auth.uid()
    )
  );

-- ==========================================
-- 4. 보안 뷰 (Security Views)
-- ==========================================
-- 타 교사는 세특의 상세 원본이나 본문은 볼 수 없지만, 진로 중심 2줄 요약은 볼 수 있도록 제공하는 보안 뷰
create or replace view public.v_seteuk_summary as
  select 
    sd.id,
    sd.student_id,
    sd.subject_id,
    sd.gemini_summary, -- 요약만 노출
    sd.status,
    sd.updated_at
  from public.seteuk_drafts sd
  where auth.role() = 'authenticated';

-- ==========================================
-- 5. 관리자 전용 교사 계정 생성 함수 (Security Definer)
-- ==========================================
-- Supabase 클라이언트에서 관리자 교사가 신규 일반 교사 계정을 발급할 수 있게 하는 보안 도우미 함수
create or replace function public.admin_create_teacher(
  teacher_email text,
  teacher_password text,
  teacher_name text,
  teacher_role text
) returns uuid as $$
declare
  new_user_id uuid;
begin
  -- 호출자가 관리자(admin)인지 검증
  if not exists (
    select 1 from public.teachers
    where id = auth.uid() and role = 'admin'
  ) then
    raise exception '계정 생성 권한이 없습니다. 관리자만 수행 가능합니다.';
  end if;

  -- auth.users에 신규 계정 삽입 (Supabase 규격 준수)
  insert into auth.users (
    instance_id,
    id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    raw_app_meta_data,
    raw_user_meta_data,
    created_at,
    updated_at,
    confirmation_token,
    email_change,
    email_change_token_new,
    recovery_token
  ) values (
    '00000000-0000-0000-0000-000000000000',
    gen_random_uuid(),
    'authenticated',
    'authenticated',
    teacher_email,
    crypt(teacher_password, gen_salt('bf')),
    now(),
    '{"provider":"email","providers":["email"]}',
    jsonb_build_object('name', teacher_name, 'role', teacher_role),
    now(),
    now(),
    '',
    '',
    '',
    ''
  ) returning id into new_user_id;

  -- public.teachers 프로필 정보 삽입
  insert into public.teachers (id, name, role)
  values (new_user_id, teacher_name, teacher_role);

  return new_user_id;
end;
$$ language plpgsql security definer;

-- 관리자 전용 교사 비밀번호 초기화 함수
create or replace function public.admin_reset_teacher_password(
  target_user_id uuid,
  new_password text
) returns boolean as $$
begin
  -- 호출자가 관리자(admin)인지 검증
  if not exists (
    select 1 from public.teachers
    where id = auth.uid() and role = 'admin'
  ) then
    raise exception '비밀번호 초기화 권한이 없습니다. 관리자만 수행 가능합니다.';
  end if;

  -- auth.users의 비밀번호 강제 업데이트
  update auth.users
  set encrypted_password = crypt(new_password, gen_salt('bf')),
      updated_at = now()
  where id = target_user_id;

  return true;
end;
$$ language plpgsql security definer;
