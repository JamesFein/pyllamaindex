"use client";

import { ChatSection, ChatMessages, ChatInput } from "@llamaindex/chat-ui";
import { useChat } from "ai/react";

// 在组件外部定义静态配置，确保引用稳定性
const STATIC_CHAT_CONFIG = {
  api: "/api/chat",
  body: { id: "stable-chat" },
  initialMessages: [
    {
      id: "welcome-message",
      role: "assistant" as const,
      content:
        "您好！我是您的AI助手，可以帮您查询和分析文档内容。请问有什么可以帮助您的吗？",
    },
  ],
};

export default function StableChatPage() {
  // 直接使用静态配置，避免任何可能导致重新创建的操作
  const handler = useChat(STATIC_CHAT_CONFIG);

  return (
    <div className="h-full flex flex-col">
      <ChatSection handler={handler as any} className="flex-1 flex flex-col">
        <ChatMessages />
        <ChatInput />
      </ChatSection>
    </div>
  );
}
