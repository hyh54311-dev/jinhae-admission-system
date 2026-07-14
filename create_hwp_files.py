import win32com.client
import os
import time

def create_hwp_files():
    try:
        # HWP 객체 생성
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = False # 백그라운드에서 실행

        target_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
        
        # 1. 쉬었음_청년_현상_탐구_운영계획.hwp 생성
        plan_hwp_path = os.path.join(target_dir, "쉬었음_청년_현상_탐구_운영계획.hwp")
        
        plan_html = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body style="font-family: '함초롬바탕', '맑은 고딕'; line-height: 1.6;">
            <div style="text-align: center;">
                <h1 style="color: #0b3c5d; font-size: 24pt;">학교 자율적 교육과정 탐구 주제별 운영 계획</h1>
                <p style="color: #888888; font-size: 10pt;">진해고등학교 융합 교육 프로그램</p>
            </div>
            
            <br>
            <h2 style="color: #328cc1; font-size: 14pt;">1. 탐구 주제 개요</h2>
            <table border="1" style="border-collapse: collapse; width: 100%; border-color: #cccccc;">
                <tr style="background-color: #f7f9fa;">
                    <th style="padding: 8px; width: 20%; color: #0b3c5d; text-align: left;">탐구 주제</th>
                    <td style="padding: 8px;"><b>'쉬었음 청년' 현상의 근본 원인은 무엇인가? (다차원적 분석 및 미디어 표현)</b></td>
                </tr>
                <tr>
                    <th style="padding: 8px; color: #0b3c5d; text-align: left;">대상 및 시수</th>
                    <td style="padding: 8px;">2~3학년 융합 교과 교실 / 총 12차시</td>
                </tr>
                <tr style="background-color: #f7f9fa;">
                    <th style="padding: 8px; color: #0b3c5d; text-align: left;">최종 산출물</th>
                    <td style="padding: 8px; line-height: 1.5;">
                        - [1단계] 쉬었음 청년 원인 분석 연구 보고서 (5차시 제출)<br>
                        - [2단계] 주제 의식을 담은 미디어 콘텐츠 (11차시 제출: 연극 녹화본, 뉴스 영상, 심층 인터뷰, 공익광고 중 택 1)<br>
                        - [3단계] 개인 성찰 일지 및 동료 평가서 (12차시 제출)
                    </td>
                </tr>
            </table>
            
            <br>
            <h2 style="color: #328cc1; font-size: 14pt;">2. 12차시 운영 계획</h2>
            <table border="1" style="border-collapse: collapse; width: 100%; border-color: #cccccc; font-size: 10pt;">
                <tr style="background-color: #0b3c5d; color: #ffffff;">
                    <th style="padding: 6px; width: 8%; text-align: center;"><b>차시</b></th>
                    <th style="padding: 6px; width: 32%; text-align: center;"><b>이 차시의 핵심 질문</b></th>
                    <th style="padding: 6px; width: 44%; text-align: center;"><b>주요 활동</b></th>
                    <th style="padding: 6px; width: 16%; text-align: center;"><b>산출물</b></th>
                </tr>
                <tr>
                    <td style="padding: 6px; text-align: center;"><b>1</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>우리 사회의 '쉬었음 청년' 현상은 무엇이며, 우리는 이를 어떻게 바라보고 있는가?</b></td>
                    <td style="padding: 6px;">- '쉬었음 청년' 관련 뉴스 보도 및 신문 기사 스크랩 분석<br>- 모둠별 현상에 대한 브레인스토밍 및 초기 원인 가설 리스트 작성</td>
                    <td style="padding: 6px; text-align: center;">초기 가설 목록표</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 6px; text-align: center;"><b>2</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>공식 통계는 이 현상을 어떻게 정의하며 어느 집단에서 가장 빠르게 느는가?</b></td>
                    <td style="padding: 6px;">- 통계청 경제활동인구조사(청년층 부가조사) 최근 5개년 데이터 분석<br>- 연령별·성별·학력별 데이터 교차 분석 및 엑셀 시각화</td>
                    <td style="padding: 6px; text-align: center;">데이터 독해 및<br>분류 분석표</td>
                </tr>
                <tr>
                    <td style="padding: 6px; text-align: center;"><b>3</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>노동시장의 구조적 요인(일자리 미스매치 등)은 청년들을 어떻게 내모는가?</b></td>
                    <td style="padding: 6px;">- 청년 노동시장 이중구조(대기업 vs 중소기업) 및 플랫폼 노동 실태 분석<br>- 구조적 원인과 개인적/심리적 원인의 상관관계 토론</td>
                    <td style="padding: 6px; text-align: center;">구조적 요인 분석표</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 6px; text-align: center;"><b>4</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>당사자들의 진짜 목소리는 무엇이며, 심리적 요인(번아웃 등)은 어찌 작용하는가?</b></td>
                    <td style="padding: 6px;">- 청년 당사자 인터뷰 기사 및 다큐멘터리 클립 심층 분석<br>- 심리적 번아웃과 자기효능감 저하 요인 마인드맵 작성</td>
                    <td style="padding: 6px; text-align: center;">인터뷰 분석 노트</td>
                </tr>
                <tr style="background-color: #fff0f0;">
                    <td style="padding: 6px; text-align: center; color: #c0392b;"><b>5</b></td>
                    <td style="padding: 6px; color: #c0392b;"><b>분석 자료를 종합하여 내린 '쉬었음 청년' 현상의 근본 원인은 무엇인가?</b></td>
                    <td style="padding: 6px;"><b>- 1~4차시 분석 결과를 종합하여 구조-개인적 차원의 종합 원인 도출<br>- [1단계 최종 산출물] 원인 분석 연구 보고서 작성 및 제출</b></td>
                    <td style="padding: 6px; text-align: center; color: #c0392b;"><b>연구 보고서<br>(최종 제출)</b></td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 6px; text-align: center;"><b>6</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>우리의 분석 결과를 대중에게 가장 효과적으로 전달할 매체는 무엇인가?</b></td>
                    <td style="padding: 6px;">- 미디어 유형(연극, 뉴스, 다큐/인터뷰, 공익광고 등) 탐색<br>- 모둠별 매체 선정, 핵심 메시지 구체화 및 기획안 작성</td>
                    <td style="padding: 6px; text-align: center;">미디어 기획서</td>
                </tr>
                <tr>
                    <td style="padding: 6px; text-align: center;"><b>7</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>쉬었음 청년의 내러티브(Narrative)와 핵심 메시지를 어찌 담을 것인가?</b></td>
                    <td style="padding: 6px;">- 등장인물 설정 및 갈등 구도 설계<br>- 시나리오 및 대본(Script) 초안 작성</td>
                    <td style="padding: 6px; text-align: center;">시나리오 대본 초안</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 6px; text-align: center;"><b>8</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>시나리오가 주제 의식을 잘 전달하며, 제작 현실성이 있는가?</b></td>
                    <td style="padding: 6px;">- 모둠 간 상호 피드백 및 교사 피드백 반영 대본 수정<br>- 촬영 콘티(스토리보드) 및 역할 분담표 작성</td>
                    <td style="padding: 6px; text-align: center;">수정 대본 및 콘티</td>
                </tr>
                <tr>
                    <td style="padding: 6px; text-align: center;"><b>9</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>실제 촬영/녹화를 위해 연기와 연출, 촬영 구도를 어찌 조율할 것인가?</b></td>
                    <td style="padding: 6px;">- 모둠별 대본 낭독 및 연기/연출 리허설 진행<br>- 촬영 장비(스마트폰 등), 장소, 소품 등 점검</td>
                    <td style="padding: 6px; text-align: center;">촬영 계획서</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 6px; text-align: center;"><b>10</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>기획한 시나리오와 콘티대로 생생하게 영상을 담아내고 있는가?</b></td>
                    <td style="padding: 6px;">- 스마트폰 등을 활용한 미디어 본격 촬영 및 녹화<br>- (연극 모둠) 연기 직접 녹화 / (뉴스/인터뷰/광고) 씬별 촬영</td>
                    <td style="padding: 6px; text-align: center;">촬영 원본 파일</td>
                </tr>
                <tr style="background-color: #f0f7ff;">
                    <td style="padding: 6px; text-align: center; color: #2980b9;"><b>11</b></td>
                    <td style="padding: 6px; color: #2980b9;"><b>전달력을 높이고 오해를 줄이기 위해 어찌 영상을 편집할 것인가?</b></td>
                    <td style="padding: 6px;"><b>- 동영상 편집 앱을 활용한 컷 편집, 가독성 자막 및 효과음 삽입<br>- [2단계 최종 산출물] 미디어 콘텐츠 영상 완성 및 제출</b></td>
                    <td style="padding: 6px; text-align: center; color: #2980b9;"><b>최종 미디어 영상<br>(최종 제출)</b></td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td style="padding: 6px; text-align: center;"><b>12</b></td>
                    <td style="padding: 6px; color: #0b3c5d;"><b>우리와 다른 모둠의 문제 진단은 어찌 다르며, 우리는 어찌 성장했는가?</b></td>
                    <td style="padding: 6px;">- 모둠별 최종 영상 상영회(시사회) 진행 및 상호 평가<br>- 활동 전체에 대한 개인별 성찰 일지 작성 및 공유</td>
                    <td style="padding: 6px; text-align: center;">성찰 일지</td>
                </tr>
            </table>
            
            <br>
            <h2 style="color: #328cc1; font-size: 14pt;">3. 차시별 상세 운영 가이드</h2>
            
            <h4 style="color: #0b3c5d; font-size: 11pt; margin-bottom: 5px;">■ 1~5차시: 자료 분석 및 보고서 작성 단계</h4>
            <p style="margin-left: 10px; font-size: 10pt;">
                <b>• 1차시: 문제 발견 및 가설 설정</b> - 관련 뉴스 시청 후 브레인스토밍을 통해 원인 가설을 수립합니다.<br>
                <b>• 2차시: 통계 데이터 기반 실태 분석</b> - 통계청 데이터를 통해 성별/학력별/연령별 분포를 엑셀로 시각화합니다.<br>
                <b>• 3차시: 노동시장 구조적 원인 분석</b> - 일자리 미스매치, 대기업-중소기업의 임금 및 고용 형태 격차를 탐구합니다.<br>
                <b>• 4차시: 당사자 심층 분석 및 심리적 원인 매핑</b> - 인터뷰 및 다큐멘터리를 통해 청년들의 번아웃과 무기력 요인을 맵으로 그립니다.<br>
                <b>• 5차시: 원인 분석 보고서 작성 및 제출</b> - 분석 결과를 종합하여 모둠별 최종 연구 보고서를 작성해 제출합니다.
            </p>
            
            <h4 style="color: #0b3c5d; font-size: 11pt; margin-bottom: 5px; margin-top: 15px;">■ 6~12차시: 시나리오 작성 및 미디어 표현 단계</h4>
            <p style="margin-left: 10px; font-size: 10pt;">
                <b>• 6차시: 미디어 매체 선정 및 기획</b> - 모둠에 가장 알맞은 매체(연극, 뉴스, 다큐, 공익광고)를 선정해 기획합니다.<br>
                <b>• 7차시: 시나리오 및 대본 작성</b> - 매체 형식에 맞춰 구체적인 극 대본, 앵커 멘트, 나레이션을 작성합니다.<br>
                <b>• 8차시: 대본 피드백 및 스토리보드 작성</b> - 동료 평가를 거쳐 대본을 다듬고 화면 구성용 스토리보드를 작성합니다.<br>
                <b>• 9차시: 촬영 준비 및 리허설</b> - 연기 및 낭독 연습을 하고 촬영용 소품, 장비를 최종 점검합니다.<br>
                <b>• 10차시: 미디어 촬영 및 녹화</b> - 학교 공간 등을 활용해 연극 연기 녹화 또는 뉴스 리포팅을 촬영합니다.<br>
                <b>• 11차시: 미디어 편집 및 완성</b> - 컷 편집 및 자막 처리를 한 뒤 최종 동영상 파일로 인코딩하여 제출합니다.<br>
                <b>• 12차시: 상영회 및 성찰</b> - 학급 상영회에서 작품을 시청한 후 상호 평가 및 개인 성찰 일지를 작성합니다.
            </p>
        </body>
        </html>
        """
        
        # 파일 열기 및 저장
        hwp.Run("FileNew")
        hwp.SetTextFile(plan_html, "HTML")
        hwp.SaveAs(plan_hwp_path)
        print(f"SUCCESS: Plan HWP created at {plan_hwp_path}")

        # 2. 쉬었음_청년_연구보고서_양식.hwp 생성
        report_hwp_path = os.path.join(target_dir, "쉬었음_청년_연구보고서_양식.hwp")
        
        report_html = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body style="font-family: '함초롬바탕', '맑은 고딕'; line-height: 1.6;">
            <div style="border: 2px solid #0b3c5d; padding: 20px; text-align: center;">
                <span style="font-size: 11pt; color: #7f8c8d;">[학교 자율적 교육과정 탐구 결과물]</span><br>
                <h1 style="color: #0b3c5d; font-size: 26pt; margin: 10px 0;">'쉬었음 청년' 현상 원인 분석 연구 보고서</h1>
                <br>
                <table border="1" style="border-collapse: collapse; margin: 0 auto; width: 60%; border-color: #bdc3c7; font-size: 11pt;">
                    <tr>
                        <th style="padding: 6px; background-color: #f2f2f2; width: 30%; text-align: center;">모둠명</th>
                        <td style="padding: 6px; text-align: center;">[ 예: 청년희망모둠 ]</td>
                    </tr>
                    <tr>
                        <th style="padding: 6px; background-color: #f2f2f2; text-align: center;">작성 인원</th>
                        <td style="padding: 6px; text-align: center;">[ 모둠원 이름 전체 입력 ]</td>
                    </tr>
                    <tr>
                        <th style="padding: 6px; background-color: #f2f2f2; text-align: center;">제출일</th>
                        <td style="padding: 6px; text-align: center;">2026년 7월 15일</td>
                    </tr>
                </table>
            </div>
            
            <p style="color: #c0392b; background-color: #fdf2e9; padding: 8px; font-size: 9pt;">
                ※ [안내] 괄호 [ ]로 표시된 부분은 안내 가이드를 참고하여 작성한 후, 괄호와 가이드 내용은 삭제하고 최종 제출하세요.
            </p>
            
            <br>
            <h2 style="font-size: 14pt; color: #0b3c5d; border-bottom: 2px solid #0b3c5d; padding-bottom: 3px;">Ⅰ. 서론</h2>
            
            <h3 style="font-size: 11pt; color: #2c3e50;">1. 연구 배경 및 필요성</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #7f8c8d;">
                [최근 우리 사회에서 비경제활동인구 중 '쉬었음 청년'이 급증하고 있는 실태와 이 현상이 개인과 사회에 미치는 심각한 문제에 관해 서술하세요. 아울러 개인의 나태함이 아닌 다차원적 원인을 과학적으로 규명해야 하는 필요성을 설명해 줍니다.]
            </p>
            
            <h3 style="font-size: 11pt; color: #2c3e50; margin-top: 15px;">2. 연구 질문 및 가설 설정</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #34495e;">
                • <b>연구 질문</b>: '쉬었음 청년' 현상을 유발하는 거시적·미시적 요인은 무엇인가?<br>
                • <b>연구 가설</b>:<br>
                - <i>가설 1</i>: [예시: 노동시장의 격차(대기업-중소기업 격차)로 인한 일자리 미스매치가 청년의 구직 단념을 유도할 것이다.]<br>
                - <i>가설 2</i>: [예시: 실패 경험과 구직 장기화로 인한 심리적 번아웃이 구직 포기를 심화시킬 것이다.]
            </p>
            
            <br>
            <h2 style="font-size: 14pt; color: #0b3c5d; border-bottom: 2px solid #0b3c5d; padding-bottom: 3px; margin-top: 25px;">Ⅱ. 본론</h2>
            
            <h3 style="font-size: 11pt; color: #2c3e50;">1. '쉬었음 청년' 추이 및 통계 분석</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #7f8c8d;">
                [최근 5개년 통계청 데이터를 토대로 '쉬었음 청년'의 변화 그래프를 삽입하고 특징을 기술하세요. (성별, 학력별, 연령대별 차이를 설명)]
            </p>
            
            <h3 style="font-size: 11pt; color: #2c3e50; margin-top: 20px;">2. 노동시장의 구조적 요인 분석</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #7f8c8d;">
                [일자리 미스매치, 대기업과 중소기업 간의 근로여건 격차, 첫 일자리 진입 시의 고용 형태 불안정 등 경제 구조의 한계를 서술하세요.]
            </p>
            
            <h3 style="font-size: 11pt; color: #2c3e50; margin-top: 20px;">3. 심리적 및 개인적 요인 분석</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #7f8c8d;">
                [구직 실패로 인한 자존감 상락, 사회적 압박감, 무기력증 및 우울감 요인을 당사자들의 목소리를 담은 인터뷰 자료를 바탕으로 작성하세요.]
            </p>
            
            <h3 style="font-size: 11pt; color: #2c3e50; margin-top: 20px;">4. 거시 구조와 개인 심리의 인과적 상관관계</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #7f8c8d;">
                [구조적 일자리 미스매치 현상이 청년 개인의 실패 경험으로 치환되어 심리적 단념으로 이어지는 순환 고리를 설명하세요.]
            </p>
            
            <br>
            <h2 style="font-size: 14pt; color: #0b3c5d; border-bottom: 2px solid #0b3c5d; padding-bottom: 3px; margin-top: 25px;">Ⅲ. 결론 및 제언</h2>
            
            <h3 style="font-size: 11pt; color: #2c3e50;">1. 연구 결과 종합</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #7f8c8d;">
                [탐구를 통해 파악한 핵심 원인들을 1~2개 문단으로 간결하게 정리하고 가설 검증 여부를 밝힙니다.]
            </p>
            
            <h3 style="font-size: 11pt; color: #2c3e50; margin-top: 15px;">2. 사회적·정책적 대안 제언</h3>
            <p style="margin-left: 10px; font-size: 10pt; color: #7f8c8d;">
                [청년들의 사회 재진입을 돕기 위해 필요한 제도적 정책 대안(맞춤형 정보 제공, 심리 회복 프로그램 등)을 구체적으로 제안합니다.]
            </p>
            
            <br>
            <h2 style="font-size: 14pt; color: #0b3c5d; border-bottom: 2px solid #0b3c5d; padding-bottom: 3px; margin-top: 25px;">Ⅳ. 참고 문헌</h2>
            <p style="margin-left: 10px; font-size: 9pt; color: #7f8c8d;">
                [인용한 자료와 논문, 언론 보도 출처를 양식에 맞춰 작성하세요.]<br>
                1. 통계청, 「경제활동인구조사 청년층 부가조사 결과」, 2025.<br>
                2. [참고 자료 출처를 여기에 기재]
            </p>
            
            <br>
            <h2 style="font-size: 12pt; color: #2c3e50; border-bottom: 1px dashed #bdc3c7; padding-bottom: 3px; margin-top: 25px;">[부록] 모둠원 역할 분담 및 기여도 자체 평가표</h2>
            <table border="1" style="border-collapse: collapse; width: 100%; border-color: #bdc3c7; font-size: 9pt; margin-top: 10px;">
                <tr style="background-color: #f2f2f2; font-weight: bold; text-align: center;">
                    <th style="padding: 6px; width: 25%;">학번 / 이름</th>
                    <th style="padding: 6px; width: 45%;">상세 담당 역할</th>
                    <th style="padding: 6px; width: 10%;">기여도</th>
                    <th style="padding: 6px; width: 20%;">소감</th>
                </tr>
                <tr>
                    <td style="padding: 6px; text-align: center;">[ 예: 20101 홍길동 ]</td>
                    <td style="padding: 6px;">[ 예: 전체 자료 조사 총괄 및 서론, 결론 파트 문서 작성 ]</td>
                    <td style="padding: 6px; text-align: center;">33%</td>
                    <td style="padding: 6px;">[ 개인별 소감 ]</td>
                </tr>
                <tr>
                    <td style="padding: 6px; text-align: center;">[ 예: 20102 김철수 ]</td>
                    <td style="padding: 6px;">[ 예: 통계 데이터 엑셀 분류 및 분석 결과 그래프 제작 ]</td>
                    <td style="padding: 6px; text-align: center;">33%</td>
                    <td style="padding: 6px;">[ 개인별 소감 ]</td>
                </tr>
                <tr>
                    <td style="padding: 6px; text-align: center;">[ 예: 20103 이영희 ]</td>
                    <td style="padding: 6px;">[ 예: 청년 인터뷰 사례 요약 분석 및 미디어 기획 연계 ]</td>
                    <td style="padding: 6px; text-align: center;">34%</td>
                    <td style="padding: 6px;">[ 개인별 소감 ]</td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        # 파일 열기 및 저장
        hwp.Run("FileNew")
        hwp.SetTextFile(report_html, "HTML")
        hwp.SaveAs(report_hwp_path)
        print(f"SUCCESS: Report HWP created at {report_hwp_path}")

        hwp.Quit()
        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            hwp.Quit()
        except:
            pass
        return False

if __name__ == "__main__":
    create_hwp_files()
