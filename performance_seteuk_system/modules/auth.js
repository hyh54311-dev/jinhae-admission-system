// auth.js - Supabase 인증 관리 모듈

window.Auth = {
  currentUser: null,

  async init() {
    // 1. Supabase 인증 상태 변경 감지
    supabase.auth.onAuthStateChange(async (event, session) => {
      if (session) {
        // 교사(teachers) 정보 조회
        const { data: teacher, error } = await supabase
          .from('teachers')
          .select('*')
          .eq('id', session.user.id)
          .single();

        if (error || !teacher) {
          console.error("교사 프로필 조회 실패:", error);
          alert("데이터베이스에 등록되지 않은 교과 교계정입니다. 관리자 교사에게 문의하세요.");
          await supabase.auth.signOut();
          return;
        }

        // 로그인 사용자 정보 설정
        window.Auth.currentUser = {
          id: session.user.id,
          email: session.user.email,
          name: teacher.name,
          role: teacher.role
        };

        // UI 업데이트
        document.getElementById('userDisplayName').innerText = `${teacher.name} 선생님`;
        const roleBadge = document.getElementById('userDisplayRole');
        roleBadge.innerText = teacher.role === 'admin' ? '관리자 교사' : '일반 교사';
        
        if (teacher.role === 'admin') {
          roleBadge.className = 'badge admin-badge';
          document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = 'flex';
          });
        } else {
          roleBadge.className = 'badge';
          document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = 'none';
          });
        }

        // 화면 전환
        document.getElementById('loginScreen').classList.remove('active');
        document.getElementById('workspaceScreen').classList.add('active');

        // 메인 애플리케이션 로그인 성공 콜백 호출
        if (window.App && typeof window.App.onLoginSuccess === 'function') {
          await window.App.onLoginSuccess();
        }
      } else {
        window.Auth.currentUser = null;
        // 화면 전환 (로그인창 복귀)
        document.getElementById('workspaceScreen').classList.remove('active');
        document.getElementById('loginScreen').classList.add('active');
      }
    });

    // 2. 로그인 폼 이벤트 리스너 등록
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // 버튼 비활성화 및 로딩 표시
        submitBtn.disabled = true;
        submitBtn.textContent = "로그인 중... ⏳";

        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        try {
          const { error } = await supabase.auth.signInWithPassword({
            email: email,
            password: password
          });

          if (error) {
            alert(`로그인 실패: ${error.message}`);
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }
        } catch (err) {
          alert(`로그인 중 오류 발생: ${err.message}`);
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        }
      });
    }

    // 3. 로그아웃 버튼 이벤트 리스너 등록
    const btnLogout = document.getElementById('btnLogout');
    if (btnLogout) {
      btnLogout.addEventListener('click', async () => {
        const confirmLogout = confirm("로그아웃 하시겠습니까?");
        if (confirmLogout) {
          await supabase.auth.signOut();
        }
      });
    }

    // 4. 개인 비밀번호 변경 폼 등록
    const formChangePassword = document.getElementById('formChangePassword');
    if (formChangePassword) {
      formChangePassword.addEventListener('submit', async (e) => {
        e.preventDefault();
        const newPassword = document.getElementById('myNewPassword').value;
        const confirmPassword = document.getElementById('myNewPasswordConfirm').value;

        if (newPassword.length < 6) {
          alert("비밀번호는 최소 6자리 이상이어야 합니다.");
          return;
        }

        if (newPassword !== confirmPassword) {
          alert("새 비밀번호와 확인 비밀번호가 일치하지 않습니다.");
          return;
        }

        const { error } = await supabase.auth.updateUser({
          password: newPassword
        });

        if (error) {
          alert(`비밀번호 변경 실패: ${error.message}`);
        } else {
          alert("비밀번호가 성공적으로 변경되었습니다. 다음 로그인부터 적용됩니다.");
          formChangePassword.reset();
        }
      });
    }
  }
};
