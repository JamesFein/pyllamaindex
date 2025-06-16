"use client";

import React, { useState } from "react";
import { Button } from "@/src/components/ui/button";
import { X, FileText, File, Image } from "lucide-react";
import { DeleteConfirm } from "./DeleteConfirm";

interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
  upload_date: string;
  created_at: string;
  updated_at: string;
}

interface DocumentCardProps {
  document: Document;
  onDelete: (id: string) => void;
}

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// 获取文件图标
function getFileIcon(type: string, name: string) {
  const extension = name.split(".").pop()?.toLowerCase();

  if (
    type?.startsWith("image/") ||
    ["jpg", "jpeg", "png", "gif", "webp"].includes(extension || "")
  ) {
    return <Image className="h-8 w-8 text-blue-500" />;
  }

  if (["pdf"].includes(extension || "")) {
    return <FileText className="h-8 w-8 text-red-500" />;
  }

  if (["txt", "md", "doc", "docx"].includes(extension || "")) {
    return <FileText className="h-8 w-8 text-blue-600" />;
  }

  return <File className="h-8 w-8 text-gray-500" />;
}

export function DocumentCard({ document, onDelete }: DocumentCardProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleDelete = () => {
    onDelete(document.id);
    setShowDeleteConfirm(false);
  };

  return (
    <>
      <div
        className="relative group bg-card border border-border rounded-lg p-4 hover:shadow-md transition-all duration-200 cursor-pointer"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* 删除按钮 */}
        <Button
          variant="ghost"
          size="sm"
          className={`absolute top-2 right-2 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity ${
            isHovered ? "opacity-100" : ""
          }`}
          onClick={(e) => {
            e.stopPropagation();
            setShowDeleteConfirm(true);
          }}
        >
          <X className="h-3 w-3" />
        </Button>

        {/* 文件图标 */}
        <div className="flex justify-center mb-3">
          {getFileIcon(document.type, document.name)}
        </div>

        {/* 文件名 */}
        <div className="text-center mb-2">
          <h3
            className="text-sm font-medium text-foreground truncate"
            title={document.name}
          >
            {document.name}
          </h3>
        </div>

        {/* 文件信息 */}
        <div className="text-xs text-muted-foreground text-center space-y-1">
          <div>{formatFileSize(document.size)}</div>
          <div title={formatDate(document.upload_date)}>
            {formatDate(document.upload_date).split(" ")[0]}
          </div>
        </div>

        {/* 悬浮时显示完整信息 */}
        {isHovered && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 p-2 bg-popover border border-border rounded-md shadow-lg z-10 min-w-48">
            <div className="text-xs space-y-1">
              <div className="font-medium">{document.name}</div>
              <div>大小: {formatFileSize(document.size)}</div>
              <div>类型: {document.type}</div>
              <div>上传时间: {formatDate(document.upload_date)}</div>
            </div>
          </div>
        )}
      </div>

      {/* 删除确认对话框 */}
      <DeleteConfirm
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
        documentName={document.name}
      />
    </>
  );
}
