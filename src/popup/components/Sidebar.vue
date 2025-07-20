<template>
  <div class="sidebar">
    <input type="file" @change="loadFile" accept=".md, .markdown" />
    <div v-html="renderedMarkdown" @click="handleContentClick"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';

const renderedMarkdown = ref('');
const emit = defineEmits(['insert-code']);

const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' + hljs.highlight(str, { language: lang, ignoreIllegals: true }).value + '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
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

const handleContentClick = (event) => {
  let target = event.target;
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
  width: 300px;
  padding: 10px;
  border-right: 1px solid #ccc;
  height: 100vh;
  overflow-y: auto;
}

.sidebar :deep(pre) {
  cursor: pointer;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 5px;
}

.sidebar :deep(pre:hover) {
  background-color: #eee;
}
</style>