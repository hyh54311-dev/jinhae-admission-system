// app.js - 통합 애플리케이션 제어 및 대시보드 로직

window.App = {
  currentSubjectId: null,
  subjects: [],
  envGeminiKey: "",

  async init() {
    // 1. 환경 변수(window.ENV) 로드 및 Supabase 클라이언트 초기화
    let supabaseUrl = "";
    let supabaseAnonKey = "";

    if (window.ENV) {
      supabaseUrl = window.ENV.SUPABASE_URL;
      supabaseAnonKey = window.ENV.SUPABASE_ANON_KEY;
      window.App.envGeminiKey = window.ENV.GEMINI_API_KEY;
    }

    // 로컬 스토리지 또는 프롬프트 백업 처리
    if (!supabaseUrl || !supabaseAnonKey) {
      supabaseUrl = localStorage.getItem('supabase_url') || "";
      supabaseAnonKey = localStorage.getItem('supabase_anon_key') || "";

      if (!supabaseUrl || !supabaseAnonKey) {
        supabaseUrl = prompt("Supabase Project URL을 입력해 주세요:");
        supabaseAnonKey = prompt("Supabase Anon Public Key를 입력해 주세요:");
        if (supabaseUrl && supabaseAnonKey) {
          localStorage.setItem('supabase_url', supabaseUrl.trim());
          localStorage.setItem('supabase_anon_key', supabaseAnonKey.trim());
        } else {
          alert("연동 정보가 없어 작동하지 않습니다. 새로고침 후 입력해 주세요.");
          return;
        }
      }
    }

    // Supabase SDK 팩토리 객체 보존 후 클라이언트 인스턴스 할당
    // CDN에서 window.supabase로 SDK가 로드되므로 createClient 호출 전에 보존
    const supabaseLib = window.supabase;
    window.supabase = supabaseLib.createClient(supabaseUrl, supabaseAnonKey);

    // 2. 인증 모듈만 먼저 초기화 (onAuthStateChange 리스너 등록)
    await window.Auth.init();

    // 3. 네비게이션 탭 이벤트 바인딩
    window.App.bindNavigation();

    // 4. 실시간 시계 작동
    window.App.startClock();
  },

  /**
   * 로그인 성공 시 메인 대시보드 데이터 및 과목 리스트 세팅
   */
  async onLoginSuccess() {
    // 1. 수행평가 및 세특 모듈 초기화 (Supabase 클라이언트가 준비된 후 실행)
    await window.Assessment.init();
    await window.SeTeuk.init();

    // 2. 담당 과목 리스트 조회 (관리자는 전체, 교사는 본인 전용)
    await window.App.loadSubjects();

    // 3. 관리자 설정 탭 추가 초기화
    if (window.Auth.currentUser.role === 'admin') {
      await window.Admin.init();
    }

    // 4. 통계 데이터 및 로더 초기화
    await window.App.loadDashboardStats();
    await window.App.loadDashboardAlerts();
  },

  /**
   * 담당 교과 과목 리스트 조회 및 드롭다운 연동
   */
  async loadSubjects() {
    const selectEl = document.getElementById('globalSubjectSelect');
    if (!selectEl) return;

    selectEl.innerHTML = '<option value="">-- 과목을 선택하세요 --</option>';
    window.App.currentSubjectId = null;

    try {
      let query = supabase.from('subjects').select('*');
      
      // 관리자가 아닐 경우 본인이 담당하는 교과만 로드
      if (window.Auth.currentUser.role !== 'admin') {
        query = query.eq('teacher_id', window.Auth.currentUser.id);
      }

      const { data: subjects, error } = await query.order('name');
      if (error) throw error;

      window.App.subjects = subjects;

      // 담당 과목이 없을 경우 안내
      if (subjects.length === 0) {
        selectEl.innerHTML = '<option value="">담당 과목이 없습니다</option>';
        return;
      }

      subjects.forEach(sub => {
        const option = document.createElement('option');
        option.value = sub.id;
        option.textContent = `${sub.grade}학년 - ${sub.name}`;
        selectEl.appendChild(option);
      });

      // 과목 변경 이벤트 핸들러 바인딩
      selectEl.removeEventListener('change', window.App.onSubjectChange);
      selectEl.addEventListener('change', window.App.onSubjectChange);

      // 만약 과목이 한 개만 존재하면 자동으로 선택해 줌
      if (subjects.length === 1) {
        selectEl.value = subjects[0].id;
        selectEl.dispatchEvent(new Event('change'));
      }
    } catch (err) {
      console.error("과목 조회 중 오류:", err);
      selectEl.innerHTML = '<option value="">⚠️ 데이터 로드 실패</option>';
    }
  },

  /**
   * 전역 선택 과목 변경 콜백
   */
  async onSubjectChange(e) {
    window.App.currentSubjectId = e.target.value;
    
    // 타 탭 데이터 목록 동기 갱신
    await window.App.loadDashboardStats();
    await window.App.loadDashboardAlerts();
    await window.Assessment.loadAssessmentsList();
    await window.SeTeuk.loadStudentList();
  },

  /**
   * 대시보드 요약 통계 수치 로드
   */
  async loadDashboardStats() {
    if (!window.Auth.currentUser) return;

    try {
      // 1. 전체 학생 수 (과목 관계없이 등록 인원 전체)
      const { count: studentCount } = await supabase
        .from('students')
        .select('*', { count: 'exact', head: true });

      document.getElementById('statTotalStudents').innerText = `${studentCount || 0}명`;

      // 과목을 선택하지 않은 경우 나머지 수치는 스킵
      if (!window.App.currentSubjectId) {
        document.getElementById('statTotalAssessments').innerText = '0개';
        document.getElementById('statTotalNontakers').innerText = '0명';
        document.getElementById('statCompletedSeTeuk').innerText = '0건';
        return;
      }

      // 2. 해당 과목의 수행평가 수
      const { count: assessmentCount } = await supabase
        .from('assessments')
        .select('*', { count: 'exact', head: true })
        .eq('subject_id', window.App.currentSubjectId);

      document.getElementById('statTotalAssessments').innerText = `${assessmentCount || 0}개`;

      // 3. [성능 개선] 해당 과목 내 미응시 및 예외 대상자 수 (배열 다운로드 없이 카운트만 가져옴)
      const { count: nontakerCount } = await supabase
        .from('submissions')
        .select('id, assessments!inner(subject_id)', { count: 'exact', head: true })
        .eq('assessments.subject_id', window.App.currentSubjectId)
        .neq('status', '응시 완료');

      document.getElementById('statTotalNontakers').innerText = `${nontakerCount || 0}명`;

      // 4. 세특 작성 완료 건수 (status = 'completed')
      const { count: completedSeTeukCount } = await supabase
        .from('seteuk_drafts')
        .select('*', { count: 'exact', head: true })
        .eq('subject_id', window.App.currentSubjectId)
        .eq('status', 'completed');

      document.getElementById('statCompletedSeTeuk').innerText = `${completedSeTeukCount || 0}건`;

    } catch (err) {
      console.error("대시보드 통계 계산 중 에러:", err);
    }
  },

  /**
   * 대시보드 미응시자 실시간 경고 리스트 로드
   */
  async loadDashboardAlerts() {
    const listBody = document.getElementById('dashboardAlertsList');
    if (!listBody) return;

    if (!window.App.currentSubjectId) {
      listBody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-muted">과목을 선택하면 실시간 미응시 리스트가 로드됩니다.</td>
        </tr>
      `;
      return;
    }

    try {
      // submissions 내역 중 해당 과목에 속하고 '응시 완료'가 아닌 내역들 Join 쿼리
      const { data: alerts, error } = await supabase
        .from('submissions')
        .select(`
          status,
          teacher_notes,
          students(hakbun, name),
          assessments!inner(name, subject_id, subjects(name))
        `)
        .eq('assessments.subject_id', window.App.currentSubjectId)
        .neq('status', '응시 완료');

      if (error) throw error;

      listBody.innerHTML = '';
      if (!alerts || alerts.length === 0) {
        listBody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center text-muted" style="color:var(--success-color);">🟢 현재 과목에 수행평가 미응시 학생이 없습니다. 전원 응시 완료!</td>
          </tr>
        `;
        return;
      }

      alerts.forEach(alertItem => {
        const student = alertItem.students;
        const ass = alertItem.assessments;
        const tr = document.createElement('tr');
        
        let badgeClass = 'badge';
        if (alertItem.status === '미응시') {
          badgeClass = 'badge admin-badge'; // 빨간색 강조
        } else if (alertItem.status.includes('예외')) {
          badgeClass = 'badge success-badge'; // 연회색/초록색 예외
        }

        tr.innerHTML = `
          <td><strong>${student.hakbun}</strong></td>
          <td>${student.name}</td>
          <td>${ass.subjects.name}</td>
          <td>${ass.name}</td>
          <td><span class="${badgeClass}">${alertItem.status}</span></td>
          <td>${alertItem.teacher_notes || '<span class="text-muted">-</span>'}</td>
        `;
        listBody.appendChild(tr);
      });

    } catch (err) {
      listBody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-danger">현황 리스트 로드 오류: ${err.message}</td>
        </tr>
      `;
    }
  },

  /**
   * SPA 탭 스위칭 네비게이션 제어
   */
  bindNavigation() {
    document.querySelectorAll('.menu-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const targetPanelId = btn.getAttribute('data-target');

        // 사이드바 버튼 활성화 스타일 처리
        document.querySelectorAll('.menu-item').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // 패널 전환 처리
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        const targetPanel = document.getElementById(targetPanelId);
        if (targetPanel) {
          targetPanel.classList.add('active');
        }

        // 헤더 타이틀 매핑
        const titleMap = {
          'panelDashboard': '📊 대시보드 현황',
          'panelAssessment': '📝 수행평가 기록 대장',
          'panelSeTeuk': '✨ 생기부 교과 세특 초안 관리',
          'panelAdmin': '⚙️ 학교 관리자 설정',
          'panelMyPage': '👤 내 정보 관리'
        };
        document.getElementById('currentPanelTitle').innerText = titleMap[targetPanelId] || '관리 포털';
      });
    });
  },

  /**
   * 우측 상단 실시간 시간 시계 구현 (클라이언트 PC 로컬 기준)
   */
  startClock() {
    const clockEl = document.getElementById('serverTime');
    if (!clockEl) return;

    setInterval(() => {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      
      clockEl.innerText = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }, 1000);
  }
};

// 페이지 로드 시 앱 기동
window.onload = () => {
  window.App.init();
};
