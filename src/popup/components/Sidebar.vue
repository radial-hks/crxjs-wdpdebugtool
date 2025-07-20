<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }" :style="{ width: sidebarWidth + 'px' }">
    <div class="sidebar-header">
      <button @click="toggleCollapse" class="collapse-btn">
        {{ isCollapsed ? '▶' : '◀' }}
      </button>
      <input v-if="!isCollapsed" type="file" @change="loadFile" accept=".md, .markdown" class="file-input" />
    </div>
    <div v-if="!isCollapsed" class="markdown-content" v-html="renderedMarkdown" @click="handleContentClick"></div>
    <div v-if="!isCollapsed" class="resize-handle" @mousedown="startResize"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';

const renderedMarkdown = ref('');
const isCollapsed = ref(false);
const sidebarWidth = ref(300);
const isResizing = ref(false);
const emit = defineEmits(['insert-code']);

const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlighted = hljs.highlight(str, { language: lang, ignoreIllegals: true }).value;
        const copyBtnId = 'copy-btn-' + Math.random().toString(36).substr(2, 9);
        return `<div class="code-block-container">
          <pre class="hljs"><code>${highlighted}</code></pre>
          <button class="copy-btn" data-code="${encodeURIComponent(str)}" data-lang="${lang}">
            📋 Copy to Input
          </button>
        </div>`;
      } catch (__) {}
    }
    return `<div class="code-block-container">
      <pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>
      <button class="copy-btn" data-code="${encodeURIComponent(str)}">
        📋 Copy to Input
      </button>
    </div>`;
  }
});

const loadFile = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      renderedMarkdown.value = md.render(e.target.result);
    };
    reader.readAsText(file);
  }
};

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
  if (isCollapsed.value) {
    sidebarWidth.value = 40; // Collapsed width
  } else {
    sidebarWidth.value = 300; // Default width
  }
};

const startResize = (event) => {
  isResizing.value = true;
  const startX = event.clientX;
  const startWidth = sidebarWidth.value;

  const handleMouseMove = (e) => {
    if (isResizing.value) {
      const newWidth = startWidth + (e.clientX - startX);
      if (newWidth >= 200 && newWidth <= 600) {
        sidebarWidth.value = newWidth;
      }
    }
  };

  const handleMouseUp = () => {
    isResizing.value = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
};

const handleContentClick = (event) => {
  let target = event.target;
  
  // Handle copy button clicks using event delegation
  if (target.classList.contains('copy-btn')) {
    event.stopPropagation();
    const encodedCode = target.getAttribute('data-code');
    const code = decodeURIComponent(encodedCode);
    emit('insert-code', code);
    return;
  }
  
  // If the click is inside a <code> block, travel up to find the parent <pre>
  if (target.tagName === 'CODE' && target.parentElement.tagName === 'PRE') {
    const code = target.textContent;
    emit('insert-code', code);
  }
};


onMounted(async () => {
  try {
    // Load a default/sample file on initial mount
    const response = await fetch('/markdown/sample.md');
    if(response.ok){
      const markdownText = await response.text();
      renderedMarkdown.value = md.render(markdownText);
    } else {
      renderedMarkdown.value = 'Sample file not found. Please select a local file.';
    }
  } catch (error) {
    console.error('Error loading or parsing markdown:', error);
    renderedMarkdown.value = 'Error loading file. Please select a local file.';
  }
});
</script>

<style scoped>
.sidebar {
  position: relative;
  padding: 10px;
  border-right: 1px solid #ccc;
  height: 100vh;
  overflow-y: auto;
  transition: width 0.3s ease;
  min-width: 40px;
}

.sidebar.collapsed {
  width: 40px !important;
  padding: 5px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.collapse-btn {
  background: #007acc;
  color: white;
  border: none;
  padding: 5px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  min-width: 24px;
}

.collapse-btn:hover {
  background: #005a9e;
}

.file-input {
  flex: 1;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 3px;
}

.markdown-content {
  flex: 1;
  overflow-y: auto;
}

.resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  background: #ccc;
  cursor: ew-resize;
  opacity: 0;
  transition: opacity 0.2s;
}

.sidebar:hover .resize-handle {
  opacity: 1;
}

.resize-handle:hover {
  background: #007acc;
}

.sidebar :deep(.code-block-container) {
  position: relative;
  margin: 10px 0;
}

.sidebar :deep(pre) {
  cursor: pointer;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 5px;
  margin: 0;
}

.sidebar :deep(pre:hover) {
  background-color: #eee;
}

.sidebar :deep(.copy-btn) {
  position: absolute;
  top: 5px;
  right: 5px;
  background: #007acc;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.sidebar :deep(.copy-btn:hover) {
  opacity: 1;
  background: #005a9e;
}

.sidebar :deep(.code-block-container:hover .copy-btn) {
  opacity: 1;
}
</style>