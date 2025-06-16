"use client";

import { CitationTooltip } from "./CitationTooltip";
import { useMemo } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface CustomChatMessageProps {
  message: Message;
  isLoading?: boolean;
}

export function CustomChatMessage({
  message,
  isLoading,
}: CustomChatMessageProps) {
  // 使用 useMemo 优化处理引用标记的函数，基于消息内容进行缓存
  const processContent = useMemo(() => {
    return (content: string) => {
      // 查找所有引用标记
      const citationRegex = /\[citation:(.*?)\]/g;
      const citations: string[] = [];
      let match;

      while ((match = citationRegex.exec(content)) !== null) {
        citations.push(match[1]);
      }

      // 替换引用标记为带tooltip的序号
      let processedContent = content;
      citations.forEach((citationId, index) => {
        const citationNumber = index + 1;
        const citationPattern = new RegExp(
          `\\[citation:${citationId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\]`,
          "g"
        );

        processedContent = processedContent.replace(
          citationPattern,
          `<citation-placeholder data-citation-id="${citationId}" data-citation-number="${citationNumber}"></citation-placeholder>`
        );
      });

      return processedContent;
    };
  }, [message.content]); // 依赖消息内容，只有内容变化时才重新计算

  // 使用 useMemo 优化渲染处理后的内容
  const renderContent = useMemo(() => {
    return (content: string) => {
      const processedContent = processContent(content);

      // 分割内容并处理引用占位符
      const parts = processedContent.split(
        /(<citation-placeholder[^>]*><\/citation-placeholder>)/g
      );

      return parts.map((part, index) => {
        const citationMatch = part.match(
          /<citation-placeholder data-citation-id="([^"]*)" data-citation-number="([^"]*)"><\/citation-placeholder>/
        );

        if (citationMatch) {
          const [, citationId, citationNumber] = citationMatch;
          return (
            <CitationTooltip
              key={`citation-${citationId}-${index}`}
              citationId={citationId}
            >
              [{citationNumber}]
            </CitationTooltip>
          );
        }

        return part;
      });
    };
  }, [processContent, message.content]); // 依赖 processContent 和消息内容

  // 如果是助手消息且包含引用，使用自定义渲染
  if (message.role === "assistant" && message.content.includes("[citation:")) {
    return (
      <div
        className={`flex ${
          message.role === "user" ? "justify-end" : "justify-start"
        } mb-4 chat-message`}
      >
        <div
          className={`max-w-[80%] rounded-lg px-4 py-3 ${
            message.role === "user"
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground border border-border"
          } shadow-sm`}
        >
          <div className="prose prose-sm max-w-none dark:prose-invert">
            {renderContent(message.content)}
          </div>
          {isLoading && (
            <div className="flex items-center mt-3 space-x-2 text-muted-foreground">
              <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xs">正在思考...</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // 对于其他消息，使用简单的消息显示
  return (
    <div
      className={`flex ${
        message.role === "user" ? "justify-end" : "justify-start"
      } mb-4 chat-message`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          message.role === "user"
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-muted-foreground border border-border"
        } shadow-sm`}
      >
        <div className="prose prose-sm max-w-none dark:prose-invert">
          {message.content}
        </div>
        {isLoading && (
          <div className="flex items-center mt-3 space-x-2 text-muted-foreground">
            <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
            <span className="text-xs">正在思考...</span>
          </div>
        )}
      </div>
    </div>
  );
}
