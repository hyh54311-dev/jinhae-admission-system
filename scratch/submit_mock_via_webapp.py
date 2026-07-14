import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    url = "https://script.google.com/macros/s/AKfycby9eXYli0UiGMK3AKt1trzj8GeGyVMIawriE1r4N_e5mB0ZJ979LnfTPaRXvJboFy8t/exec"
    
    students = [
        {
            "ban": 1, "num": 1, "name": "김태영",
            "initialHypothesis": "청년들이 눈이 높아서 대기업만 고집하다가 취업이 안 되니까 그냥 집에서 쉬는 것 같다.",
            "statAnalysis": "2026년 상반기 청년 고용률이 43.8%로 하락한 가운데, 쉬었음 청년 수가 40만 명을 돌파했습니다. 특히 대졸 이상 고학력자가 46.7%(17만 4천 명)에 달해, 청년들이 일자리가 없어서 경제활동을 유예하고 있음을 보여줍니다.",
            "causeAnalysis": "경력직 위주의 수시 채용이 확산되면서 첫 구직 단계에서 탈락한 청년들이 '상흔 효과'를 겪고 있습니다. 잦은 좌절이 무기력증과 정서 소진(번아웃)으로 이어져 구직활동을 포기하게 만드는 심리적 기제가 작용하고 있습니다.",
            "policyIdea": "청년도전지원사업의 장기수당(350만 원) 지원을 확대하고, 지방자치단체가 주도하는 청년 공간 및 커뮤니티 기반의 정서적 상담 프로그램을 결합하여 사회 복귀를 유도해야 합니다.",
            "aiHistory": "학생: 대졸 청년들이 대기업만 선호해서 쉬는 것 아닌가요?\nAI튜터: 통계에 따르면 쉬었음 청년의 87.7%는 이미 일한 경험이 있는 자들이며 대다수가 1년 미만 단기 계약에 노출되어 번아웃을 겪었습니다. 단순히 눈높이 탓만은 아니겠지요?\n학생: 아, 그렇다면 고용 안정성의 문제가 크겠네요.",
            "reflection": "K: 청년들이 나태하거나 노력이 부족해서 쉰다고 비난조로 생각했음.\nW: 왜 대졸 고학력자의 쉬었음 비중이 절반에 육박하는지 노동시장 구조를 알고자 함.\nL: 영세한 첫 직장에서 겪은 번아웃과 수시채용 장벽이라는 다차원적 병리를 실증하게 됨. 정책적 소득 보전의 필요성에 공감함."
        },
        {
            "ban": 1, "num": 2, "name": "임언숙",
            "initialHypothesis": "지방에 일자리가 없고, 즐길 거리가 없으니 청년들이 일하기 싫어지는 것 같다.",
            "statAnalysis": "제조업 중심 도시인 경남 창원시의 청년 인구가 22만 명 급감하고 수도권으로의 순유출이 5.6배 급증하여 12,092명에 달했습니다. 지역의 정주 여건 악화와 소득 격차가 청년 이탈을 심화시킵니다.",
            "causeAnalysis": "지역 노동시장의 양질의 일자리 부족과 수도권 경제력 쏠림 현상 때문입니다. 창원 청년들의 평균 부채가 1,806만 원으로 증가하여 자산 형성이 불가능해지자, 구직 의욕을 잃고 비자발적 쉬었음 상태로 전락하고 있습니다.",
            "policyIdea": "비수도권 청년들의 지역 정착을 지원하기 위해 지역 우수 기업 고용 시 장기근속 인센티브를 확대하고 주거 비용 지원 정책을 입체적으로 연계해야 합니다.",
            "aiHistory": "학생: 창원 청년들이 서울로 가는 이유가 단순히 화려한 도시를 좋아해서인가요?\nAI튜터: 서울-경기와 비수도권 간의 평균 임금 격차는 7% 이상, IT 업종은 20% 이상 벌어지고 있습니다. 경제적 격차가 이탈을 강제하는 구조를 고민해 봅시다.",
            "reflection": "K: 지방 청년들은 고향을 싫어해서 수도권으로 간다고 단순하게 인식함.\nW: 경남과 창원 지역의 제조업 붕괴 지표와 실제 순유출률의 상관관계를 통계로 규명하고자 함.\nL: 지역 불균형이 자산 형성을 막아 비자발적 쉬었음 상태로 밀어내고 있음을 실증함. 지역 일자리 정책에 관심을 두게 됨."
        },
        {
            "ban": 1, "num": 3, "name": "조진희",
            "initialHypothesis": "부모님이 과보호하거나 용돈을 주기 때문에 굳이 힘든 일을 구하지 않고 쉬는 것이다.",
            "statAnalysis": "쉬었음 청년의 예상 소득은 180만 원으로 취업 청년의 82.7%에 불과하며, 국가적으로 연간 9.6조 원, 5년 누적 44.5조 원의 막대한 경제적 기회비용 손실을 발생시키고 있습니다.",
            "causeAnalysis": "청년층의 경제활동 배제가 장기화되면서 인적 자본 축적이 저해되고 잠재적 노동 생산성이 저하됩니다. 이는 장기적으로 세수 감소와 사회 보장 비용의 폭증으로 이어집니다.",
            "policyIdea": "청년들의 직무 역량 강화 교육과 사회적 일자리 매칭 시스템을 고도화하고, 장기 고립 청년을 위한 사회 안전망을 다차원적으로 구축해야 합니다.",
            "aiHistory": "학생: 청년 이탈이 국가 경제에 직접적인 손실을 주나요?\nAI튜터: 예상 소득 격차로 인해 국가적으로 연간 9.6조 원의 손실이 누적됩니다. 이는 잠재적 노동가치가 사장되는 큰 문제지요.",
            "reflection": "K: 부모의 과보호로 청년들이 독립심을 상실했다고 주관적으로 해석함.\nW: 국가 경제적 손실 기회비용(C_total) 공식을 통해 청년 이탈의 계량적 피해를 분석하고자 함.\nL: 개인의 안락함이 아니라 사회적 정서 치유 비용과 기회비용 손실이 맞물려 있음을 학습함. 안전망 보완의 시급성을 절감함."
        },
        {
            "ban": 1, "num": 4, "name": "강지영",
            "initialHypothesis": "요즘 직장 상사들이 꼰대 같고 힘들게 하니까 청년들이 견디지 못하고 다 도망치는 것 같다.",
            "statAnalysis": "장기 쉬었음 청년의 87.7%가 유경험자이나, 소기업(42.2%)이나 숙박업(12.1%) 등 영세 사업장 출신이 대부분이며 이들의 평균 근속 기간은 17.8개월에 불과한 실정입니다.",
            "causeAnalysis": "영세 업장의 불합리한 처우와 열악한 근로 환경이 만연해 있습니다. 불안정한 고용 형태(단기 계약)와 부적절한 대인 관계 갈등이 누적되면서 번아웃이 발생하여 구직을 아예 단념하는 트라우마로 이어졌습니다.",
            "policyIdea": "근로 기준법 준수 모니터링을 강화하고, 영세 소상공인 사업장 근로자를 위한 심리 상담 지원 프로그램과 공적 퇴직 위로금 안전망 제도를 신설해야 합니다.",
            "aiHistory": "학생: 청년들이 첫 직장을 너무 쉽게 관두는 것 같습니다.\nAI튜터: 그들이 일했던 환경을 보면 42.2%가 10인 미만 영세 기업이었고, 고용 불안이 높은 단기직이 많았습니다. 청년들이 마주한 현실을 들여다봅시다.",
            "reflection": "K: 끈기가 부족해 회사를 쉽게 그만두고 쉰다고 생각했음.\nW: 쉬었음 청년 중 과거 직장 경험이 있는 비율과 그들이 일했던 기업 규모를 분석하고자 함.\nL: 87.7%의 대다수가 영세 기업에서 번아웃을 겪은 유경험자임을 알고 이들의 직장 트라우마 치유가 정책적으로 연계되어야 함을 깨달음."
        },
        {
            "ban": 1, "num": 5, "name": "황요한",
            "initialHypothesis": "알고리즘이나 SNS를 보면서 남들과 비교하니까 쉽게 번아웃이 와서 숨어버리는 것 같다.",
            "statAnalysis": "경남 지역 청년의 41%가 번아웃을 경험했으며, 번아웃의 요인으로는 진로 불안(38.6%), 직무 과중(16.4%), 노동 가치 회의감(16.1%) 순으로 높게 나타났습니다.",
            "causeAnalysis": "학업 및 취업 준비 기간이 장기화되면서 장래의 진로 불안이 심화되고 있습니다. 여기에 SNS를 통한 상대적 박탈감이 대인 신뢰도를 50.2%로 하락시켜 극단적인 사회적 회피와 은둔을 자극하고 있습니다.",
            "policyIdea": "청년들의 정서적 치유를 위한 상담 인프라를 동 단위 복지센터에 확충하고, 사회적 연결망을 다시 구축해 줄 수 있는 로컬 청년 클럽 활동 지원을 법제화해야 합니다.",
            "aiHistory": "학생: 청년들이 겪는 번아웃은 단순 스트레스 수준인가요?\nAI튜터: 조사 결과 무직 상태에 대해 77.2%가 극도의 불안을 느끼며, 62.5%가 자존감 상실을 호소합니다. 단순 스트레스를 넘어선 자아 붕괴 현상에 가깝습니다.",
            "reflection": "K: 알고리즘 중독이나 남과의 비교가 나약한 멘탈을 만든다고 편견을 가짐.\nW: 경남 청년 번아웃의 다차원적 지표 비율을 조사하고 이들의 불안 수준을 계량화하고자 함.\nL: 번아웃의 가장 큰 요인이 진로 불안(38.6%)임을 포착하고, 청년들의 정서 회복을 도울 정책적 개입의 당위성을 공부함."
        },
        {
            "ban": 1, "num": 6, "name": "박서진",
            "initialHypothesis": "학교 다닐 때 공부를 대충 해서 경쟁력 있는 대학을 못 갔고, 그 결과 갈 곳이 없어진 것이다.",
            "statAnalysis": "최근 쉬었음 청년 중 고졸 비중보다 전문대 및 대졸 이상 비중이 46.7%로 매우 크게 늘어났으며, 고학력 청년층의 구직 포기가 만성화되는 구조적 기조가 통계로 확인되었습니다.",
            "causeAnalysis": "학력을 불문하고 실제 기업 수요는 IT, 신기술 등 특정 산업 분야에 집중되는데 반해 졸업생들의 전공은 매칭되지 않는 '구조적 일자리 미스매치'가 본질입니다. 고학력자일수록 눈높이를 낮추기 어려운 심리적 매몰비용도 작용합니다.",
            "policyIdea": "산업계 요구에 맞춘 대학 전공 재구조화를 유도하고, 졸업예정자 및 졸업생들을 대상으로 하는 대기업 수준의 디지털 직무 전환 무료 교육 제도를 대규모로 확대해야 합니다.",
            "aiHistory": "학생: 고학력 청년들은 충분히 좋은 일자리를 구할 수 있지 않나요?\nAI튜터: 고학력일수록 질 좋은 일자리가 한정되어 있고, 실패 시 따르는 사회적 비용과 자존감의 상처가 더 큽니다. 구조적 공급 과잉과 수요 불일치를 무시하기 어렵죠.",
            "reflection": "K: 좋은 학력이 없어 노동시장에서 탈락한 것이라 여겼음.\nW: 전문대 이상 고학력 청년의 실업 비중과 구직 단념 지속 일수를 살피고자 함.\nL: 학력 자원 배치가 어긋난 구조적 채용 정체 장벽이 청년들의 무기력을 부추겼음을 깨닫고 제도 매칭 개선 필요성에 주목함."
        },
        {
            "ban": 1, "num": 7, "name": "유형우",
            "initialHypothesis": "어릴 때부터 곱게만 자라서 육체노동이나 작은 기업의 고통을 견디기 힘들어하는 탓이다.",
            "statAnalysis": "쉬었음 청년 중 유민상 모델의 '이직-소극형'에 해당하는 집단은 과거 17개월가량 일하며 열악한 영세 기업 환경에서 야간 근무와 임금 체불 등 직장 트라우마를 심하게 겪은 것으로 드러났습니다.",
            "causeAnalysis": "근로기준법의 사각지대에 있는 5인 미만 영세 기업 등에서 발생한 인격적 모독, 노동력 착취, 고용 불안이 청년들에게 직장 트라우마를 유발해 노동 시장으로 재진입하는 것을 가로막는 공포 기제로 작용하고 있습니다.",
            "policyIdea": "중소·영세 기업의 노동 환경 감독관 제도를 대폭 확충하고, 퇴사 이후 청년들이 근로 권리 구제를 신속하게 받을 수 있는 공익 노무사 무료 매칭 제도를 활성화해야 합니다.",
            "aiHistory": "학생: 청년들은 왜 중소기업을 기피할까요?\nAI튜터: 영세 기업의 낮은 임금 안정성과 법 사각지대 괴롭힘 등이 청년들의 발길을 차단하는 심리적 억제제 역할을 합니다.",
            "reflection": "K: 중소기업 기피가 청년들이 고된 일을 기피하는 나약함 때문이라고 해석함.\nW: 초도 이탈 원인 중 부당 대우 및 근로 괴롭힘 통계를 수치적으로 알고자 함.\nL: 사각지대 노동 현장 스트레스가 상흔 효과로 구직 장벽을 세운 인과를 포착하고 공정 일터 구축 지원 필요성에 주목함."
        },
        {
            "ban": 1, "num": 8, "name": "이승우",
            "initialHypothesis": "요즘 청년들은 정부에서 주는 청년수당이나 각종 복지 혜택만 받고 탱자탱자 놀고 있다.",
            "statAnalysis": "쉬었음 청년의 자존감 수준은 취업 청년의 60% 미만으로 크게 낮으며, 무직 기간이 장기화될수록 자살 생각과 우울증 유병률이 급격하게 증가하는 보건 지표를 나타내고 있습니다.",
            "causeAnalysis": "사회로부터의 이탈이 장기화되면서 발생하는 경제적 무소득 기간 누적뿐만 아니라, 관계 단절로 인한 고립감과 자아 상실이 심각한 우울 증세로 발현되어 활동 동기를 잠식하고 있습니다.",
            "policyIdea": "단순 현금 수당을 넘어 은둔 회복 지원센터 인프라를 넓히고, 자조 모임 형태의 심리 치유 서비스와 공적 가치 봉사 기회를 동반 연계해야 합니다.",
            "aiHistory": "학생: 지원 수당이 일을 안 하게 만드는 걸까요?\nAI튜터: 청년 지원 수급자의 대다수는 교통비나 교재 구매 등 실질 취업 활동 실비로 활용하며, 장기 수급이 나태함으로 이어진다는 실증적 근거는 미약합니다.",
            "reflection": "K: 지원금만 타며 무임승차하고 편히 쉬는 중이라고 속단했음.\nW: 무직 상태 청년들의 정신 건강 유병률 및 심리적 취약성 데이터를 살피고자 함.\nL: 수당 의존이 아닌 깊은 고립과 자존감 상실의 사회적 치유가 결합되어야 실효성이 있음을 분석하게 됨."
        },
        {
            "ban": 1, "num": 9, "name": "김도현",
            "initialHypothesis": "경제가 전반적으로 불황이고 대기업들이 채용 문을 닫았으니 당연한 사회 현상이다.",
            "statAnalysis": "국내 30대 대기업의 2026년 공채 축소 비율은 65%에 달하며, 수시 및 경력 채용 전환 비율은 80%를 상회하여 신입 청년들의 진입 장벽이 극단적으로 높아진 상황입니다.",
            "causeAnalysis": "기업들의 즉시 전력감 중심 경력직 수시 채용 선호가 정착되면서 졸업 청년들이 진입해 경력을 쌓을 디딤돌 일자리 자체가 상실되었습니다. 이러한 병목 현상이 장기 구직 실패로 이어집니다.",
            "policyIdea": "중소 중견기업이 신입을 채용해 교육 훈련하는 비용에 대규모 세제 및 보조금 혜택을 부여하여 디딤돌 역할을 촉진해야 합니다.",
            "aiHistory": "학생: 신입은 경력을 대체 어디서 쌓아야 하나요?\nAI튜터: 기업들이 신입 교육 리스크를 거부하는 현상이 장벽의 주요 축입니다. 이를 보완할 정책적 디딤돌이 시급합니다.",
            "reflection": "K: 불경기로 인한 당연한 대기업 취업난 수준으로만 이해했음.\nW: 기업의 채용 형태 변화 지표와 청년 신입 일자리 기회 소멸률을 분석하고자 함.\nL: 경력을 우대하는 채용 미스매치 악순환 구조가 청년층을 고사시킴을 이해하고 인턴 훈련 정책 보완에 동의하게 됨."
        },
        {
            "ban": 1, "num": 10, "name": "최윤혁",
            "initialHypothesis": "학창 시절에 진로 교육을 제대로 안 해서 자기가 뭘 좋아하는지 몰라 쉬고 있을 것이다.",
            "statAnalysis": "쉬었음 청년의 62.5%가 '무엇을 하고 싶은지 몰라서' 혹은 '진로 계획을 수립하기 어려워서' 구직을 단념한 상태로, 학교 교육과 직업 세계의 단절이 통계적으로 입증되었습니다.",
            "causeAnalysis": "성적 중심의 수능 경쟁 공교육 체제가 청년들에게 자발적 진로 탐구 역량을 결여시켰으며, 첫 적응 실패 시 회복력을 갖지 못하고 영구 이탈하게 하는 부작용을 낳고 있습니다.",
            "policyIdea": "학교와 사회 전환기에 진로 집중 탐색 무료 프로그램과 멘토 지도를 확대 보편화하고 적성 전환 교육을 법제화해야 합니다.",
            "aiHistory": "학생: 진로 탐색 교육이 왜 중요한가요?\nAI튜터: 진로 자기효능감이 높은 학생일수록 이탈 초기 회복 속도가 빠르며 무조건적 구직 단념 확률을 현저히 경감시킵니다.",
            "reflection": "K: 자아 성찰 기피나 나태함으로 인한 진로 단념으로 파악했음.\nW: 공교육 진로 멘토링 유무와 첫 직장 정착 개월수의 상관 지표를 확인하려 함.\nL: 인생 회복력을 담보할 공교육의 적성 중심 정책 보완 필요성에 대해 공감하게 됨."
        }
    ]
    
    groups = [
        {
            "ban": 1, "groupNum": 1, 
            "members": "김태영, 임언숙, 조진희",
            "mediaType": "뉴스",
            "scenarioText": "[씬 1: 스튜디오 앵커 브리핑]\n앵커: 2026년 상반기 청년 고용률이 43.8%로 연속 하락한 가운데, '쉬었음 청년'은 40만 명을 돌파하며 역대 최고치를 기록했습니다. 고학력 대졸 쉬었음(46.7%) 청년들의 실태를 조명합니다.\n[씬 2: 창원 국가산업단지 현장 취재]\n기자: 과거 경남 지역 경제의 핵심이었던 창원시. 그러나 최근 10년간 청년 인구 22만 명이 급감하고 연간 수도권 순유출이 12,092명으로 약 5.6배 급증했습니다. 청년들의 가구 평균 부채는 1,806만 원을 돌파했습니다.\n창원 청년 인터뷰: '이 지역엔 남고 싶어도 제조업 중심의 일자리뿐이고 임금 격차가 심해 버틸 재간이 없습니다.'\n[씬 3: 스튜디오 마무리]\n앵커: 청년들의 가치가 활용되지 못하고 사장됨으로써 발생하는 국가적 경제 손실은 매년 9.6조 원에 육박합니다. 청년들이 지역에 정착하고 다시 구직을 결심할 수 있도록 하는 맞춤형 고용 안전망과 지역 정주 여건 보완이 절실합니다.",
            "alternativeType": "일반 촬영 영상",
            "mediaLink": "https://drive.google.com/file/d/1mock_video_group1_real/view?usp=sharing"
        },
        {
            "ban": 1, "groupNum": 2, 
            "members": "강지영, 황요한, 박서진",
            "mediaType": "다큐멘터리",
            "scenarioText": "[씬 1: 어두운 방, 노트북 모니터 불빛만 켜진 방안 (익스트림 클로즈업)]\n성우(독백): '첫 직장이었던 소규모 온라인 쇼핑몰. 10인 미만 영세 직장에서 매일 12시간씩 일했는데 번아웃(27.7%) 외엔 남은 게 없었어요. 17개월 만에 사직서를 냈을 때, 제 대인 신뢰도는 50.2%로 곤두박질쳤습니다.'\n[씬 2: 유민상 5분류 모델 중 '이직-소극형' 페르소나의 하루 연출]\n(화면에 무기력하게 침대에 누워 스마트폰 알고리즘 화면을 넘기는 청년의 모습)\n자막: 극심한 진로 불안(38.6%)과 전 직장에서 얻은 직장 트라우마가 만들어낸 비자발적 이탈.\n심리 전문가 인터뷰: '청년들은 게으른 것이 아니라 마음의 상처를 치료할 시간이 필요합니다. 사회가 이들을 나태하다고 비난하면 고립은 심화됩니다.'\n[씬 3: 희망의 빛 - 청년도전지원사업 참여 센터 방문]\n청년: '이곳에서 350만 원의 소득 지원과 전문 멘토의 1:1 정서 치유를 받으며 다시 이력서를 쓸 용기를 얻었습니다.'\n자막: 청년의 이탈은 낙인이 아닌 치유의 관점에서 접근해야 합니다.",
            "alternativeType": "디테일 시나리오 보고서",
            "mediaLink": "https://docs.google.com/document/d/1mock_report_group2_detailed/edit?usp=sharing"
        },
        {
            "ban": 1, "groupNum": 3, 
            "members": "유형우, 이승우, 김도현, 최윤혁",
            "mediaType": "공익광고",
            "scenarioText": "[0초~15초: 차갑고 바쁜 아침 출근길 (슬로우 모션)]\n성우: '모두가 바쁘게 앞서나가는 세상. 그 대열에서 잠시 멈춘 청년들이 있습니다. 우리는 그들을 나태하다고 부릅니다.'\n(자막: 대졸 쉬었음 청년 46.7%, 대다수가 일경험이 있는 무기력 상태)\n[15초~30초: 어두운 방안의 대비적 묘사 (첼로 연주음)]\n성우: '그러나 이들이 마주한 현실은 대기업 공채 축소 65%, 경력직 수시 채용 80%의 높은 장벽. 첫 단추를 채우기도 전에 겪는 수시 채용 장벽입니다.'\n[30초~45초: 따뜻한 톤으로 전환 (피아노 연주음 및 청년들이 모여 대화하는 창원 청년카페 공간)]\n성우: '청년들의 무직 기간 누적으로 인한 국가적 손실 연간 9.6조 원. 하지만 이보다 더 큰 손실은 청년들의 잃어버린 자존감입니다.'\n[45초~60초: 로고 화면]\n성우: '청년도전지원사업과 사회적 멘토링이 청년의 손을 잡습니다. 청년이 다시 시작할 수 있도록 사회가 함께 안전망을 넓혀야 할 때입니다.'\n(자막: 대한민국 청년들의 내일을 응원합니다. 교육부·고용노동부)",
            "alternativeType": "AI 생성 영상",
            "mediaLink": "https://drive.google.com/file/d/1mock_ai_avatar_group3/view?usp=sharing"
        }
    ]
    
    print("Initializing Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Opening Web App: {url}")
        page.goto(url)
        print("Waiting for page and frames to load...")
        time.sleep(7)
        
        # iframe 찾기
        # GAS 웹앱은 보통 'sandboxFrame' 이라는 id의 iframe을 사용하거나 첫 번째 iframe에 페이지 콘텐츠가 들어있음
        print("Listing all frames...")
        target_frame = None
        for f in page.frames:
            print(f"Frame name: {f.name}, url: {f.url}")
            # google.script 객체가 정의된 프레임 찾기
            try:
                if f.evaluate("typeof google !== 'undefined'"):
                    target_frame = f
                    print(f"--> Found target frame containing 'google': {f.name}")
                    break
            except Exception:
                pass
                
        if not target_frame:
            # 캡슐화된 iframe 탐색 대체 기법
            print("Trying default fallback frame (the first sub-frame)...")
            if len(page.frames) > 1:
                target_frame = page.frames[1]
            else:
                target_frame = page
                
        print("\n=== [1] 개인 탐구보고서 제출 시작 ===")
        for s in students:
            print(f"Submitting individual report for {s['name']} (Class {s['ban']}, No {s['num']})...")
            
            payload = {
                "ban": s["ban"],
                "num": s["num"],
                "name": s["name"],
                "initialHypothesis": s["initialHypothesis"],
                "statAnalysis": s["statAnalysis"],
                "causeAnalysis": s["causeAnalysis"],
                "policyIdea": s["policyIdea"],
                "aiHistory": s["aiHistory"],
                "reflection": ""
            }
            
            eval_js = f"""
            new Promise((resolve, reject) => {{
                google.script.run
                    .withSuccessHandler((res) => resolve(res))
                    .withFailureHandler((err) => reject(err))
                    .submitIndividualReport({payload});
            }})
            """
            try:
                res = target_frame.evaluate(eval_js)
                print(f"  Report Result: {res}")
            except Exception as e:
                print(f"  Report Error: {e}")
                
            reflection_text = f"K: {s['reflection'].split('K:')[1].split('W:')[0].strip()}\nW: {s['reflection'].split('W:')[1].split('L:')[0].strip()}\nL: {s['reflection'].split('L:')[1].strip()}"
            eval_ref_js = f"""
            new Promise((resolve, reject) => {{
                google.script.run
                    .withSuccessHandler((res) => resolve(res))
                    .withFailureHandler((err) => reject(err))
                    .submitReflectionOnly({s['ban']}, "{s['name']}", `{reflection_text}`);
            }})
            """
            try:
                res_ref = target_frame.evaluate(eval_ref_js)
                print(f"  Reflection Result: {res_ref}")
            except Exception as e:
                print(f"  Reflection Error: {e}")
                
            time.sleep(1.5)
            
        print("\n=== [2] 모둠 보고서 제출 시작 ===")
        for g in groups:
            print(f"Submitting group scenario for Group {g['groupNum']}...")
            payload_g = {
                "ban": g["ban"],
                "groupNum": g["groupNum"],
                "members": g["members"],
                "mediaType": g["mediaType"],
                "scenarioText": g["scenarioText"],
                "alternativeType": g["alternativeType"],
                "mediaLink": g["mediaLink"]
            }
            eval_grp_js = f"""
            new Promise((resolve, reject) => {{
                google.script.run
                    .withSuccessHandler((res) => resolve(res))
                    .withFailureHandler((err) => reject(err))
                    .submitGroupScenario({payload_g});
            }})
            """
            try:
                res_g = target_frame.evaluate(eval_grp_js)
                print(f"  Group Result: {res_g}")
            except Exception as e:
                print(f"  Group Error: {e}")
                
            time.sleep(1.5)
            
        print("\nAll mock data submission processes completed successfully!")
        browser.close()

if __name__ == '__main__':
    main()
