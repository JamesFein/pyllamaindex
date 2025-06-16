"use client";

import { ChatSection, ChatMessages, ChatInput } from "@llamaindex/chat-ui";
import { useChat } from "ai/react";
import { ErrorBoundary } from "./components/ErrorBoundary";

export default function ChatPage() {
  const handler = useChat({
    api: "http://localhost:8000/api/chat",
    body: { id: `chat-${Date.now()}` },
    initialMessages: [
      {
        id: "welcome-message",
        role: "assistant",
        content:
          "您好！我是您的AI助手，可以帮您查询和分析文档内容。请问有什么可以帮助您的吗？",
      },
    ],
  });

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
