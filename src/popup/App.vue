<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import Sidebar from './components/Sidebar.vue'
import Dock from './components/Dock.vue';

const wsUrl = ref('ws://localhost:5151');
const status = ref('Idle');
const messageToSend = ref('');
const receivedMessages = ref('');
const jsonValidationStatus = ref('');
const jsonValidationClass = ref('');
const connectBtnDisabled = ref(false);
const disconnectBtnDisabled = ref(true);
const sendBtnDisabled = ref(true);
const wsUrlDisabled = ref(false);

let websocket: WebSocket | null = null;

const updateStatus = (message: string, isError = false) => {
  status.value = message;
  console.log(`Status: ${message}`);
};

const logReceivedMessage = (message: string) => {
  const timestamp = new Date().toLocaleTimeString();
  receivedMessages.value += `[${timestamp}] Received: ${message}\n\n`;
};

const connectWebSocket = () => {
  if (!wsUrl.value.trim()) {
    updateStatus('WebSocket URL cannot be empty.', true);
    return;
  }

  updateStatus(`Connecting to ${wsUrl.value}...`);
  websocket = new WebSocket(wsUrl.value.trim());

  websocket.onopen = () => {
    updateStatus(`Connected to ${wsUrl.value}`);
    connectBtnDisabled.value = true;
    disconnectBtnDisabled.value = false;
    wsUrlDisabled.value = true;
    validateJsonInput();
  };

  websocket.onmessage = (event) => {
    let messageData = event.data;
    if (messageData instanceof Blob) {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const jsonStr = reader.result as string;
          const parsedJson = JSON.parse(jsonStr);
          messageData = JSON.stringify(parsedJson, null, 2);
        } catch (e) {
          messageData = reader.result as string;
        }
        logReceivedMessage(messageData);
      };
      reader.readAsText(messageData);
      return;
    }
    try {
      const parsedJson = JSON.parse(messageData);
      messageData = JSON.stringify(parsedJson, null, 2);
    } catch (e) {
      // Not JSON
    }
    logReceivedMessage(messageData);
  };

  websocket.onerror = (error) => {
    updateStatus(`WebSocket Error: ${(error as any).message || 'Unknown error. Check console.'}`, true);
    console.error('WebSocket Error:', error);
    if (websocket?.readyState !== WebSocket.OPEN) {
      disconnectWebSocket(false);
    }
  };

  websocket.onclose = (event) => {
    updateStatus(`Disconnected. Code: ${event.code}, Reason: ${event.reason || 'No reason given'}`);
    connectBtnDisabled.value = false;
    disconnectBtnDisabled.value = true;
    sendBtnDisabled.value = true;
    wsUrlDisabled.value = false;
    websocket = null;
  };
};

const disconnectWebSocket = (notifyServer = true) => {
  if (websocket) {
    if (notifyServer && websocket.readyState === WebSocket.OPEN) {
      websocket.close(1000, "Client initiated disconnect");
    } else if (!notifyServer && websocket.readyState !== WebSocket.CLOSED && websocket.readyState !== WebSocket.CLOSING) {
      websocket.close();
    }
    updateStatus('Disconnected');
  } else {
    updateStatus('Already disconnected or never connected.');
  }
  connectBtnDisabled.value = false;
  disconnectBtnDisabled.value = true;
  sendBtnDisabled.value = true;
  wsUrlDisabled.value = false;
  jsonValidationStatus.value = '';
  jsonValidationClass.value = '';
};

const sendMessage = () => {
  if (!websocket || websocket.readyState !== WebSocket.OPEN) {
    updateStatus('Not connected to WebSocket server.', true);
    return;
  }

  const message = messageToSend.value.trim();
  if (!message) {
    updateStatus('Cannot send an empty message.', true);
    return;
  }

  websocket.send(message);
  const timestamp = new Date().toLocaleTimeString();
  
  let loggedMessage = message;
  try {
    const parsed = JSON.parse(message);
    loggedMessage = JSON.stringify(parsed, null, 2);
  } catch(e) {
    // not json, log as is
  }
  receivedMessages.value += `[${timestamp}] Sent: ${loggedMessage}\n\n`;
};

const validateJson = (jsonString: string) => {
  if (!jsonString.trim()) {
    return { valid: false, message: '输入为空' };
  }
  try {
    JSON.parse(jsonString);
    return { valid: true, message: '格式正确' };
  } catch (e) {
    return { valid: false, message: (e as Error).message };
  }
};

const formatJson = () => {
  const jsonString = messageToSend.value.trim();
  if (!jsonString) {
    updateStatus('无内容可格式化', true);
    return;
  }
  try {
    const parsedJson = JSON.parse(jsonString);
    messageToSend.value = JSON.stringify(parsedJson, null, 4);
    updateJsonValidationStatus(true, '格式化成功');
  } catch (e) {
    updateStatus(`无法格式化: ${(e as Error).message}`, true);
  }
};

const updateJsonValidationStatus = (isValid: boolean, message: string) => {
  jsonValidationStatus.value = message;
  if (isValid) {
    jsonValidationClass.value = 'json-valid';
  } else {
    jsonValidationClass.value = 'json-invalid';
  }
};

const validateJsonInput = () => {
  const result = validateJson(messageToSend.value);
  updateJsonValidationStatus(result.valid, result.message);
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    sendBtnDisabled.value = !result.valid;
  }
};

const clearLog = () => {
  receivedMessages.value = '';
};

const escapeHtmlForHighlight = (str: string) => 
    str.replace(/&/g, '&amp;')
       .replace(/</g, '&lt;')
       .replace(/>/g, '&gt;')
       .replace(/"/g, '&quot;')
       .replace(/'/g, '&#039;');

const highlightedInput = computed(() => {
    const code = messageToSend.value;
    if (jsonValidationClass.value === 'json-valid') {
        try {
            const highlighted = hljs.highlight(code, { language: 'json', ignoreIllegals: true }).value;
            return `${highlighted}<br>`;
        } catch (e) {
            return `${escapeHtmlForHighlight(code)}<br>`;
        }
    }
    return `${escapeHtmlForHighlight(code)}<br>`;
});

const syncScroll = (event: Event) => {
  const editor = event.target as HTMLElement;
  const highlighter = document.getElementById('highlighting');
  if (highlighter) {
    highlighter.scrollTop = editor.scrollTop;
    highlighter.scrollLeft = editor.scrollLeft;
  }
};

const highlightedMessages = computed(() => {
    const escapeHtml = (str: string) => str.replace(/</g, '&lt;').replace(/>/g, '&gt;');

    return receivedMessages.value
        .split('\n\n')
        .filter(line => line.trim())
        .map(line => {
            const prefixMatch = line.match(/^(.*?] (?:Sent|Received): )/);
            if (!prefixMatch) {
                return `<div class="log-line">${escapeHtml(line)}</div>`;
            }
            const prefix = prefixMatch[1];
            const content = line.substring(prefix.length);
            
            try {
                JSON.parse(content); // Just to validate
                const highlighted = hljs.highlight(content, { language: 'json' }).value;
                return `<div class="log-line">${escapeHtml(prefix)}<pre class="code-block"><code class="language-json">${highlighted}</code></pre></div>`;
            } catch (e) {
                return `<div class="log-line">${escapeHtml(prefix)}<pre class="code-block"><code>${escapeHtml(content)}</code></pre></div>`;
            }
        })
        .join('');
});

watch(receivedMessages, async () => {
    await nextTick();
    const container = document.getElementById('receivedMessages');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
});

const handleInsertCode = (code: string) => {
  try {
    // Try to parse as JSON and format it
    const parsed = JSON.parse(code);
    messageToSend.value = JSON.stringify(parsed, null, 2);
  } catch (e) {
    // If not valid JSON, insert as plain text
    messageToSend.value = code;
  }
  // Validate the inserted content
  validateJsonInput();
  // Focus on the textarea
  nextTick(() => {
    const textarea = document.getElementById('messageToSend') as HTMLTextAreaElement;
    if (textarea) {
      textarea.focus();
    }
  });
};

const handleDockMessage = (message: string) => {
  // Set the message content from Dock
  messageToSend.value = message;
  // Validate the content
  validateJsonInput();
  // Auto-send the message if connected and valid
  if (websocket && websocket.readyState === WebSocket.OPEN && !sendBtnDisabled.value) {
    sendMessage();
  }
};

onMounted(() => {
  // Initial validation
  validateJsonInput();
});

</script>

<template>
  <div class="app-container">
    <Sidebar @insert-code="handleInsertCode" />
    <div class="container">
    <h1><i class="fas fa-plug"></i> WDP Debug Tool</h1>

    <div class="connection-section">
      <h2><i class="fas fa-network-wired"></i> Connection</h2>
      <div class="input-group">
        <label for="wsUrl">WebSocket URL:</label>
        <input type="text" id="wsUrl" v-model="wsUrl" :disabled="wsUrlDisabled">
      </div>
      <div class="button-group">
        <button id="connectBtn" @click="connectWebSocket" :disabled="connectBtnDisabled"><i class="fas fa-link"></i> Connect</button>
        <button id="disconnectBtn" @click="() => disconnectWebSocket()" :disabled="disconnectBtnDisabled"><i class="fas fa-unlink"></i> Disconnect</button>
      </div>
      <p class="status-display">Status: <span id="status">{{ status }}</span></p>
    </div>

    <div class="message-section">
      <div class="send-message">
        <h2><i class="fas fa-paper-plane"></i> Send Message (JSON)</h2>
        <div class="textarea-container">
          <pre id="highlighting" aria-hidden="true"><code class="language-json" v-html="highlightedInput"></code></pre>
          <textarea id="messageToSend" rows="5" placeholder="Enter JSON message here..." v-model="messageToSend" @input="validateJsonInput" @scroll="syncScroll" spellcheck="false"></textarea>
          <div id="jsonValidationStatus" class="json-validation-status" :class="jsonValidationClass">{{ jsonValidationStatus }}</div>
        </div>
        <div class="button-group">
          <button id="formatJsonBtn" @click="formatJson"><i class="fas fa-indent"></i> 格式化</button>
          <button id="sendBtn" @click="sendMessage" :disabled="sendBtnDisabled"><i class="fas fa-share"></i> Send</button>
        </div>
      </div>

      <div class="received-messages">
        <h2><i class="fas fa-inbox"></i> Received Messages</h2>
        <div id="receivedMessages" class="log-display" v-html="highlightedMessages"></div>
        <button id="clearLogBtn" @click="clearLog"><i class="fas fa-trash"></i> Clear Log</button>
      </div>
    </div>
    </div>
    <Dock @send-message="handleDockMessage" />
  </div>
</template>

<style>
/* Modern WebSocket Client Styles */
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

:root {
    --primary-color: #4a6fa5;
    --primary-hover: #3a5a8c;
    --secondary-color: #e63946;
    --secondary-hover: #c1121f;
    --background-color: #f8f9fa;
    --card-bg: #ffffff;
    --text-color: #2b2d42;
    --border-color: #dee2e6;
    --success-color: #2a9d8f;
    --info-color: #457b9d;
    --border-radius: 8px;
    --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    --transition: all 0.3s ease;
}

html, body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
    height: 100%;
    width: 100%;
}

.container {
    flex: 1;
    max-width: none;
    margin: 0;
    padding: 20px;
    overflow-y: auto;
}

.input-group {
    margin-bottom: 15px;
}

.button-group {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}

.status-display {
    margin-top: 15px;
    font-size: 1.1rem;
}

i {
    margin-right: 5px;
}

h1 {
    text-align: center;
    color: var(--primary-color);
    margin-bottom: 30px;
    font-size: 2.5rem;
    font-weight: 600;
}

h2 {
    color: var(--primary-color);
    font-size: 1.5rem;
    margin-bottom: 15px;
    font-weight: 500;
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 8px;
}

.connection-section, .message-section {
    background-color: var(--card-bg);
    padding: 25px;
    margin-bottom: 30px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    transition: var(--transition);
}

.connection-section:hover, .message-section:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

label {
    display: inline-block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--text-color);
}

input[type="text"] {
    width: calc(100% - 22px);
    padding: 12px;
    margin-bottom: 15px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-sizing: border-box;
    transition: var(--transition);
    font-size: 1rem;
}

input[type="text"]:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.2);
}

button {
    padding: 12px 20px;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    margin-right: 10px;
    margin-bottom: 10px;
    font-weight: 500;
    transition: var(--transition);
    font-size: 1rem;
}

button:hover {
    background-color: var(--primary-hover);
    transform: translateY(-2px);
}

button:active {
    transform: translateY(0);
}

button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
    transform: none;
}

#disconnectBtn {
    background-color: var(--secondary-color);
}

#disconnectBtn:hover {
    background-color: var(--secondary-hover);
}

#clearLogBtn {
    background-color: var(--info-color);
}

#clearLogBtn:hover {
    background-color: #3d6990;
}

textarea {
    width: 100%;
    padding: 12px;
    margin-bottom: 0;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-sizing: border-box;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
    resize: vertical;
    transition: var(--transition);
}

textarea:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 3px rgba(74, 111, 165, 0.2);
}

.textarea-container {
    position: relative;
    margin-bottom: 15px;
    width: 100%;
}

#highlighting,
#messageToSend {
    margin: 0;
    padding: 12px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-sizing: border-box;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
    width: 100%;
    height: 120px;
    overflow: auto;
    white-space: pre;
    word-wrap: normal;
}

#messageToSend {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    color: transparent;
    background: transparent;
    caret-color: var(--text-color);
    resize: vertical;
}

#messageToSend:focus {
  outline: none;
}

#highlighting {
    position: relative;
    z-index: 1;
    pointer-events: none;
    overflow: hidden;
}

#highlighting code {
    display: block;
}

.json-validation-status {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    opacity: 0.9;
}

.json-valid {
    background-color: rgba(42, 157, 143, 0.2);
    color: var(--success-color);
}

.json-invalid {
    background-color: rgba(230, 57, 70, 0.2);
    color: var(--secondary-color);
}

#status {
    font-weight: bold;
}

.log-display {
    background-color: #282c34;
    color: #abb2bf;
    padding: 15px;
    border-radius: var(--border-radius);
    height: 300px;
    overflow-y: auto;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.9rem;
    border: 1px solid var(--border-color);
}

.log-line {
    margin-bottom: 10px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.log-line:last-child {
    margin-bottom: 0;
}

.code-block {
    margin: 0;
    padding: 0;
    background: transparent;
    white-space: pre-wrap;
}

.code-block .hljs {
  padding: 0;
  background: transparent;
}
</style>
