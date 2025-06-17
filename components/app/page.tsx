"use client";

import { ChatSection, ChatMessages, ChatInput } from "@llamaindex/chat-ui";
import { useChat } from "ai/react";
import { ErrorBoundary } from "./components/ErrorBoundary";

// 修复422错误：使用正确的请求格式 { id: "...", messages: [...] }
const CHAT_CONFIG = {
  api: "http://localhost:8000/api/chat",
  body: { id: "stable-chat-fixed" }, // 添加必需的id字段
  initialMessages: [
    {
      id: "welcome-message",
      role: "assistant" as const,
      content:
        "您好！我是您的AI助手，422错误已修复，可以帮您查询和分析文档内容。请问有什么可以帮助您的吗？",
    },
  ],
};

export default function ChatPage() {
  const handler = useChat(CHAT_CONFIG);

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-background">
        <ChatSection handler={handler as any} className="flex-1 flex flex-col">
          <ChatMessages />
          <ChatInput />
        </ChatSection>
      </div>
    </ErrorBoundary>
  );
}
