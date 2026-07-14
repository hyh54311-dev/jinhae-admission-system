// admin.js - 관리자 기능 모듈 (교사 및 학생 관리, CSV 업로드, 비밀번호 초기화)

window.Admin = {
  async init() {
    // 관리자(admin) 권한 여부 체크
    if (window.Auth.currentUser.role !== 'admin') {
      console.log("일반 교사이므로 관리자 탭 활성화를 스킵합니다.");
      return;
    }

    // 1. 개별 교사 단건 추가 폼 제출 리스너
    const formAddTeacher = document.getElementById('formAddTeacherSingle');
    if (formAddTeacher) {
      formAddTeacher.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('addTeacherName').value.trim();
        const email = document.getElementById('addTeacherEmail').value.trim();
        const tempPass = document.getElementById('addTeacherTempPassword').value;
        const role = document.getElementById('addTeacherRole').value;

        if (tempPass.length < 6) {
          alert("비밀번호는 최소 6글자 이상으로 설정해 주세요.");
          return;
        }

        try {
          const { data: newUserId, error } = await supabase.rpc('admin_create_teacher', {
            teacher_email: email,
            teacher_password: tempPass,
            teacher_name: name,
            teacher_role: role
          });

          if (error) throw error;

          alert(`${name} 선생님의 교사 계정 및 데이터베이스 프로필이 성공적으로 생성되었습니다.`);
          formAddTeacher.reset();
          await window.Admin.loadTeacherSelect();
        } catch (err) {
          alert(`교사 추가 중 오류 발생: ${err.message}`);
        }
      });
    }

    // 2. CSV 일괄 업로드 드롭존 바인딩
    window.Admin.setupCSVUpload('fileUploadTeachers', 'dropzoneTeachers', window.Admin.processTeachersCSV);
    window.Admin.setupCSVUpload('fileUploadStudents', 'dropzoneStudents', window.Admin.processStudentsCSV);

    // 3. 관리자용 교사 비밀번호 강제 초기화 폼 리스너
    const formAdminResetPassword = document.getElementById('formAdminResetPassword');
    if (formAdminResetPassword) {
      formAdminResetPassword.addEventListener('submit', async (e) => {
        e.preventDefault();
        const teacherId = document.getElementById('adminResetTeacherSelect').value;
        const newPassword = document.getElementById('adminResetNewPassword').value;

        if (!teacherId) {
          alert("비밀번호를 재설정할 대상 교사를 선택하세요.");
          return;
        }
        if (newPassword.length < 6) {
          alert("비밀번호는 최소 6글자 이상이어야 합니다.");
          return;
        }

        const confirmReset = confirm("해당 교사의 비밀번호를 강제 변경하시겠습니까?");
        if (!confirmReset) return;

        try {
          const { data, error } = await supabase.rpc('admin_reset_teacher_password', {
            target_user_id: teacherId,
            new_password: newPassword
          });

          if (error) throw error;

          alert("해당 교사의 비밀번호가 임시 비밀번호로 성공적으로 재설정되었습니다.");
          formAdminResetPassword.reset();
        } catch (err) {
          alert(`비밀번호 재설정 중 오류 발생: ${err.message}`);
        }
      });
    }

    // 4. 대상 교사 리스트 드롭다운 로드
    await window.Admin.loadTeacherSelect();
  },

  /**
   * 비밀번호 재설정용 교사 목록 드롭다운 데이터 바인딩
   */
  async loadTeacherSelect() {
    const selectEl = document.getElementById('adminResetTeacherSelect');
    if (!selectEl) return;

    const { data: teachers, error } = await supabase
      .from('teachers')
      .select('id, name')
      .order('name');

    if (error) {
      console.error("교사 명단 로드 실패:", error);
      return;
    }

    selectEl.innerHTML = '<option value="">-- 대상 교사를 선택하세요 --</option>';
    teachers.forEach(t => {
      // 본인 계정은 리스트에서 배제 (마이페이지에서 변경 유도)
      if (t.id !== window.Auth.currentUser.id) {
        const option = document.createElement('option');
        option.value = t.id;
        option.textContent = `${t.name} 선생님`;
        selectEl.appendChild(option);
      }
    });
  },

  /**
   * CSV 드래그 앤 드롭 영역 및 파일 선택 인터페이스 구성
   */
  setupCSVUpload(fileInputId, dropzoneId, processFn) {
    const fileInput = document.getElementById(fileInputId);
    const dropzone = document.getElementById(dropzoneId);

    if (!fileInput || !dropzone) return;

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.style.borderColor = 'var(--primary-color)';
      dropzone.style.background = 'rgba(59, 130, 246, 0.05)';
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
      dropzone.style.background = 'rgba(255, 255, 255, 0.01)';
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
      dropzone.style.background = 'rgba(255, 255, 255, 0.01)';
      
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        processFn(files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        processFn(fileInput.files[0]);
      }
    });
  },

  /**
   * 교사 명렬표 CSV 파싱 및 DB RPC(일괄 가입) 연동 처리
   */
  async processTeachersCSV(file) {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target.result;
      const rows = window.Utils.parseCSV(text);
      if (rows.length < 2) {
        alert("업로드된 CSV 내용이 비어 있거나 올바르지 않습니다.");
        return;
      }

      // 엑셀 규격: 성명, 이메일, 임시비밀번호, 역할 (2행부터 데이터 행 시작)
      let successCount = 0;
      let errorLogs = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (row.length < 4 || !row[0] || !row[1] || !row[2]) continue;

        const name = row[0].trim();
        const email = row[1].trim();
        const tempPassword = row[2].trim();
        const role = row[3].trim().toLowerCase() === 'admin' ? 'admin' : 'teacher';

        try {
          const { error } = await supabase.rpc('admin_create_teacher', {
            teacher_email: email,
            teacher_password: tempPassword,
            teacher_name: name,
            teacher_role: role
          });

          if (error) throw error;
          successCount++;
        } catch (err) {
          errorLogs.push(`${name} (${email}): ${err.message}`);
        }
      }

      let summaryMessage = `${successCount}명의 교사 계정이 일괄 생성 및 등록되었습니다.`;
      if (errorLogs.length > 0) {
        summaryMessage += `\n\n[등록 실패 계정 정보]\n` + errorLogs.join('\n');
      }
      alert(summaryMessage);
      await window.Admin.loadTeacherSelect();
    };
    
    // 한국어 깨짐을 방지하기 위해 EUC-KR 및 UTF-8 자동 처리 대비 (기본 UTF-8 읽기)
    reader.readAsText(file, 'utf-8');
  },

  /**
   * 학생 명렬표 CSV 파싱 및 bulk upsert 연동 처리
   */
  async processStudentsCSV(file) {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target.result;
      const rows = window.Utils.parseCSV(text);
      if (rows.length < 2) {
        alert("업로드된 CSV 내용이 유효하지 않습니다.");
        return;
      }

      // 엑셀 규격: 학번, 성명, 학년, 반, 번호
      let students = [];
      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (row.length < 5 || !row[0] || !row[1]) continue;

        const hakbun = row[0].trim();
        const name = row[1].trim();
        const grade = parseInt(row[2], 10);
        const classNum = parseInt(row[3], 10);
        const number = parseInt(row[4], 10);

        if (isNaN(grade) || isNaN(classNum) || isNaN(number)) continue;

        students.push({
          hakbun: hakbun,
          name: name,
          grade: grade,
          class: classNum,
          number: number
        });
      }

      if (students.length === 0) {
        alert("업로드된 파일 내 유효한 학생 정보가 한 명도 존재하지 않습니다.");
        return;
      }

      try {
        const { error } = await supabase
          .from('students')
          .upsert(students, { onConflict: 'hakbun' });

        if (error) throw error;

        alert(`${students.length}명의 학생 명단이 성공적으로 업로드/일괄 반영되었습니다.`);
        
        // 대시보드 통계 수치 실시간 갱신 트리거
        if (window.App && typeof window.App.loadDashboardStats === 'function') {
          await window.App.loadDashboardStats();
        }
      } catch (err) {
        alert(`학생 일괄 업로드 실패: ${err.message}`);
      }
    };
    reader.readAsText(file, 'utf-8');
  }
};
