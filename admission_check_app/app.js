document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('checkForm');
    const studentIdInput = document.getElementById('studentId');
    const studentNameInput = document.getElementById('studentName');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    const resultBox = document.getElementById('resultBox');

    // 구글 시트 CSV 내보내기 URL
    // (gviz/tq 를 사용하여 CORS 문제 없이 가져오기 유리함)
    const SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1EVwwxdU4rDRuqTHDSB-1cn5Bx85rqA_uo3disf4uVNo/gviz/tq?tqx=out:csv";

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const targetId = studentIdInput.value.trim();
        const targetName = studentNameInput.value.trim();

        if (!targetId || !targetName) {
            showResult('error', '입력 오류', '학번과 이름을 모두 입력해주세요.');
            return;
        }

        setLoading(true);

        Papa.parse(SHEET_CSV_URL, {
            download: true,
            header: false, // 배열 형태로 가져오기 (인덱스로 접근하기 위함)
            complete: function(results) {
                const data = results.data;
                checkResult(data, targetId, targetName);
            },
            error: function(err) {
                console.error("CSV 파싱 에러:", err);
                showResult('error', '서버 통신 오류', '데이터를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.');
                setLoading(false);
            }
        });
    });

    function checkResult(data, targetId, targetName) {
        let found = false;
        let isPassed = false;

        // 첫 번째 줄은 헤더일 확률이 높으므로 i=1부터 시작해도 되지만, 안전하게 전체 탐색
        for (let i = 0; i < data.length; i++) {
            const row = data[i];
            
            // 데이터가 충분한 열을 가지고 있는지 확인 (최소 3개 열 이상: 타임스탬프, 학번, 이름...)
            if (row.length < 3) continue;

            const rowId = String(row[1]).trim();
            const rowName = String(row[2]).trim();

            if (rowId === targetId && rowName === targetName) {
                found = true;
                
                // 구글 시트 gviz CSV 내보내기 시 끝에 빈 열("","")이 여러 개 붙는 현상 방지
                // 뒤에서부터 처음으로 값이 있는 열을 찾거나, 확실한 인덱스(12번째 열)를 사용
                let status = "";
                for (let j = row.length - 1; j >= 0; j--) {
                    if (row[j] && String(row[j]).trim() !== "") {
                        status = String(row[j]).trim().toUpperCase();
                        break;
                    }
                }

                if (status === 'O') {
                    isPassed = true;
                }
                break;
            }
        }

        if (!found) {
            showResult('not-found', '지원 내역 없음', `입력하신 정보(${targetId} ${targetName})와 일치하는 지원 내역이 없습니다. 학번과 이름을 다시 확인해주세요.`);
        } else if (isPassed) {
            showResult('success', '합격을 축하합니다! 🎉', `${targetName} 학생은 2026학년도 진해고등학교 입학홍보단에 최종 합격하셨습니다. 앞으로의 멋진 활동을 기대합니다!`);
            triggerConfetti(); // 간단한 효과를 위해 추가 가능
        } else {
            showResult('error', '아쉽게도 불합격입니다.', `${targetName} 학생은 아쉽게도 이번 입학홍보단에 선발되지 못했습니다. 지원해주셔서 진심으로 감사드리며, 다음 기회에 꼭 다시 뵙기를 바랍니다.`);
        }

        setLoading(false);
    }

    function showResult(type, title, desc) {
        resultBox.className = `result-box ${type}`;
        
        let icon = '';
        if (type === 'success') icon = '🎊';
        else if (type === 'error') icon = '💧';
        else if (type === 'not-found') icon = '🔍';

        resultBox.innerHTML = `
            <div class="result-icon">${icon}</div>
            <div class="result-title">${title}</div>
            <div class="result-desc">${desc}</div>
        `;
        
        resultBox.classList.remove('hidden');
    }

    function setLoading(isLoading) {
        if (isLoading) {
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
            submitBtn.disabled = true;
            resultBox.classList.add('hidden');
        } else {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    }

    // 간단한 이모지 폭죽 효과 (선택적)
    function triggerConfetti() {
        const emojis = ['🎉', '✨', '🎈', '🎊', '⭐'];
        for(let i=0; i<15; i++) {
            setTimeout(() => {
                const conf = document.createElement('div');
                conf.innerText = emojis[Math.floor(Math.random() * emojis.length)];
                conf.style.position = 'absolute';
                conf.style.left = Math.random() * 100 + 'vw';
                conf.style.top = '-20px';
                conf.style.fontSize = (Math.random() * 20 + 10) + 'px';
                conf.style.zIndex = '100';
                conf.style.pointerEvents = 'none';
                conf.style.transition = 'all 2s ease-out';
                document.body.appendChild(conf);

                setTimeout(() => {
                    conf.style.top = '100vh';
                    conf.style.transform = `rotate(${Math.random() * 360}deg) translateX(${Math.random() * 100 - 50}px)`;
                }, 50);

                setTimeout(() => {
                    conf.remove();
                }, 2000);
            }, i * 100);
        }
    }
});
