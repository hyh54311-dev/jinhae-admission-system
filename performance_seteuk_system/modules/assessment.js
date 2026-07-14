// assessment.js - 수행평가 관리 및 미응시/예외 처리 모듈

window.Assessment = {
  currentAssessmentId: null,

  async init() {
    // 1. 수행평가 항목 선택 변경 시 명단 로드
    const selectEl = document.getElementById('assessmentSelect');
    if (selectEl) {
      selectEl.addEventListener('change', async (e) => {
        window.Assessment.currentAssessmentId = e.target.value;
        await window.Assessment.loadStudentRoster();
      });
    }

    // 2. 신규 수행평가 추가 모달 열기 버튼 바인딩
    const btnOpenModal = document.getElementById('btnCreateAssessmentModal');
    if (btnOpenModal) {
      btnOpenModal.addEventListener('click', () => {
        if (!window.App.currentSubjectId) {
          alert("과목을 먼저 선택해 주세요.");
          return;
        }
        document.getElementById('modalCreateAssessment').classList.add('active');
      });
    }

    // 3. 신규 수행평가 추가 폼 제출 리스너
    const formCreateAssessment = document.getElementById('formCreateAssessment');
    if (formCreateAssessment) {
      formCreateAssessment.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('newAssessmentName').value.trim();
        const maxScore = parseFloat(document.getElementById('newAssessmentMaxScore').value);
        const dueDate = document.getElementById('newAssessmentDueDate').value || null;

        try {
          const { data, error } = await supabase
            .from('assessments')
            .insert([
              {
                subject_id: window.App.currentSubjectId,
                name: name,
                max_score: maxScore,
                due_date: dueDate
              }
            ])
            .select();

          if (error) throw error;

          alert("수행평가 항목이 새로 추가되었습니다.");
          document.getElementById('modalCreateAssessment').classList.remove('active');
          formCreateAssessment.reset();
          
          // 수행평가 목록 다시 로드
          await window.Assessment.loadAssessmentsList();
          
          // 새로 만든 평가를 자동 선택
          if (data && data[0]) {
            document.getElementById('assessmentSelect').value = data[0].id;
            window.Assessment.currentAssessmentId = data[0].id;
            await window.Assessment.loadStudentRoster();
          }
        } catch (err) {
          alert(`수행평가 추가 중 오류 발생: ${err.message}`);
        }
      });
    }
  },

  /**
   * 전역 과목 변경 시 수행평가 리스트 드롭다운 갱신
   */
  async loadAssessmentsList() {
    const selectEl = document.getElementById('assessmentSelect');
    if (!selectEl) return;

    // 리스트 초기화
    selectEl.innerHTML = '<option value="">-- 수행평가를 선택하세요 --</option>';
    window.Assessment.currentAssessmentId = null;
    document.getElementById('assessmentRosterList').innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-muted">수행평가 항목을 선택하면 명단이 활성화됩니다.</td>
      </tr>
    `;
    document.getElementById('assessmentRosterCount').innerText = '학생 0명';

    if (!window.App.currentSubjectId) return;

    try {
      const { data: assessments, error } = await supabase
        .from('assessments')
        .select('*')
        .eq('subject_id', window.App.currentSubjectId)
        .order('created_at', { ascending: true });

      if (error) throw error;

      assessments.forEach(ass => {
        const option = document.createElement('option');
        option.value = ass.id;
        const dueText = ass.due_date ? ` (~${ass.due_date})` : '';
        option.textContent = `${ass.name} (배점: ${ass.max_score}점)${dueText}`;
        selectEl.appendChild(option);
      });
    } catch (err) {
      console.error("수행평가 항목 로드 오류:", err);
    }
  },

  /**
   * 해당 과목 학년의 학생 명단 및 각 학생의 수행평가 제출/미응시 내역 로드
   */
  async loadStudentRoster() {
    const tbody = document.getElementById('assessmentRosterList');
    if (!tbody) return;

    if (!window.Assessment.currentAssessmentId) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center text-muted">수행평가 항목을 선택하면 명단이 활성화됩니다.</td>
        </tr>
      `;
      document.getElementById('assessmentRosterCount').innerText = '학생 0명';
      return;
    }

    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center">로스터 데이터를 불러오는 중... ⏳</td>
      </tr>
    `;

    try {
      // 1. 현재 과목 정보 획득 (학년 체크용)
      const currentSubject = window.App.subjects.find(s => s.id === window.App.currentSubjectId);
      if (!currentSubject) return;

      // 2. 해당 학년의 전체 학생 리스트 로드
      const { data: students, error: studentError } = await supabase
        .from('students')
        .select('*')
        .eq('grade', currentSubject.grade)
        .order('hakbun', { ascending: true });

      if (studentError) throw studentError;

      // 3. 해당 수행평가에 대한 응시 기록(submissions) 로드
      const { data: submissions, error: subError } = await supabase
        .from('submissions')
        .select('*')
        .eq('assessment_id', window.Assessment.currentAssessmentId);

      if (subError) throw subError;

      // 4. 빠른 조회를 위해 제출 기록 맵핑 구성 (Student ID -> Submission 객체)
      const submissionMap = {};
      submissions.forEach(sub => {
        submissionMap[sub.student_id] = sub;
      });

      // 5. 로스터 테이블 그리기
      tbody.innerHTML = '';
      document.getElementById('assessmentRosterCount').innerText = `학생 ${students.length}명`;

      students.forEach(student => {
        const sub = submissionMap[student.id];
        const status = sub ? sub.status : '미응시'; // 기본값 미응시
        const score = sub && sub.score !== null ? sub.score : '';
        const content = sub && sub.submitted_content ? sub.submitted_content : '';
        const notes = sub && sub.teacher_notes ? sub.teacher_notes : '';

        const tr = document.createElement('tr');
        
        // 상태값 선택 드롭다운 옵션 동적 구성
        const statusOptions = ['미응시', '응시 완료', '예외(위탁)', '예외(자퇴)', '예외(전출)'];
        let statusSelectHTML = `<select class="form-control status-select" data-student-id="${student.id}" style="width:120px;">`;
        statusOptions.forEach(opt => {
          const selected = opt === status ? 'selected' : '';
          statusSelectHTML += `<option value="${opt}" ${selected}>${opt}</option>`;
        });
        statusSelectHTML += `</select>`;

        tr.innerHTML = `
          <td><strong>${student.hakbun}</strong></td>
          <td>${student.class}반 ${student.number}번</td>
          <td>${student.name}</td>
          <td>${statusSelectHTML}</td>
          <td>
            <input type="number" class="form-control score-input" data-student-id="${student.id}" value="${score}" placeholder="점수" style="width:75px;" min="0">
          </td>
          <td>
            <textarea class="form-control content-textarea" data-student-id="${student.id}" rows="1" placeholder="답안/수행물" style="min-width:150px; font-size:12px;">${content}</textarea>
          </td>
          <td>
            <input type="text" class="form-control notes-input" data-student-id="${student.id}" value="${notes}" placeholder="예외 사유 및 수기 기록" style="min-width:180px;">
          </td>
          <td>
            <button class="btn btn-primary btn-sm btn-save-row" data-student-id="${student.id}">💾 저장</button>
          </td>
        `;

        // 해당 행의 단일 저장 처리
        const btnSave = tr.querySelector('.btn-save-row');
        btnSave.addEventListener('click', async () => {
          await window.Assessment.saveSubmissionRow(student.id, tr);
        });

        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center text-danger">데이터 로드 실패: ${err.message}</td>
        </tr>
      `;
    }
  },

  /**
   * 특정 학생의 응시 기록을 DB에 업서트(Upsert) 저장
   */
  async saveSubmissionRow(studentId, rowEl) {
    const btn = rowEl.querySelector('.btn-save-row');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Saving...';

    const status = rowEl.querySelector('.status-select').value;
    const scoreVal = rowEl.querySelector('.score-input').value;
    const score = scoreVal !== '' ? parseFloat(scoreVal) : null;
    const content = rowEl.querySelector('.content-textarea').value.trim();
    const notes = rowEl.querySelector('.notes-input').value.trim();

    try {
      // submissions 테이블 업서트 수행 (assessment_id, student_id 고유 제약조건 기준 자동 매칭)
      const { error } = await supabase
        .from('submissions')
        .upsert({
          assessment_id: window.Assessment.currentAssessmentId,
          student_id: studentId,
          status: status,
          score: score,
          submitted_content: content,
          teacher_notes: notes,
          updated_by: window.Auth.currentUser.id,
          updated_at: new Date()
        }, { onConflict: 'assessment_id,student_id' });

      if (error) throw error;

      btn.className = 'btn btn-success btn-sm btn-save-row';
      btn.textContent = '완료 ✓';
      
      // 1초 뒤 원래 스타일로 복원
      setTimeout(() => {
        btn.className = 'btn btn-primary btn-sm btn-save-row';
        btn.textContent = originalText;
        btn.disabled = false;
      }, 1000);

      // 대시보드 및 세특 학생 리스트 상태 동기화 트리거
      if (window.App && typeof window.App.loadDashboardStats === 'function') {
        window.App.loadDashboardStats(); // 백그라운드 호출
      }
    } catch (err) {
      alert(`저장 오류: ${err.message}`);
      btn.className = 'btn btn-danger btn-sm btn-save-row';
      btn.textContent = '실패 ✗';
      setTimeout(() => {
        btn.className = 'btn btn-primary btn-sm btn-save-row';
        btn.textContent = originalText;
        btn.disabled = false;
      }, 2000);
    }
  }
};
