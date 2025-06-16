"use client";

import { ChatSection, ChatMessages, ChatInput } from "@llamaindex/chat-ui";
import { useChat } from "ai/react";
import { CustomChatMessage } from "./components/CustomChatMessage";
import { ErrorBoundary } from "./components/ErrorBoundary";

export default function ChatPage() {
  const handler = useChat({
    api: "/api/chat",
    onError: (error) => {
      console.error("Chat error:", error);
    },
    // 自定义请求体格式以匹配FastAPI后端
    body: {
      id: `chat-${Date.now()}`,
    },
    initialMessages: [
      {
        id: "1",
        role: "assistant",
        content:
          "您好！我是您的AI助手，可以帮您查询和分析文档内容。请问有什么可以帮助您的吗？",
      },
    ],
  });

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col">
        <ChatSection handler={handler} className="flex-1 flex flex-col">
          <ChatMessages
            messageRenderer={(message, isLoading) => (
              <CustomChatMessage message={message} isLoading={isLoading} />
            )}
          />
          <ChatInput />
        </ChatSection>
      </div>
    </ErrorBoundary>
  );
}
