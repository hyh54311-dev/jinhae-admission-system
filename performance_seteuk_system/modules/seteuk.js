// seteuk.js - 세특 초안 생성 및 나이스 편집 관리 모듈

window.SeTeuk = {
  students: [],
  selectedStudentId: null,
  isBatchRunning: false,
  cancelBatchFlag: false,

  async init() {
    // 1. 학생 검색 이벤트 바인딩
    const searchInput = document.getElementById('searchSeTeukStudent');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        window.SeTeuk.filterStudentList();
      });
    }

    // 2. 단건 제미나이 생성 버튼 바인딩
    const btnGenSingle = document.getElementById('btnGenerateSingleSeTeuk');
    if (btnGenSingle) {
      btnGenSingle.addEventListener('click', async () => {
        if (!window.SeTeuk.selectedStudentId) return;
        btnGenSingle.disabled = true;
        btnGenSingle.textContent = '제미나이 생성 중... ⏳';
        
        try {
          await window.SeTeuk.generateStudentSeTeuk(window.SeTeuk.selectedStudentId);
          alert("세특 초안이 성공적으로 생성되었습니다.");
        } catch (err) {
          alert(`생성 중 오류 발생: ${err.message}`);
        } finally {
          btnGenSingle.disabled = false;
          btnGenSingle.textContent = '✨ 제미나이 초안 생성 (단건)';
        }
      });
    }

    // 3. 일괄 생성 모달 열기 버튼 바인딩
    const btnBulkModal = document.getElementById('btnBulkSeTeukModal');
    if (btnBulkModal) {
      btnBulkModal.addEventListener('click', () => {
        if (!window.App.currentSubjectId) {
          alert("과목을 먼저 선택해 주세요.");
          return;
        }
        window.SeTeuk.openBulkModal();
      });
    }

    // 4. 일괄 생성 취소 버튼 바인딩
    const btnCancelBatch = document.getElementById('btnCancelBatch');
    if (btnCancelBatch) {
      btnCancelBatch.addEventListener('click', () => {
        window.SeTeuk.cancelBatchFlag = true;
        btnCancelBatch.textContent = '중단 요청 중...';
        btnCancelBatch.disabled = true;
      });
    }

    // 5. 최종 세특 편집 텍스트 변경 이벤트 (실시간 바이트 계산)
    const textareaFinal = document.getElementById('seteukFinalContent');
    if (textareaFinal) {
      textareaFinal.addEventListener('input', () => {
        window.SeTeuk.updateByteCounter();
      });
    }

    // 6. 초안 복사 버튼 바인딩
    const btnCopy = document.getElementById('btnCopyDraft');
    if (btnCopy) {
      btnCopy.addEventListener('click', () => {
        const draftText = document.getElementById('geminiDraftText').innerText;
        window.Utils.copyToClipboard(draftText)
          .then(() => {
            btnCopy.textContent = '복사 완료 ✓';
            setTimeout(() => { btnCopy.textContent = '복사하기 📋'; }, 1500);
            
            // 최종 입력창에 값이 비어있다면 초안을 자동으로 채워줌
            const finalInput = document.getElementById('seteukFinalContent');
            if (!finalInput.value.trim()) {
              finalInput.value = draftText;
              window.SeTeuk.updateByteCounter();
            }
          });
      });
    }

    // 7. 세특 데이터 저장 버튼 바인딩
    const btnSave = document.getElementById('btnSaveSeTeuk');
    if (btnSave) {
      btnSave.addEventListener('click', async () => {
        await window.SeTeuk.saveStudentSeTeukData();
      });
    }
  },

  /**
   * 전역 과목 변경 시 세특 탭 학생 리스트 새로고침
   */
  async loadStudentList() {
    const listContainer = document.getElementById('seteukStudentList');
    if (!listContainer) return;

    listContainer.innerHTML = '<li>로딩 중... ⏳</li>';
    window.SeTeuk.selectedStudentId = null;
    document.getElementById('seteukEmptyState').style.display = 'flex';
    document.getElementById('seteukEditorView').style.display = 'none';

    if (!window.App.currentSubjectId) {
      listContainer.innerHTML = '<li class="empty-list">과목을 선택하면 명단이 노출됩니다.</li>';
      return;
    }

    try {
      const currentSubject = window.App.subjects.find(s => s.id === window.App.currentSubjectId);
      if (!currentSubject) return;

      // 1. 해당 과목 학년 학생 리스트 로드
      const { data: students, error: studentError } = await supabase
        .from('students')
        .select('*')
        .eq('grade', currentSubject.grade)
        .order('hakbun', { ascending: true });

      if (studentError) throw studentError;

      // 2. 이미 작성된 세특 데이터 로드
      const { data: drafts, error: draftError } = await supabase
        .from('seteuk_drafts')
        .select('*')
        .eq('subject_id', window.App.currentSubjectId);

      if (draftError) throw draftError;

      const draftMap = {};
      drafts.forEach(d => {
        draftMap[d.student_id] = d;
      });

      // 3. 학생 데이터 셋업 및 렌더링
      window.SeTeuk.students = students.map(student => {
        const draft = draftMap[student.id];
        return {
          ...student,
          status: draft ? draft.status : 'waiting',
          raw_content: draft ? draft.raw_content : '',
          gemini_draft: draft ? draft.gemini_draft : '',
          gemini_summary: draft ? draft.gemini_summary : '',
          final_content: draft ? draft.final_content : ''
        };
      });

      window.SeTeuk.renderStudentList();
    } catch (err) {
      console.error("세특 학생 로드 실패:", err);
      listContainer.innerHTML = '<li class="empty-list text-danger">명단 불러오기 실패</li>';
    }
  },

  renderStudentList() {
    const listContainer = document.getElementById('seteukStudentList');
    if (!listContainer) return;

    listContainer.innerHTML = '';
    if (window.SeTeuk.students.length === 0) {
      listContainer.innerHTML = '<li class="empty-list">학생이 존재하지 않습니다.</li>';
      return;
    }

    window.SeTeuk.students.forEach(student => {
      const li = document.createElement('li');
      li.setAttribute('data-id', student.id);
      
      // 상태별 뱃지 클래스
      let statusClass = 'badge';
      let statusText = '대기';
      if (student.status === 'completed') {
        statusClass = 'badge success-badge';
        statusText = '완료';
      } else if (student.status === 'generating') {
        statusText = '생성중';
      } else if (student.status === 'failed') {
        statusText = '실패';
      }

      li.innerHTML = `
        <span><strong>${student.hakbun}</strong> ${student.name}</span>
        <span class="${statusClass}">${statusText}</span>
      `;

      li.addEventListener('click', () => {
        window.SeTeuk.selectStudent(student.id);
      });

      listContainer.appendChild(li);
    });
  },

  filterStudentList() {
    const query = document.getElementById('searchSeTeukStudent').value.trim().toLowerCase();
    const items = document.querySelectorAll('#seteukStudentList li');

    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      if (text.includes(query)) {
        item.style.display = 'flex';
      } else {
        item.style.display = 'none';
      }
    });
  },

  async selectStudent(studentId) {
    // 활성 상태 스타일 교체
    document.querySelectorAll('#seteukStudentList li').forEach(li => {
      if (li.getAttribute('data-id') === studentId) {
        li.classList.add('active');
      } else {
        li.classList.remove('active');
      }
    });

    const student = window.SeTeuk.students.find(s => s.id === studentId);
    if (!student) return;

    window.SeTeuk.selectedStudentId = studentId;

    // 입력 데이터 로드 및 노출
    document.getElementById('editStudentHeaderName').innerText = `${student.name} (${student.hakbun})`;
    document.getElementById('studentRawContent').value = student.raw_content || '';
    document.getElementById('geminiSummaryText').innerText = student.gemini_summary || '아직 생성된 진로 중심 요약이 없습니다.';
    document.getElementById('geminiDraftText').innerText = student.gemini_draft || '제미나이 생성 버튼을 누르면 추천 문안이 여기에 노출됩니다.';
    document.getElementById('seteukFinalContent').value = student.final_content || '';

    // 복사 버튼 활성화 여부
    const btnCopy = document.getElementById('btnCopyDraft');
    if (student.gemini_draft) {
      btnCopy.style.display = 'block';
    } else {
      btnCopy.style.display = 'none';
    }

    // 수행평가 응시 현황 요약 정보 조회
    const { count, error } = await supabase
      .from('submissions')
      .select('*', { count: 'exact', head: true })
      .eq('student_id', studentId)
      .eq('status', '응시 완료');
      
    document.getElementById('editStudentSubmissionsBadge').innerText = error ? '현황 에러' : `수행평가 ${count || 0}건 응시완료`;

    // 에디터 활성화
    document.getElementById('seteukEmptyState').style.display = 'none';
    document.getElementById('seteukEditorView').style.display = 'block';

    window.SeTeuk.updateByteCounter();
  },

  /**
   * 실시간 바이트 계산 및 나이스(1,500바이트) 제한 체크 시각화
   */
  updateByteCounter() {
    const text = document.getElementById('seteukFinalContent').value;
    const bytes = window.Utils.getNeisByteLength(text);
    const chars = text.length;

    const counterEl = document.getElementById('byteCounter');
    counterEl.innerText = `${chars}자 / ${bytes}바이트 (나이스 제한: 1,500바이트)`;

    const progressFill = document.getElementById('byteProgressFill');
    const progressTrack = progressFill.parentElement;
    
    // 퍼센트 계산 (최대 1500)
    let percent = Math.min((bytes / 1500) * 100, 100);
    progressFill.style.width = percent + '%';

    // 색상 등급 지정
    progressTrack.className = 'progress-track byte-progress-track';
    if (bytes > 1500) {
      progressTrack.classList.add('danger');
      counterEl.style.color = 'var(--error-color)';
    } else if (bytes >= 1200) {
      progressTrack.classList.add('warning');
      counterEl.style.color = 'var(--warning-color)';
    } else {
      counterEl.style.color = 'var(--text-muted)';
    }
  },

  /**
   * 현재 편집 중인 학생의 데이터 저장
   */
  async saveStudentSeTeukData() {
    if (!window.SeTeuk.selectedStudentId) return;

    const rawContent = document.getElementById('studentRawContent').value.trim();
    const finalContent = document.getElementById('seteukFinalContent').value.trim();
    const student = window.SeTeuk.students.find(s => s.id === window.SeTeuk.selectedStudentId);

    try {
      const { error } = await supabase
        .from('seteuk_drafts')
        .upsert({
          student_id: window.SeTeuk.selectedStudentId,
          subject_id: window.App.currentSubjectId,
          raw_content: rawContent,
          final_content: finalContent,
          gemini_draft: student.gemini_draft || '',
          gemini_summary: student.gemini_summary || '',
          status: finalContent ? 'completed' : 'waiting',
          updated_at: new Date()
        }, { onConflict: 'student_id,subject_id' });

      if (error) throw error;

      alert("데이터가 성공적으로 데이터베이스에 저장되었습니다.");
      
      // 내부 메모리 및 리스트 상태 동기화
      student.raw_content = rawContent;
      student.final_content = finalContent;
      student.status = finalContent ? 'completed' : 'waiting';
      window.SeTeuk.renderStudentList();
      
      // 선택 상태 원복
      window.SeTeuk.selectStudent(window.SeTeuk.selectedStudentId);
    } catch (err) {
      alert(`저장 중 오류 발생: ${err.message}`);
    }
  },

  /**
   * 단건 제미나이 세특 생성 코어 로직
   */
  async generateStudentSeTeuk(studentId) {
    const student = window.SeTeuk.students.find(s => s.id === studentId);
    if (!student) return;

    // 1. API Key 확인 (없으면 에러)
    let apiKey = localStorage.getItem('gemini_api_key') || window.App.envGeminiKey;
    if (!apiKey) {
      // 키가 없으면 로컬 스토리지에 입력을 요청함
      const userKey = prompt("Gemini API Key가 필요합니다. API 키를 입력해 주세요 (브라우저 로컬 저장):");
      if (userKey) {
        apiKey = userKey.trim();
        localStorage.setItem('gemini_api_key', apiKey);
      } else {
        throw new Error("Gemini API Key가 없어 생성이 취소되었습니다.");
      }
    }

    // 2. 수행평가 점수 및 교과 특이사항 로드 (현재 과목 소속 수행평가만 필터링, 제출 답안 포함)
    const { data: subs } = await supabase
      .from('submissions')
      .select('score, teacher_notes, submitted_content, assessments!inner(name, subject_id)')
      .eq('student_id', studentId)
      .eq('assessments.subject_id', window.App.currentSubjectId);
    
    let performanceNotes = "";
    const hasSubmissions = subs && subs.length > 0;
    if (hasSubmissions) {
      performanceNotes = subs.map(s => `[${s.assessments.name}] 점수: ${s.score || '미채점'}, 제출답안: ${s.submitted_content || '없음'}, 비고: ${s.teacher_notes || '없음'}`).join('\n');
    } else {
      performanceNotes = "기록된 수행평가 이력 없음.";
    }

    // 3. 기초 자료 검증 (수행평가 제출 내용이나 비고가 없고, 추가 관찰자료 텍스트도 없을 때만 에러)
    const rawContent = document.getElementById('studentRawContent').value.trim();
    const hasAnyRecord = rawContent || (subs && subs.some(s => s.submitted_content || s.teacher_notes || s.score !== null));
    if (!hasAnyRecord) {
      throw new Error("수행평가 기록과 추가 관찰자료가 모두 비어 있어 세특을 생성할 수 없습니다. 최소한 하나의 정보는 존재해야 합니다.");
    }

    // 3. 제미나이 프롬프트 조립
    const promptText = `당신은 대한민국 고등학교의 국어과 교사입니다. 학생의 활동 응답자료와 성적/수행평가 이력을 바탕으로, 나이스(NEIS) 학교생활기록부 교과그룹 세부능력 및 특기사항(세특)을 작성해야 합니다.
다음 조건을 반드시 지키며 작성하세요:
1. 학생의 구체적인 참여 활동, 탐구 내용, 역량 위주로 사실에 기반해 작성할 것.
2. 교사의 평가적 어조로 공손하고 객관적으로 작성할 것. (예: '~함.', '~를 주도적으로 탐구함.')
3. 분량은 공백 포함 1500바이트(나이스 입력 제한 기준)를 넘지 않는 약 400~500자 분량으로 작성할 것.
4. 출력은 반드시 다음 두 가지 파트를 JSON 형식으로 리턴할 것:
   - 'draft': 실제 나이스에 입력할 완성된 세특 문장.
   - 'summary': 다른 교사들과 공유할, 학생의 진로를 중심으로 요약한 2줄 요약문.
   
[학생 정보]
이름: ${student.name}
학번: ${student.hakbun}

[학생 제출자료/답변]
${rawContent}

[수행평가 및 특이사항]
${performanceNotes}

JSON 응답 포맷 예시:
{
  "draft": "문학 시간에 배운 시조를 바탕으로... 탐구하는 역량을 보여줌.",
  "summary": "진로인 미디어 분야에 맞추어 시조의 현대적 변용에 대해 탐구함."
}`;

    // 4. API Request
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: promptText }] }],
        generationConfig: {
          responseMimeType: "application/json",
          temperature: 0.7,
          maxOutputTokens: 1000
        }
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error ? errorData.error.message : 'API 통신 오류');
    }

    const resData = await response.json();
    const responseText = resData.candidates[0].content.parts[0].text;
    
    // JSON 파싱
    let parsedResult;
    try {
      parsedResult = JSON.parse(responseText);
    } catch (e) {
      // fallback 파싱
      console.warn("JSON 파싱 실패, 정규식으로 복구 시도");
      const draftMatch = responseText.match(/"draft"\s*:\s*"([^"]+)"/);
      const summaryMatch = responseText.match(/"summary"\s*:\s*"([^"]+)"/);
      parsedResult = {
        draft: draftMatch ? draftMatch[1] : responseText,
        summary: summaryMatch ? summaryMatch[1] : "진로 활동 탐구 완료."
      };
    }

    // 5. DB에 상태값 업데이트
    const { error: upsertError } = await supabase
      .from('seteuk_drafts')
      .upsert({
        student_id: studentId,
        subject_id: window.App.currentSubjectId,
        raw_content: rawContent,
        gemini_draft: parsedResult.draft,
        gemini_summary: parsedResult.summary,
        status: student.final_content ? 'completed' : 'waiting',
        updated_at: new Date()
      }, { onConflict: 'student_id,subject_id' });

    if (upsertError) throw upsertError;

    // 내부 메모리 동기화
    student.raw_content = rawContent;
    student.gemini_draft = parsedResult.draft;
    student.gemini_summary = parsedResult.summary;

    // 만약 현재 수정 창에 열려 있는 학생이라면 즉시 화면에도 반영
    if (window.SeTeuk.selectedStudentId === studentId) {
      document.getElementById('geminiSummaryText').innerText = parsedResult.summary;
      document.getElementById('geminiDraftText').innerText = parsedResult.draft;
      document.getElementById('btnCopyDraft').style.display = 'block';
    }

    window.SeTeuk.renderStudentList();
  },

  /**
   * 일괄 생성 모달 열기 및 명단 셋업
   */
  openBulkModal() {
    const modal = document.getElementById('modalBulkProgress');
    modal.classList.add('active');
    
    const logList = document.getElementById('batchLogList');
    logList.innerHTML = '<div class="batch-log-item info">일괄 생성 대기 중...</div>';
    
    document.getElementById('batchProgressFill').style.width = '0%';
    document.getElementById('batchProgressRatio').innerText = `0 / 0 명`;
    document.getElementById('batchProgressLabel').innerText = '대기 중...';
    document.getElementById('batchTimerBox').style.display = 'none';

    // 생성할 대상 학생 (제출자료(raw_content)가 존재하지만 세특 초안(gemini_draft)이 없는 학생 우선 선정)
    const targetStudents = window.SeTeuk.students.filter(s => s.raw_content && !s.gemini_draft);
    
    if (targetStudents.length === 0) {
      logList.innerHTML += '<div class="batch-log-item warning">⚠️ 생성 가능한 대상(답변이 있으나 초안이 비어있는 학생)이 없습니다.</div>';
      document.getElementById('btnCancelBatch').disabled = true;
      return;
    }

    document.getElementById('btnCancelBatch').disabled = false;
    document.getElementById('btnCancelBatch').textContent = '생성 중단 (Stop)';
    window.SeTeuk.cancelBatchFlag = false;

    // 일괄 백그라운드 태스크 시작
    window.SeTeuk.runBulkGenerationQueue(targetStudents);
  },

  /**
   * 일괄 배치 생성 큐 작동 (5인 생성 -> 30초 딜레이)
   */
  async runBulkGenerationQueue(targetStudents) {
    window.SeTeuk.isBatchRunning = true;
    const logList = document.getElementById('batchLogList');
    const total = targetStudents.length;

    logList.innerHTML += `<div class="batch-log-item info">총 ${total}명의 학생에 대해 일괄 생성을 시작합니다. (5인당 30초 대기)</div>`;

    let processedCount = 0;
    let batchIndex = 0;

    for (let i = 0; i < total; i++) {
      // 중단 요청 체크
      if (window.SeTeuk.cancelBatchFlag) {
        logList.innerHTML += `<div class="batch-log-item error">🛑 사용자에 의해 일괄 작업이 강제 중단되었습니다.</div>`;
        break;
      }

      const student = targetStudents[i];
      logList.innerHTML += `<div class="batch-log-item">[${i + 1}/${total}] ${student.name} (${student.hakbun}) 세특 생성 시도...</div>`;
      logList.scrollTop = logList.scrollHeight;

      try {
        await window.SeTeuk.generateStudentSeTeuk(student.id);
        logList.innerHTML += `<div class="batch-log-item success">✓ ${student.name} 생성 성공!</div>`;
        processedCount++;
      } catch (err) {
        logList.innerHTML += `<div class="batch-log-item error">✗ ${student.name} 실패: ${err.message}</div>`;
      }

      // UI 프로그레스 갱신
      const percent = (processedCount / total) * 100;
      document.getElementById('batchProgressFill').style.width = percent + '%';
      document.getElementById('batchProgressRatio').innerText = `${processedCount} / ${total} 명`;
      document.getElementById('batchProgressLabel').innerText = `세특 생성 진행 중...`;

      // 5명 처리 후 30초 대기 (단, 마지막 사람인 경우 대기 패스)
      if (processedCount > 0 && processedCount % 5 === 0 && i < total - 1) {
        document.getElementById('batchTimerBox').style.display = 'flex';
        document.getElementById('batchProgressLabel').innerText = `30초 API 속도 제한 대기 중...`;
        logList.innerHTML += `<div class="batch-log-item info">⏳ API 속도 제한으로 인해 30초 대기 구역 진입합니다.</div>`;
        logList.scrollTop = logList.scrollHeight;

        // 30초 역카운트다운
        for (let countdown = 30; countdown > 0; countdown--) {
          if (window.SeTeuk.cancelBatchFlag) break;
          document.getElementById('batchCountdown').innerText = countdown;
          await new Promise(resolve => setTimeout(resolve, 1000));
        }

        document.getElementById('batchTimerBox').style.display = 'none';
      }
    }

    // 최종 처리 결과 알림
    window.SeTeuk.isBatchRunning = false;
    document.getElementById('batchProgressLabel').innerText = '일괄 생성 완료';
    document.getElementById('btnCancelBatch').disabled = true;
    logList.innerHTML += `<div class="batch-log-item success">🎉 모든 대기열 완료! 성공: ${processedCount}/${total}</div>`;
    logList.scrollTop = logList.scrollHeight;

    // 리스트 갱신
    window.SeTeuk.renderStudentList();
    if (window.SeTeuk.selectedStudentId) {
      window.SeTeuk.selectStudent(window.SeTeuk.selectedStudentId);
    }
  }
};
