const { createApp, ref, reactive, computed, onMounted, nextTick } = Vue;

// 聊天应用组件
const ChatApp = {
  template: `
    <div class="min-h-screen bg-gray-50 flex flex-col">
        <!-- 头部 -->
        <header class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-4xl mx-auto px-4 py-4">
                <div class="flex items-center justify-between">
                    <h1 class="text-xl font-semibold text-gray-900">AI聊天助手</h1>
                    <div class="flex items-center space-x-4">
                        <!-- 文件上传 -->
                        <input 
                            ref="fileInput"
                            type="file" 
                            accept=".pdf,.txt,.doc,.docx" 
                            multiple
                            class="hidden"
                            @change="handleFileUpload"
                        />
                        <button 
                            @click="$refs.fileInput.click()"
                            class="flex items-center space-x-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                            </svg>
                            <span>上传文件</span>
                        </button>
                    </div>
                </div>
                
                <!-- 已上传文件列表 -->
                <div v-if="uploadedFiles.length > 0" class="mt-3 flex flex-wrap gap-2">
                    <div 
                        v-for="file in uploadedFiles" 
                        :key="file.id"
                        class="flex items-center space-x-2 bg-gray-100 px-3 py-1 rounded-full text-sm"
                    >
                        <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        <span>{{ file.id }}</span>
                        <button 
                            @click="removeFile(file.id)"
                            class="text-gray-400 hover:text-red-500 transition-colors"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- 聊天区域 -->
        <main class="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- 聊天消息区域 -->
                <div class="lg:col-span-2">
                    <div
                        ref="messagesContainer"
                        class="bg-white rounded-lg shadow-sm border border-gray-200 h-96 overflow-y-auto custom-scrollbar p-4 space-y-4"
                    >
                        <transition-group name="message" tag="div">
                            <div
                                v-for="message in messages"
                                :key="message.id"
                                :class="[
                                    'flex',
                                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                                ]"
                            >
                                <div
                                    :class="[
                                        'max-w-xs lg:max-w-md px-4 py-2 rounded-lg',
                                        message.sender === 'user'
                                            ? 'bg-blue-500 text-white'
                                            : 'bg-gray-100 text-gray-900'
                                    ]"
                                >
                                    <div v-html="message.content" class="text-sm leading-relaxed"></div>
                                    <div class="text-xs mt-1 opacity-70">{{ message.time }}</div>
                                </div>
                            </div>
                        </transition-group>
                    </div>
                </div>

                <!-- 引用数据列表区域 -->
                <div class="lg:col-span-1">
                    <div class="bg-white rounded-lg shadow-sm border border-gray-200 h-96 overflow-y-auto custom-scrollbar">
                        <div class="p-4 border-b border-gray-200">
                            <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                                <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                引用来源
                            </h3>
                        </div>
                        <div class="p-4">
                            <div v-if="!currentCitations || Object.keys(currentCitations).length === 0" class="text-gray-500 text-sm text-center py-8">
                                暂无引用数据
                            </div>
                            <div v-else class="space-y-3">
                                <div
                                    v-for="citation in sortedCitations"
                                    :key="citation.rank"
                                    class="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
                                >
                                    <div class="flex items-start justify-between mb-2">
                                        <span class="inline-flex items-center justify-center w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full">
                                            {{ citation.rank }}
                                        </span>
                                        <span class="text-xs text-green-600 font-medium">
                                            {{ Math.round(citation.similarity_score * 100) }}%
                                        </span>
                                    </div>
                                    <div class="text-sm font-medium text-gray-900 mb-1">
                                        {{ formatFilename(citation.filename) }}
                                    </div>
                                    <div class="text-xs text-gray-600 line-clamp-3">
                                        {{ citation.content.replace(/^Source \d+: /, '').substring(0, 150) }}...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- 输入区域 -->
        <footer class="bg-white border-t border-gray-200">
            <div class="max-w-4xl mx-auto px-4 py-4">
                <div class="flex space-x-3">
                    <div class="flex-1">
                        <textarea
                            v-model="inputMessage"
                            @keydown.enter.exact.prevent="sendMessage"
                            @keydown.enter.shift.exact="inputMessage += '\\n'"
                            placeholder="输入你的消息... (Enter发送，Shift+Enter换行)"
                            rows="1"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                            :disabled="isLoading"
                        ></textarea>
                        <div class="text-xs text-gray-500 mt-1">{{ inputMessage.length }}/2000</div>
                    </div>
                    <button 
                        @click="sendMessage"
                        :disabled="!inputMessage.trim() || isLoading"
                        class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                    >
                        <svg v-if="!isLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                        </svg>
                        <div v-else class="loading-spinner w-5 h-5"></div>
                    </button>
                </div>
            </div>
        </footer>

        <!-- 引用悬浮框 -->
        <div 
            v-if="tooltip.show"
            ref="tooltip"
            class="citation-tooltip custom-scrollbar"
            :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        >
            <div class="font-semibold text-gray-900 mb-2">
                📄 引用 #{{ tooltip.rank }}
            </div>
            <div class="text-sm text-gray-600 mb-2">
                <strong>文档:</strong> {{ tooltip.filename }}
            </div>
            <div class="text-sm text-gray-600 mb-2">
                <strong>相似度:</strong> {{ tooltip.similarity }}
            </div>
            <div class="text-sm text-gray-700 leading-relaxed">
                {{ tooltip.content }}
            </div>
        </div>
    </div>
    `,

  setup() {
    // 响应式数据
    const messages = ref([
      {
        id: 1,
        sender: "bot",
        content: "你好！我是AI助手，有什么可以帮助你的吗？",
        time: new Date().toLocaleTimeString("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ]);

    const inputMessage = ref("");
    const isLoading = ref(false);
    const uploadedFiles = ref([]);
    const chatId = ref(
      `chat_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`
    );

    // 引用悬浮框
    const tooltip = reactive({
      show: false,
      x: 0,
      y: 0,
      rank: 0,
      filename: "",
      similarity: "",
      content: "",
    });

    // 当前引用数据
    const currentCitations = ref({});

    // 引用
    const messagesContainer = ref(null);
    const fileInput = ref(null);

    // 方法
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop =
            messagesContainer.value.scrollHeight;
        }
      });
    };

    const addMessage = (content, sender = "user") => {
      const message = {
        id: Date.now() + Math.random(),
        sender,
        content,
        time: new Date().toLocaleTimeString("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      // 调试信息
      if (sender === "bot") {
        console.log("添加机器人消息:", {
          contentLength: content.length,
          hasCitationNumbers: content.includes("citation-number"),
          hasSourceMarks: content.includes("Source"),
          content: content.substring(0, 200) + "...",
        });
      }

      messages.value.push(message);
      scrollToBottom();
    };

    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isLoading.value) return;

      const message = inputMessage.value.trim();
      addMessage(message, "user");
      inputMessage.value = "";
      isLoading.value = true;

      try {
        const response = await callChatAPI(message);
        // 注意：流式API已经通过currentBotMessage实时更新了消息
        // 只有在使用普通API时才需要添加响应消息
        if (response && response.isFromRegularAPI) {
          addMessage(response.text, "bot");
        }
      } catch (error) {
        console.error("发送消息失败:", error);
        addMessage(`抱歉，发生了错误：${error.message}`, "bot");
      } finally {
        isLoading.value = false;
      }
    };

    const callChatAPI = async (message) => {
      const annotations = [];
      if (uploadedFiles.value.length > 0) {
        annotations.push({
          type: "document_file",
          data: { files: uploadedFiles.value },
        });
      }

      const requestBody = {
        id: chatId.value,
        messages: [
          {
            role: "user",
            content: message,
            annotations,
          },
        ],
        data: {},
      };

      // 尝试使用流式API
      try {
        await callStreamingAPI(requestBody);
        // 流式API成功，返回标识表示不需要额外处理
        return { isFromRegularAPI: false };
      } catch (error) {
        console.warn("流式API失败，回退到普通API:", error);
        // 回退到普通API
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          throw new Error(`API调用失败: ${response.status}`);
        }

        const responseText = await response.text();
        const processedText = processResponse(responseText);
        return {
          isFromRegularAPI: true,
          text: processedText,
        };
      }
    };

    const callStreamingAPI = async (requestBody) => {
      return new Promise((resolve, reject) => {
        const eventSource = new EventSource(
          "/api/chat/stream?" +
            new URLSearchParams({
              data: JSON.stringify(requestBody),
            })
        );

        let fullText = "";
        let citations = {};
        let currentBotMessage = null;

        eventSource.onopen = () => {
          console.log("流式连接已建立");
          // 添加一个临时的机器人消息
          const botMessage = {
            id: Date.now() + Math.random(),
            sender: "bot",
            content: "",
            time: new Date().toLocaleTimeString("zh-CN", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          };
          messages.value.push(botMessage);
          currentBotMessage = botMessage;
          console.log("添加了机器人消息:", currentBotMessage);
          scrollToBottom();
        };

        eventSource.addEventListener("citation_data", (event) => {
          try {
            const data = JSON.parse(event.data);
            citations = data.citations;
            currentCitations.value = citations; // 更新响应式引用数据
            console.log("收到引用数据:", citations);
          } catch (e) {
            console.error("解析引用数据失败:", e);
          }
        });

        eventSource.addEventListener("text_chunk", (event) => {
          try {
            const data = JSON.parse(event.data);
            fullText += data.chunk;
            console.log("收到文本块:", data.chunk);
            console.log("累积文本:", fullText);

            // 实时更新消息内容 - 找到消息并更新
            if (currentBotMessage) {
              const messageIndex = messages.value.findIndex(
                (m) => m.id === currentBotMessage.id
              );
              if (messageIndex !== -1) {
                messages.value[messageIndex].content = fullText;
                console.log(
                  "更新消息内容:",
                  messages.value[messageIndex].content
                );
                nextTick(() => {
                  scrollToBottom();
                });
              }
            }
          } catch (e) {
            console.error("解析文本块失败:", e);
          }
        });

        eventSource.addEventListener("complete", (event) => {
          console.log("流式响应完成");
          eventSource.close();

          // 处理最终文本和引用
          const processedText =
            window.citationProcessor.processTextWithCitations(
              fullText,
              citations
            );

          if (currentBotMessage) {
            const messageIndex = messages.value.findIndex(
              (m) => m.id === currentBotMessage.id
            );
            if (messageIndex !== -1) {
              messages.value[messageIndex].content = processedText;
              console.log(
                "最终处理后的消息内容:",
                messages.value[messageIndex].content
              );
            }
          }

          resolve(); // 不返回文本，因为消息已经通过currentBotMessage更新了
        });

        eventSource.addEventListener("error", (event) => {
          console.error("流式响应错误:", event);
          eventSource.close();

          try {
            const data = JSON.parse(event.data);
            reject(new Error(data.error || "流式响应错误"));
          } catch (e) {
            reject(new Error("流式响应发生未知错误"));
          }
        });

        eventSource.onerror = (error) => {
          console.error("EventSource错误:", error);
          eventSource.close();
          reject(new Error("连接流式API失败"));
        };
      });
    };

    const processResponse = (responseText) => {
      const result = window.citationProcessor.processResponse(responseText);
      console.log("引用处理结果:", result);
      return result.text;
    };

    // 文件上传处理
    const handleFileUpload = async (event) => {
      const files = Array.from(event.target.files);

      for (const file of files) {
        try {
          isLoading.value = true;
          const uploadedFile = await uploadFile(file);
          uploadedFiles.value.push(uploadedFile);
          addMessage(`文件上传成功: ${file.name}`, "bot");
        } catch (error) {
          console.error("文件上传失败:", error);
          addMessage(`文件上传失败: ${error.message}`, "bot");
        } finally {
          isLoading.value = false;
        }
      }

      // 清空文件输入
      if (fileInput.value) {
        fileInput.value.value = "";
      }
    };

    const uploadFile = async (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = async (e) => {
          try {
            const base64 = e.target.result.split(",")[1];

            const response = await fetch("/api/chat/file", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                name: file.name,
                base64: base64,
                params: JSON.stringify({
                  size: file.size,
                  type: file.type,
                }),
              }),
            });

            if (!response.ok) {
              const errorText = await response.text();
              throw new Error(`上传失败: ${response.status} - ${errorText}`);
            }

            const result = await response.json();
            resolve(result);
          } catch (error) {
            reject(error);
          }
        };

        reader.onerror = () => reject(new Error("文件读取失败"));
        reader.readAsDataURL(file);
      });
    };

    const removeFile = (fileId) => {
      uploadedFiles.value = uploadedFiles.value.filter((f) => f.id !== fileId);
    };

    // 格式化文件名
    const formatFilename = (filename) => {
      return filename.replace(/^常见问题类-\d+_/, "").replace(/\.txt$/, "");
    };

    // 计算属性：排序后的引用数据
    const sortedCitations = computed(() => {
      if (
        !currentCitations.value ||
        Object.keys(currentCitations.value).length === 0
      ) {
        return [];
      }
      return Object.values(currentCitations.value).sort(
        (a, b) => a.rank - b.rank
      );
    });

    // 引用悬浮框处理
    const showCitationTooltip = (event, rank) => {
      const citation = window.citationProcessor.getCitationByRank(rank);
      if (!citation) return;

      const rect = event.target.getBoundingClientRect();
      tooltip.show = true;
      tooltip.x = rect.left + window.scrollX;
      tooltip.y = rect.bottom + window.scrollY + 5;
      tooltip.rank = rank;
      tooltip.filename = window.citationProcessor.formatFilename(
        citation.filename
      );
      tooltip.similarity = window.citationProcessor.formatSimilarityScore(
        citation.similarity_score
      );
      tooltip.content = citation.content.replace(/^Source \d+: /, "");
    };

    const hideCitationTooltip = () => {
      tooltip.show = false;
    };

    // 全局方法注册（供HTML中的v-html使用）
    window.showCitationTooltip = showCitationTooltip;
    window.hideCitationTooltip = hideCitationTooltip;

    return {
      messages,
      inputMessage,
      isLoading,
      uploadedFiles,
      tooltip,
      currentCitations,
      sortedCitations,
      messagesContainer,
      fileInput,
      sendMessage,
      handleFileUpload,
      removeFile,
      formatFilename,
      showCitationTooltip,
      hideCitationTooltip,
    };
  },
};

// 创建Vue应用
createApp({
  components: {
    ChatApp,
  },
}).mount("#app");
