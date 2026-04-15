/**
 * AI 对话流式渲染
 */

let chatHistory = [];
let isChatStreaming = false;
let currentBaziData = null;

function initChat(baziData) {
  currentBaziData = baziData;
  chatHistory = [];
  document.getElementById('chat-card').style.display = 'block';
}

function addChatMessage(role, content, isStreaming = false) {
  const messagesEl = document.getElementById('chat-messages');
  const msgEl = document.createElement('div');
  msgEl.className = `chat-message ${role} fade-in`;

  const avatar = role === 'user' ? '👤' : '☯';
  const bubbleId = isStreaming ? 'streaming-bubble' : '';

  msgEl.innerHTML = `
    <div class="chat-avatar">${avatar}</div>
    <div class="chat-bubble ${isStreaming ? 'typing-cursor' : ''}" id="${bubbleId}">${content}</div>
  `;

  messagesEl.appendChild(msgEl);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return msgEl.querySelector('.chat-bubble');
}

async function sendChatMessage(message) {
  if (!currentBaziData) {
    addChatMessage('assistant', '请先完成八字排盘，再进行命理问答。');
    return;
  }

  if (isChatStreaming) return;

  isChatStreaming = true;
  const sendBtn = document.getElementById('chat-send-btn');
  sendBtn.disabled = true;

  // 添加用户消息
  addChatMessage('user', message);
  chatHistory.push({ role: 'user', content: message });

  // 添加助手消息占位
  const assistantBubble = addChatMessage('assistant', '', true);
  let fullText = '';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: chatHistory,
        bazi_data: currentBaziData.bazi
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            assistantBubble.classList.remove('typing-cursor');
            break;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.text) {
              fullText += parsed.text;
              assistantBubble.textContent = fullText;
              document.getElementById('chat-messages').scrollTop =
                document.getElementById('chat-messages').scrollHeight;
            }
          } catch (e) {}
        }
      }
    }

    if (fullText) {
      chatHistory.push({ role: 'assistant', content: fullText });
    }

  } catch (error) {
    assistantBubble.classList.remove('typing-cursor');
    assistantBubble.textContent = '抱歉，出现了错误：' + error.message;
  } finally {
    isChatStreaming = false;
    sendBtn.disabled = false;
  }
}

// 初始化聊天输入
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send-btn');

  sendBtn.addEventListener('click', () => {
    const msg = input.value.trim();
    if (msg) {
      input.value = '';
      input.style.height = '40px';
      sendChatMessage(msg);
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendBtn.click();
    }
  });

  input.addEventListener('input', () => {
    input.style.height = '40px';
    input.style.height = Math.min(input.scrollHeight, 100) + 'px';
  });
});
