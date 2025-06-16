"use client";

import { ChatSection, ChatMessages, ChatInput } from "@llamaindex/chat-ui";
import { useChat } from "ai/react";
import { CustomChatMessage } from "./CustomChatMessage";
import { ErrorBoundary } from "./ErrorBoundary";
import { useMemo, useCallback, useRef } from "react";

export default function StableChatPage() {
  // 使用 useRef 来存储稳定的配置
  const chatConfigRef = useRef({
    api: "/api/chat",
    body: { id: `chat-${Date.now()}` },
    initialMessages: [
      {
        id: "1",
        role: "assistant" as const,
        content:
          "您好！我是您的AI助手，可以帮您查询和分析文档内容。请问有什么可以帮助您的吗？",
      },
    ],
  });

  // 稳定的错误处理函数
  const handleError = useCallback((error: Error) => {
    console.error("Chat error:", error);
  }, []);

  // 稳定的消息渲染函数
  const messageRenderer = useCallback((message: any, isLoading: any) => (
    <CustomChatMessage message={message} isLoading={isLoading} />
  ), []);

  const handler = useChat({
    ...chatConfigRef.current,
    onError: handleError,
  });

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col">
        <ChatSection handler={handler} className="flex-1 flex flex-col">
          <ChatMessages />
          <ChatInput />
        </ChatSection>
      </div>
    </ErrorBoundary>
  );
}
