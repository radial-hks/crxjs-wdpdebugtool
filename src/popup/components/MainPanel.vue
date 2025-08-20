<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

const props = defineProps<{
  initialMessage: string;
}>();

const emit = defineEmits(['message-sent']);

const isConnectionOpen = ref(false);
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
  emit('message-sent', message);
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

watch(() => props.initialMessage, (newVal) => {
  if (newVal) {
    setMessage(newVal);
  }
});

const setMessage = (code: string) => {
  try {
    const parsed = JSON.parse(code);
    messageToSend.value = JSON.stringify(parsed, null, 2);
  } catch (e) {
    messageToSend.value = code;
  }
  validateJsonInput();
  nextTick(() => {
    const textarea = document.getElementById('messageToSend') as HTMLTextAreaElement;
    if (textarea) {
      textarea.focus();
    }
  });
};

const setMessageAndSend = (message: string) => {
  setMessage(message);
  if (websocket && websocket.readyState === WebSocket.OPEN && !sendBtnDisabled.value) {
    sendMessage();
  }
};

defineExpose({
  setMessage,
  setMessageAndSend,
});

onMounted(() => {
  validateJsonInput();
});

</script>

<template>
  <div class="main-panel-container">
    <h1><i class="fas fa-plug"></i> WDP Debug Tool</h1>

    <div class="connection-section">
      <h2 @click="isConnectionOpen = !isConnectionOpen" class="collapsible-header">
        <i class="fas fa-network-wired"></i> Connection
        <i class="fas fa-chevron-down" :class="{ 'rotated': !isConnectionOpen }"></i>
      </h2>
      <div v-if="isConnectionOpen" class="collapsible-content">
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
</template>

<style scoped>
.main-panel-container {
    padding: 20px;
    overflow-y: auto;
    background-color: var(--background-color);
    color: var(--text-color);
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.collapsible-header {
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.collapsible-header .fa-chevron-down {
    transition: transform 0.3s ease;
}

.collapsible-header .fa-chevron-down.rotated {
    transform: rotate(180deg);
}

.message-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
}

.received-messages {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
}

.log-display {
    flex: 1;
    overflow-y: auto;
    background-color: #282c34;
    color: #abb2bf;
    padding: 15px;
    border-radius: var(--border-radius);
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.9rem;
    border: 1px solid var(--border-color);
}
</style>
