<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from './components/Sidebar.vue'
import Dock from './components/Dock.vue';
import MainPanel from './components/MainPanel.vue';

const messageToEdit = ref('');
const mainPanel = ref<InstanceType<typeof MainPanel> | null>(null);

const handleInsertCode = (code: string) => {
  if (mainPanel.value) {
    mainPanel.value.setMessage(code);
  }
};

const handleDockMessage = (message: string) => {
  if (mainPanel.value) {
    mainPanel.value.setMessageAndSend(message);
  }
};

const onMessageSent = (message: string) => {
  // Can be used to update other components if needed in the future
};
</script>

<template>
  <div class="app-container">
    <Sidebar @insert-code="handleInsertCode" />
    <MainPanel
      ref="mainPanel"
      :initial-message="messageToEdit"
      @message-sent="onMessageSent"
      class="main-panel"
    />
    <Dock @send-message="handleDockMessage" />
  </div>
</template>

<style>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
</style>
