"use client";

import React from "react";
import { Button } from "@/src/components/ui/button";
import { AlertTriangle } from "lucide-react";

interface DeleteConfirmProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  documentName: string;
}

export function DeleteConfirm({
  isOpen,
  onClose,
  onConfirm,
  documentName,
}: DeleteConfirmProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="h-6 w-6 text-red-500" />
          <h3 className="text-lg font-semibold text-foreground">
            确认删除文档
          </h3>
        </div>

        <p className="text-muted-foreground mb-6">
          您确定要删除文档{" "}
          <span className="font-medium text-foreground">"{documentName}"</span>{" "}
          吗？
          <br />
          <br />
          此操作将：
          <br />
          • 从数据库中删除文档记录
          <br />
          • 删除文件系统中的文件
          <br />
          • 删除相关的向量数据
          <br />
          <br />
          <span className="text-red-500 font-medium">此操作不可撤销！</span>
        </p>

        <div className="flex gap-3 justify-end">
          <Button variant="outline" onClick={onClose}>
            取消
          </Button>
          <Button variant="destructive" onClick={onConfirm}>
            确认删除
          </Button>
        </div>
      </div>
    </div>
  );
}
