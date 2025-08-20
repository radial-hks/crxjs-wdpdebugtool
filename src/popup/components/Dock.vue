<template>
  <div class="dock-container" :class="{ collapsed: isCollapsed }">
    <div class="dock-header">
      <h3 v-if="!isCollapsed">快捷测试</h3>
      <button class="dock-toggle" @click="toggleDock">
        {{ isCollapsed ? '◀' : '▶' }}
      </button>
    </div>
    
    <div v-if="!isCollapsed" class="dock-content">
      <!-- Loading state -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载配置中...</p>
      </div>
      
      <!-- Main content -->
      <template v-else>
        <!-- Category Tabs -->
        <div class="category-tabs">
          <button 
            v-for="category in categories" 
            :key="category.id"
            class="category-tab"
            :class="{ active: activeCategory === category.id }"
            @click="switchCategory(category.id)"
          >
            {{ category.name }}
          </button>
        </div>
        
        <!-- Button List -->
        <div class="button-list">
          <button 
            v-for="preset in filteredPresets" 
            :key="preset.id"
            class="dock-button"
            @click="sendPreset(preset)"
            :title="preset.description"
          >
            <div class="button-icon">{{ preset.icon }}</div>
            <div class="button-label">{{ preset.label }}</div>
          </button>
        </div>
        
        <div class="dock-footer">
          <button class="config-button" @click="toggleConfig">
            ⚙️ 配置
          </button>
        </div>
      </template>
    </div>
    
    <!-- Configuration Panel -->
    <div v-if="showConfig" class="config-overlay" @click="closeConfig">
      <div class="config-panel" @click.stop>
        <div class="config-header">
          <h4>按钮配置</h4>
          <button class="close-button" @click="closeConfig">×</button>
        </div>
        
        <!-- Import/Export Section -->
        <div class="import-export-section">
          <div class="section-title">导入/导出</div>
          <div class="import-export-buttons">
            <input 
              ref="fileInput" 
              type="file" 
              accept=".json" 
              @change="importConfig" 
              style="display: none"
            />
            <button @click="$refs.fileInput.click()" class="import-button">📁 导入JSON</button>
            <button @click="exportConfig" class="export-button">💾 导出JSON</button>
          </div>
        </div>
        
        <!-- Category Management -->
        <div class="category-management">
          <div class="section-title">分类管理</div>
          <div class="category-form">
            <input v-model="newCategory.name" placeholder="分类名称" class="config-input" />
            <button @click="addCategory" class="add-category-button">添加分类</button>
          </div>
          <div class="category-list">
            <div v-for="category in categories" :key="category.id" class="category-item">
              <span>{{ category.name }}</span>
              <button v-if="category.id !== 'default'" @click="removeCategory(category.id)" class="remove-button">删除</button>
            </div>
          </div>
        </div>
        
        <!-- Add Preset Form -->
        <div class="preset-form">
          <div class="section-title">添加按钮</div>
          <select v-model="newPreset.categoryId" class="config-select">
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <input v-model="newPreset.label" placeholder="按钮标签" class="config-input" />
          <input v-model="newPreset.icon" placeholder="图标" class="config-input" />
          <textarea v-model="newPreset.content" placeholder="JSON内容" class="config-textarea"></textarea>
          <input v-model="newPreset.description" placeholder="描述" class="config-input" />
          <div class="config-buttons">
            <button @click="addPreset" class="add-button">添加</button>
            <button @click="resetConfig" class="reset-button">重置</button>
          </div>
        </div>
        
        <!-- Preset List -->
        <div class="preset-management">
          <div class="section-title">按钮管理</div>
          <div class="preset-list">
            <div v-for="preset in presets" :key="preset.id" class="preset-item">
              <div class="preset-info">
                <span class="preset-category">[{{ getCategoryName(preset.categoryId) }}]</span>
                <span class="preset-label">{{ preset.label }}</span>
              </div>
              <button @click="removePreset(preset.id)" class="remove-button">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const emit = defineEmits(['send-message']);

const isCollapsed = ref(false);
const showConfig = ref(false);
const activeCategory = ref('default');
const isLoading = ref(true);

// Default fallback data (used when external config fails to load)
const fallbackCategories = [
  { id: 'default', name: '默认' },
  { id: 'page', name: '页面操作' },
  { id: 'element', name: '元素操作' },
  { id: 'script', name: '脚本执行' }
];

const fallbackPresets = [
  {
    id: 1,
    categoryId: 'page',
    label: '获取页面信息',
    icon: '📄',
    content: JSON.stringify({
      "action": "getPageInfo",
      "params": {}
    }, null, 2),
    description: '获取当前页面的基本信息'
  }
];

const categories = ref([]);
const presets = ref([]);
const newPreset = ref({
  categoryId: 'default',
  label: '',
  icon: '🔧',
  content: '',
  description: ''
});
const newCategory = ref({
  name: ''
});

let nextId = 5;
let nextCategoryId = 5;

// Computed properties
const filteredPresets = computed(() => {
  return presets.value.filter(preset => preset.categoryId === activeCategory.value);
});

const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId);
  return category ? category.name : '未知分类';
};

const toggleDock = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleConfig = () => {
  showConfig.value = !showConfig.value;
};

const closeConfig = () => {
  showConfig.value = false;
};

const sendPreset = (preset) => {
  emit('send-message', preset.content);
};

// Category management
const switchCategory = (categoryId) => {
  activeCategory.value = categoryId;
};

const addCategory = () => {
  if (newCategory.value.name.trim()) {
    const categoryId = `custom_${nextCategoryId++}`;
    categories.value.push({
      id: categoryId,
      name: newCategory.value.name.trim()
    });
    saveCategories();
    newCategory.value.name = '';
  }
};

const removeCategory = (categoryId) => {
  if (categoryId === 'default') {
    alert('默认分类不能删除');
    return;
  }
  
  if (confirm('确定要删除此分类吗？该分类下的所有预设也将被删除。')) {
    categories.value = categories.value.filter(c => c.id !== categoryId);
    presets.value = presets.value.filter(p => p.categoryId !== categoryId);
    
    if (activeCategory.value === categoryId) {
      activeCategory.value = 'default';
    }
    
    saveCategories();
    savePresets();
  }
};

// Preset management
const addPreset = () => {
  if (!newPreset.value.label || !newPreset.value.content) {
    alert('请填写标签和内容');
    return;
  }
  
  try {
    // Validate JSON
    JSON.parse(newPreset.value.content);
    
    const preset = {
      id: nextId++,
      categoryId: newPreset.value.categoryId,
      label: newPreset.value.label,
      icon: newPreset.value.icon || '🔧',
      content: newPreset.value.content,
      description: newPreset.value.description
    };
    
    presets.value.push(preset);
    savePresets();
    
    // Reset form
    newPreset.value = {
      categoryId: 'default',
      label: '',
      icon: '🔧',
      content: '',
      description: ''
    };
  } catch (e) {
    alert('JSON格式错误: ' + e.message);
  }
};

const removePreset = (id) => {
  const index = presets.value.findIndex(p => p.id === id);
  if (index > -1) {
    presets.value.splice(index, 1);
    savePresets();
  }
};

const resetConfig = () => {
  if (confirm('确定要重置所有预设吗？这将删除所有自定义预设和分类。')) {
    presets.value = [...defaultPresets];
    categories.value = [...defaultCategories];
    activeCategory.value = 'default';
    savePresets();
    saveCategories();
  }
};

// JSON Import/Export
const exportConfig = () => {
  const config = {
    categories: categories.value,
    presets: presets.value,
    version: '1.0'
  };
  
  const dataStr = JSON.stringify(config, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = 'dock-config.json';
  link.click();
  
  URL.revokeObjectURL(url);
};

const importConfig = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const config = JSON.parse(e.target.result);
      
      if (config.categories && config.presets) {
        if (confirm('确定要导入配置吗？这将覆盖当前所有配置。')) {
          categories.value = config.categories || [...defaultCategories];
          presets.value = config.presets || [...defaultPresets];
          activeCategory.value = 'default';
          
          // Update next IDs
          nextId = Math.max(...presets.value.map(p => p.id), 4) + 1;
          nextCategoryId = Math.max(
            ...categories.value
              .filter(c => c.id.startsWith('custom_'))
              .map(c => parseInt(c.id.replace('custom_', '')) || 0),
            4
          ) + 1;
          
          saveCategories();
          savePresets();
          
          alert('配置导入成功！');
        }
      } else {
        alert('配置文件格式错误');
      }
    } catch (e) {
      alert('配置文件解析失败：' + e.message);
    }
  };
  reader.readAsText(file);
  
  // Reset file input
  event.target.value = '';
};

// Storage functions
const savePresets = () => {
  localStorage.setItem('dock-presets', JSON.stringify(presets.value));
};

const loadPresets = () => {
  const saved = localStorage.getItem('dock-presets');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse saved presets:', e);
    }
  }
  return null;
};

const saveCategories = () => {
  localStorage.setItem('dock-categories', JSON.stringify(categories.value));
};

const loadCategories = () => {
  const saved = localStorage.getItem('dock-categories');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse saved categories:', e);
    }
  }
  return null;
};

// Load external configuration
const loadExternalConfig = async () => {
  try {
    const response = await fetch('/dock-config.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const config = await response.json();
    
    // Load categories
    if (config.categories && Array.isArray(config.categories)) {
      categories.value = [...config.categories];
    } else {
      categories.value = [...fallbackCategories];
    }
    
    // Load presets
    if (config.presets && Array.isArray(config.presets)) {
      presets.value = config.presets.map(preset => ({
        ...preset,
        content: typeof preset.content === 'string' ? preset.content : JSON.stringify(preset.content, null, 2)
      }));
    } else {
      presets.value = [...fallbackPresets];
    }
    
    console.log('External dock configuration loaded successfully');
  } catch (error) {
    console.warn('Failed to load external dock configuration, using fallback:', error);
    categories.value = [...fallbackCategories];
    presets.value = [...fallbackPresets];
  } finally {
    isLoading.value = false;
  }
};

// Load data from localStorage on mount
onMounted(async () => {
  // First load external config
  await loadExternalConfig();
  
  // Then try to load from localStorage (this will override external config if exists)
  const savedCategories = loadCategories();
  const savedPresets = loadPresets();
  
  // If localStorage has data, use it; otherwise keep external config
  if (savedCategories && savedCategories.length > 0) {
    categories.value = savedCategories;
  }
  if (savedPresets && savedPresets.length > 0) {
    presets.value = savedPresets;
  }
  
  // Update nextId to avoid conflicts
  if (presets.value.length > 0) {
    const maxId = Math.max(...presets.value.map(p => p.id), 0);
    nextId = maxId + 1;
  }
});
</script>

<style scoped>
.dock-container {
  width: 280px;
  height: 100vh;
  background-color: var(--card-bg);
  color: var(--text-color);
  padding: 10px;
  border-left: 1px solid var(--border-color);
  z-index: 10;
  transition: all 0.3s ease;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.dock-container.collapsed {
  width: 40px;
  padding: 10px 5px;
}

.dock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 0 5px;
  flex-shrink: 0;
}

.dock-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  transition: opacity 0.3s ease;
}

.dock-toggle {
  background: var(--primary-color);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: var(--border-radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: var(--transition);
  flex-shrink: 0;
}

.dock-toggle:hover {
  background: var(--primary-hover);
}

.dock-content {
  flex: 1;
  overflow-y: auto;
  transition: opacity 0.3s ease;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}

.category-tab {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 4px 10px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 12px;
  transition: var(--transition);
  white-space: nowrap;
}

.category-tab:hover {
  background: #e9ecef;
  border-color: var(--primary-color);
}

.category-tab.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
  font-weight: 500;
}

.button-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dock-button {
  background: #f8f9fa;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 10px;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  text-align: left;
}

.dock-button:hover {
  background: #e9ecef;
  transform: translateY(-1px);
  box-shadow: var(--box-shadow);
}

.button-icon {
  font-size: 16px;
  margin-right: 8px;
}

.button-label {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-color);
}

.dock-footer {
  padding: 10px 0;
  border-top: 1px solid var(--border-color);
  margin-top: 12px;
}

.config-button {
  width: 100%;
  padding: 8px 12px;
  background: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: var(--transition);
}

.config-button:hover {
  background: #e9ecef;
  border-color: var(--primary-color);
}

.config-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.config-panel {
  background: var(--card-bg);
  border-radius: var(--border-radius);
  padding: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.config-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
}

.close-button {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: var(--transition);
}

.close-button:hover {
  background: var(--secondary-color);
  color: white;
  border-color: var(--secondary-color);
}

.import-export-section,
.category-management,
.preset-form,
.preset-management {
  margin-bottom: 20px;
  background: var(--background-color);
  border-radius: var(--border-radius);
  padding: 12px;
  border: 1px solid var(--border-color);
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 12px;
}

.import-export-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.import-button,
.export-button {
  background: var(--info-color);
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: var(--transition);
}

.import-button:hover,
.export-button:hover {
  opacity: 0.9;
}

.category-form {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 4px 10px;
  font-size: 12px;
}

.add-category-button {
  background: var(--success-color);
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: var(--transition);
  white-space: nowrap;
}

.add-category-button:hover {
  opacity: 0.9;
}

.config-input,
.config-textarea,
.config-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--card-bg);
  color: var(--text-color);
  font-size: 13px;
  box-sizing: border-box;
  transition: var(--transition);
  margin-bottom: 8px;
}

.config-input:focus,
.config-textarea:focus,
.config-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(58, 127, 255, 0.2);
}

.config-input::placeholder,
.config-textarea::placeholder {
  color: #999;
}

.config-textarea {
  min-height: 100px;
  resize: vertical;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  line-height: 1.4;
}

.config-buttons {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.add-button,
.reset-button {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: var(--transition);
}

.add-button {
  background: var(--success-color);
  color: white;
}

.add-button:hover {
  opacity: 0.9;
}

.reset-button {
  background: var(--secondary-color);
  color: white;
}

.reset-button:hover {
  opacity: 0.9;
}

.preset-list {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 8px;
}

.preset-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--card-bg);
  border-radius: var(--border-radius);
  padding: 8px 12px;
  margin-bottom: 6px;
  font-size: 12px;
  transition: var(--transition);
  border: 1px solid var(--border-color);
}

.preset-item:hover {
  background: #e9ecef;
  border-color: var(--primary-color);
}

.preset-info {
  flex: 1;
}

.preset-category {
  font-size: 10px;
  opacity: 0.6;
  margin-right: 8px;
}

.preset-label {
  font-weight: 500;
}

.remove-button {
  background: var(--secondary-color);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.remove-button:hover {
  opacity: 0.9;
}

/* Collapsed state styles */
.dock-container.collapsed .dock-header h3,
.dock-container.collapsed .dock-content {
  opacity: 0;
  pointer-events: none;
}

.dock-container.collapsed .dock-toggle {
  width: 24px;
  height: 24px;
  font-size: 12px;
}

/* Loading state styles */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-color-light);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  margin: 0;
  font-size: 14px;
  color: var(--text-color-light);
}

/* Scrollbar styles */
.dock-container::-webkit-scrollbar,
.config-panel::-webkit-scrollbar,
.preset-list::-webkit-scrollbar {
  width: 6px;
}

.dock-container::-webkit-scrollbar-track,
.config-panel::-webkit-scrollbar-track,
.preset-list::-webkit-scrollbar-track {
  background: var(--background-color);
  border-radius: 3px;
}

.dock-container::-webkit-scrollbar-thumb,
.config-panel::-webkit-scrollbar-thumb,
.preset-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.dock-container::-webkit-scrollbar-thumb:hover,
.config-panel::-webkit-scrollbar-thumb:hover,
.preset-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>