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
  position: fixed;
  top: 0;
  right: 0;
  width: 320px;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: all 0.3s ease;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.dock-container.collapsed {
  width: 60px;
  padding: 10px;
}

.dock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.dock-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  transition: opacity 0.3s ease;
}

.dock-toggle {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.dock-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
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
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 12px;
}

.category-tab {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.category-tab:hover {
  background: rgba(255, 255, 255, 0.2);
}

.category-tab.active {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.button-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dock-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  text-align: left;
}

.dock-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.button-icon {
  font-size: 16px;
  margin-right: 8px;
}

.button-label {
  font-weight: 500;
  font-size: 14px;
  color: white;
}

.dock-footer {
  padding: 10px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  margin-top: 16px;
}

.config-button {
  width: 100%;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.config-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.config-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
}

.config-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 12px;
}

.config-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.close-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.import-export-section,
.category-management,
.preset-form,
.preset-management {
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 12px;
}

.import-export-buttons {
  display: flex;
  gap: 12px;
}

.import-button,
.export-button {
  background: rgba(76, 175, 80, 0.8);
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.import-button:hover,
.export-button:hover {
  background: rgba(76, 175, 80, 1);
}

.category-form {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
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
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 12px;
}

.add-category-button {
  background: rgba(76, 175, 80, 0.8);
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.add-category-button:hover {
  background: rgba(76, 175, 80, 1);
}

.config-input,
.config-textarea,
.config-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 13px;
  box-sizing: border-box;
  transition: all 0.2s ease;
  margin-bottom: 8px;
}

.config-input:focus,
.config-textarea:focus,
.config-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.15);
}

.config-input::placeholder,
.config-textarea::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.config-textarea {
  min-height: 100px;
  resize: vertical;
  font-family: 'Courier New', monospace;
  line-height: 1.4;
}

.config-buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.add-button,
.reset-button {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.add-button {
  background: rgba(76, 175, 80, 0.8);
  color: white;
}

.add-button:hover {
  background: rgba(76, 175, 80, 1);
}

.reset-button {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

.reset-button:hover {
  background: rgba(244, 67, 54, 1);
}

.preset-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px;
}

.preset-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 6px;
  font-size: 12px;
  transition: all 0.2s ease;
}

.preset-item:hover {
  background: rgba(255, 255, 255, 0.1);
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
  background: rgba(244, 67, 54, 0.8);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-button:hover {
  background: rgba(244, 67, 54, 1);
}

/* Collapsed state styles */
.dock-container.collapsed .dock-header h3,
.dock-container.collapsed .dock-content {
  opacity: 0;
  pointer-events: none;
}

.dock-container.collapsed .dock-toggle {
  width: 28px;
  height: 28px;
  font-size: 12px;
}

/* Loading state styles */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.8);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top: 3px solid rgba(255, 255, 255, 0.8);
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
  color: rgba(255, 255, 255, 0.7);
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
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.dock-container::-webkit-scrollbar-thumb,
.config-panel::-webkit-scrollbar-thumb,
.preset-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.dock-container::-webkit-scrollbar-thumb:hover,
.config-panel::-webkit-scrollbar-thumb:hover,
.preset-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>