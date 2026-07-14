/**
 * 吏꾪빐怨좊벑?숆탳 ?낇븰 ?곷떞 梨쀫큸 2.0 - Core Logic
 */

const CONFIG = {
    API_KEY: "", // 蹂댁븞???꾪빐 ?쒕쾭?ъ씠??Vercel)?먯꽌 愿由ы빀?덈떎.
    MODEL: "gemini-3.1-flash-lite", // ?ъ슜???붿껌???곕씪 理쒖떊 3.1 Pro Preview 紐⑤뜽 ?곸슜
    SYSTEM_PROMPT: `?뱀떊? '吏꾪빐怨좊벑?숆탳'??移쒖젅?섍퀬 ?꾨Ц?곸씤 ?낇븰 ?곷떞 援먯궗?낅땲?? 
?꾨옒 ?쒓났??[?낇븰 ?곷떞 吏??踰좎씠??瑜?諛뷀깢?쇰줈 ?숈깮怨??숇?紐⑥쓽 吏덈Ц???듬??섏꽭??

[?듬? 洹쒖튃]
1. ??긽 ?곕쑜?섍퀬 ?ㅼ젙??議대뙎留먯쓣 ?ъ슜?섏꽭??
2. 諛섎뱶??[?낇븰 ?곷떞 吏??踰좎씠????洹쇨굅?섏뿬 ?듬??섏꽭?? 
3. 吏??踰좎씠?ㅼ뿉 ?녿뒗 ?댁슜? 異붿륫?섏? 留먭퀬 "?뺥솗???덈궡瑜??꾪빐 蹂멸탳 援먮Т??055-546-2260)濡?臾몄쓽??二쇱떆硫?媛먯궗?섍쿋?듬땲??"?쇨퀬 ?덈궡?섏꽭??
4. ?듬?? 媛꾧껐?섎㈃?쒕룄 ?듭떖 ?뺣낫媛 ?덉뿉 ???꾨룄濡?援ъ꽦?섏꽭??(?꾩슂???대え吏 ?ъ슜).

[?낇븰 ?곷떞 吏??踰좎씠??
${JSON.stringify(ADMISSION_KNOWLEDGE, null, 2)}
`
};

const chatHistory = document.getElementById('chat-history');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

// ????댁뿭 ???(AI 而⑦뀓?ㅽ듃 ?좎???
let chatMessages = [];

// 珥덇린 硫붿떆吏???쒖뒪???쒖뒪???꾨＼?꾪듃???쒖떆?섏? ?딆쓬
function addMessage(role, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    messageDiv.innerHTML = text.replace(/\n/g, '<br>');
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 濡쒕뵫 ?곹깭 ?쒖떆
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading-indicator';
    loadingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    chatHistory.appendChild(loadingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return loadingDiv;
}

async function callGemini(prompt) {
    // 濡쒖뺄 諛?諛고룷 ?섍꼍 怨듭슜 ?붾뱶?ъ씤??(?곷? 寃쎈줈 ?ъ슜)
    const url = `/api/chat`;
    
    // 硫붿떆吏 援ъ꽦 (?쒖뒪???꾨＼?꾪듃 + ?꾩옱 吏덈Ц)
    const contents = [
        { role: "user", parts: [{ text: `${CONFIG.SYSTEM_PROMPT}\n\n?ъ슜?? ${prompt}` }] }
    ];

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                apiKey: CONFIG.API_KEY,
                model: CONFIG.MODEL,
                contents: contents 
            })
        });

        const data = await response.json();
        
        if (data.error) {
            console.error('Proxy Error:', data.error);
            const errorMsg = typeof data.error === 'object' ? JSON.stringify(data.error) : data.error;
            return `?ㅻ쪟媛 諛쒖깮?덉뒿?덈떎: ${errorMsg}`;
        }

        if (data.candidates && data.candidates[0].content) {
            return data.candidates[0].content.parts[0].text;
        } else {
            console.error('API Response Error:', data);
            return "二꾩넚?⑸땲?? ?듬????앹꽦?섎뒗 以묒뿉 臾몄젣媛 諛쒖깮?덉뒿?덈떎.";
        }
    } catch (error) {
        console.error('Fetch Error:', error);
        return "濡쒖뺄 ?쒕쾭? ?듭떊?섎뒗 以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎. 'start_chat.py'媛 ?ㅽ뻾 以묒씤吏 ?뺤씤??二쇱꽭??";
    }
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // ?ъ슜??硫붿떆吏 異붽?
    addMessage('user', text);
    userInput.value = '';

    // 遊??듬? ?湲?    const loadingIndicator = showLoading();
    const botResponse = await callGemini(text);
    
    // 濡쒕뵫 ?쒓굅 諛??듬? 異붽?
    loadingIndicator.remove();
    addMessage('bot', botResponse);
});

// ???≪뀡 踰꾪듉 泥섎━
function sendQuickMessage(text) {
    userInput.value = text;
    chatForm.dispatchEvent(new Event('submit'));
}

// ?낅젰李??ъ빱???먮룞 ?좎?
window.onload = () => userInput.focus();

