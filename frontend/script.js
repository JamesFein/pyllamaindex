// 全局变量
let chatId =
  "chat_" + Date.now() + "_" + Math.random().toString(36).substring(2, 11);
let uploadedFiles = [];

// DOM元素
let chatMessages,
  messageInput,
  sendBtn,
  fileInput,
  uploadBtn,
  uploadedFilesDiv,
  loadingOverlay,
  charCount;

// 初始化
document.addEventListener("DOMContentLoaded", function () {
  // 获取DOM元素
  chatMessages = document.getElementById("chatMessages");
  messageInput = document.getElementById("messageInput");
  sendBtn = document.getElementById("sendBtn");
  fileInput = document.getElementById("fileInput");
  uploadBtn = document.getElementById("uploadBtn");
  uploadedFilesDiv = document.getElementById("uploadedFiles");
  loadingOverlay = document.getElementById("loadingOverlay");
  charCount = document.querySelector(".char-count");

  // 绑定事件
  sendBtn.addEventListener("click", sendMessage);
  messageInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  messageInput.addEventListener("input", function () {
    autoResize();
    updateCharCount();
  });
  uploadBtn.addEventListener("click", function () {
    fileInput.click();
  });
  fileInput.addEventListener("change", handleFileUpload);

  updateCharCount();
});

function autoResize() {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
}

function updateCharCount() {
  const count = messageInput.value.length;
  charCount.textContent = count + "/2000";
  charCount.style.color = count > 1800 ? "#ff4757" : "#666";
}

// 文件上传处理
async function handleFileUpload(event) {
  const files = Array.from(event.target.files);

  for (const file of files) {
    try {
      showLoading("正在上传文件...");
      const uploadedFile = await uploadFile(file);
      uploadedFiles.push(uploadedFile);
      displayUploadedFile(uploadedFile);
      addMessage("文件上传成功: " + file.name, "bot");
    } catch (error) {
      console.error("文件上传失败:", error);
      addMessage("文件上传失败: " + error.message, "bot");
    } finally {
      hideLoading();
    }
  }

  // 清空文件输入
  fileInput.value = "";
}

async function uploadFile(file) {
  const reader = new FileReader();

  return new Promise((resolve, reject) => {
    reader.onload = async function (e) {
      try {
        const base64 = e.target.result.split(",")[1];

        const response = await fetch("/api/chat/file", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
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
          throw new Error("上传失败: " + response.status + " - " + errorText);
        }

        const result = await response.json();
        resolve(result);
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = function () {
      reject(new Error("文件读取失败"));
    };
    reader.readAsDataURL(file);
  });
}

function displayUploadedFile(file) {
  const fileTag = document.createElement("div");
  fileTag.className = "file-tag";
  fileTag.innerHTML =
    "📄 " +
    file.id +
    ' <span class="remove-file" onclick="removeFile(\'' +
    file.id +
    "')\">&times;</span>";
  uploadedFilesDiv.appendChild(fileTag);
}

function removeFile(fileId) {
  uploadedFiles = uploadedFiles.filter((f) => f.id !== fileId);
  updateUploadedFilesDisplay();
}

function updateUploadedFilesDisplay() {
  uploadedFilesDiv.innerHTML = "";
  uploadedFiles.forEach((file) => displayUploadedFile(file));
}

// 发送消息
async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message) return;

  // 显示用户消息
  addMessage(message, "user");
  messageInput.value = "";
  autoResize();
  updateCharCount();

  try {
    showLoading();
    const response = await callChatAPI(message);
    addMessage(response, "bot");
  } catch (error) {
    console.error("发送消息失败:", error);
    addMessage(
      "抱歉，发生了错误，请稍后重试。错误信息: " + error.message,
      "bot"
    );
  } finally {
    hideLoading();
  }
}

async function callChatAPI(message) {
  // 构建注释数组
  const annotations = [];
  if (uploadedFiles.length > 0) {
    annotations.push({
      type: "document_file",
      data: {
        files: uploadedFiles,
      },
    });
  }

  const requestBody = {
    id: chatId,
    messages: [
      {
        role: "user",
        content: message,
        annotations: annotations,
      },
    ],
    data: {},
  };

  console.log("发送请求:", JSON.stringify(requestBody, null, 2));

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error("API调用失败: " + response.status + " - " + errorText);
  }

  return await response.text();
}

// 添加消息到聊天界面
function addMessage(text, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message " + sender + "-message";

  const now = new Date();
  const timeString = now.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  });

  messageDiv.innerHTML =
    '<div class="message-content"><div class="message-text">' +
    escapeHtml(text) +
    '</div><div class="message-time">' +
    timeString +
    "</div></div>";

  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoading(text) {
  if (!text) text = "AI正在思考中...";
  loadingOverlay.querySelector(".loading-text").textContent = text;
  loadingOverlay.style.display = "flex";
  sendBtn.disabled = true;
}

function hideLoading() {
  loadingOverlay.style.display = "none";
  sendBtn.disabled = false;
}
