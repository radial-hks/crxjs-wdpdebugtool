<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }" :style="{ width: sidebarWidth + 'px' }">
    <div class="sidebar-header">
      <button @click="toggleCollapse" class="collapse-btn">
        {{ isCollapsed ? '▶' : '◀' }}
      </button>
      <!-- 只在非折叠状态显示文件输入 -->
      <input v-if="!isCollapsed" type="file" @change="loadFile" accept=".md, .markdown" class="file-input" />
    </div>
    
    <!-- 只在非折叠状态显示标签导航 -->
    <div v-if="!isCollapsed && tabs.length > 0" class="tab-navigation">
      <div class="tab-list">
        <div 
          v-for="tab in tabs" 
          :key="tab.id"
          class="tab-item"
          :class="{ active: tab.id === activeTabId }"
          @click="switchTab(tab.id)"
        >
          <span class="tab-title">{{ tab.title }}</span>
          <button 
            v-if="tabs.length > 1"
            class="tab-close"
            @click.stop="closeTab(tab.id)"
          >
            ×
          </button>
        </div>
      </div>
    </div>
    
    <!-- 只在非折叠状态显示内容 -->
    <div v-if="!isCollapsed" class="markdown-content" v-html="activeTabContent" @click="handleContentClick"></div>
    <div v-if="!isCollapsed" class="resize-handle" @mousedown="startResize"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';

// Tab management
const tabs = ref([]);
const activeTabId = ref(null);
let tabIdCounter = 0;

// 修改默认状态为折叠
const isCollapsed = ref(true);
const sidebarWidth = ref(40); // 默认为折叠宽度
const isResizing = ref(false);
const emit = defineEmits(['insert-code']);

// Computed property for active tab content
const activeTabContent = computed(() => {
  const activeTab = tabs.value.find(tab => tab.id === activeTabId.value);
  return activeTab ? activeTab.content : '';
});

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

// Tab management methods
const addTab = (title, content) => {
  const newTab = {
    id: ++tabIdCounter,
    title: title,
    content: md.render(content)
  };
  tabs.value.push(newTab);
  activeTabId.value = newTab.id;
  return newTab.id;
};

const switchTab = (tabId) => {
  activeTabId.value = tabId;
};

const closeTab = (tabId) => {
  const tabIndex = tabs.value.findIndex(tab => tab.id === tabId);
  if (tabIndex === -1) return;
  
  tabs.value.splice(tabIndex, 1);
  
  // If we closed the active tab, switch to another tab
  if (activeTabId.value === tabId) {
    if (tabs.value.length > 0) {
      // Switch to the previous tab or the first tab
      const newActiveIndex = Math.max(0, tabIndex - 1);
      activeTabId.value = tabs.value[newActiveIndex].id;
    } else {
      activeTabId.value = null;
    }
  }
};

const loadFile = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const fileName = file.name.replace(/\.[^/.]+$/, ""); // Remove file extension
      addTab(fileName, e.target.result);
    };
    reader.readAsText(file);
  }
  // Clear the input so the same file can be loaded again
  event.target.value = '';
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
    const response = await fetch('/markdown/Normative.md');
    if(response.ok){
      const markdownText = await response.text();
      addTab('Default', markdownText);
    } else {
      addTab('Welcome', 'Sample file not found. Please select a local file.');
    }
  } catch (error) {
    console.error('Error loading or parsing markdown:', error);
    addTab('Error', 'Error loading file. Please select a local file.');
  }
});
</script>

<style scoped>
.sidebar {
  position: relative;
  padding: 10px;
  border-right: 1px solid var(--border-color);
  background-color: var(--card-bg);
  height: 100vh;
  overflow-y: auto;
  transition: width 0.3s ease;
  min-width: 40px;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 0 !important;
  padding: 0;
  background-color: transparent;
  border-right: none;
  overflow: visible;
}

.sidebar.collapsed .sidebar-header {
  position: absolute;
  top: 20px;
  left: 10px;
  z-index: 1000;
  justify-content: center;
  gap: 0;
  background-color: var(--card-bg);
  border-radius: 50%;
  margin: 0;
  padding: 0;
  width: 40px;
  height: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--border-color);
}

.sidebar.collapsed .sidebar-toggle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 0 5px;
}

/* 在折叠状态下居中显示按钮 */
.sidebar.collapsed .sidebar-header {
  justify-content: center;
  gap: 0;
}

.collapse-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 5px 8px;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 12px;
  min-width: 24px;
  transition: var(--transition);
}

.collapse-btn:hover {
  background: var(--primary-hover);
}

.file-input {
  flex: 1;
  padding: 5px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 12px;
}

.markdown-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.resize-handle {
  position: absolute;
  top: 0;
  right: -2px;
  width: 4px;
  height: 100%;
  background: transparent;
  cursor: ew-resize;
  transition: background-color 0.2s;
}

.sidebar:hover .resize-handle {
  background-color: var(--primary-color);
}

.tab-navigation {
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 10px;
}

.tab-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 0 5px;
}

.tab-item {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  font-size: 12px;
  max-width: 120px;
  transition: var(--transition);
}

.tab-item:hover {
  background: #e9ecef;
}

.tab-item.active {
  background: var(--card-bg);
  border-color: var(--primary-color);
  color: var(--primary-color);
  font-weight: 500;
}

.tab-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 4px;
}

.tab-close {
  background: none;
  border: none;
  color: var(--text-color-light);
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-left: 4px;
  transition: var(--transition);
}

.tab-close:hover {
  background: var(--secondary-color);
  color: white;
}

.sidebar :deep(.code-block-container) {
  position: relative;
  margin: 1em 0;
}

.sidebar :deep(pre) {
  cursor: pointer;
  background-color: #f5f5f5;
  padding: 1em;
  border-radius: var(--border-radius);
  margin: 0;
  border: 1px solid var(--border-color);
  white-space: pre-wrap;
  word-break: break-all;
}

.sidebar :deep(pre:hover) {
  background-color: #e9ecef;
  border-color: var(--primary-color);
}

.sidebar :deep(.copy-btn) {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 11px;
  opacity: 0;
  transition: opacity 0.2s;
}

.sidebar :deep(.copy-btn:hover) {
  background: var(--primary-hover);
}

.sidebar :deep(.code-block-container:hover .copy-btn) {
  opacity: 1;
}
</style>