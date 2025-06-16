"use client";

import React, { useState, useEffect } from "react";
import { DocumentGrid } from "../components/DocumentGrid";
import { DocumentUpload } from "../components/DocumentUpload";
import { Button } from "@/src/components/ui/button";
import { ArrowLeft, Upload } from "lucide-react";
import Link from "next/link";

interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
  upload_date: string;
  created_at: string;
  updated_at: string;
}

interface UploadResult {
  filename: string;
  status: "success" | "error";
  message: string;
  chunks?: number;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  // 获取文档列表
  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/documents");
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      } else {
        console.error("Failed to fetch documents");
      }
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };

  // 删除文档
  const handleDocumentDelete = async (docId: string) => {
    try {
      const response = await fetch(`/api/documents/${docId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        // 从列表中移除已删除的文档
        setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
      } else {
        console.error("Failed to delete document");
      }
    } catch (error) {
      console.error("Error deleting document:", error);
    }
  };

  // 处理文件上传
  const handleUploadComplete = (results: UploadResult[]) => {
    console.log("Upload results:", results);
    // 刷新文档列表
    fetchDocuments();
    setShowUpload(false);
  };

  // 处理上传进度
  const handleUploadProgress = (progress: any) => {
    console.log("Upload progress:", progress);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <div className="h-full flex flex-col">
      {/* 页面头部 */}
      <div className="flex items-center justify-between p-6 border-b border-border">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              返回聊天
            </Button>
          </Link>
          <h1 className="text-2xl font-semibold text-foreground">
            📄 文档管理
          </h1>
        </div>

        <Button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2"
        >
          <Upload className="h-4 w-4" />
          批量上传
        </Button>
      </div>

      {/* 上传区域 */}
      {showUpload && (
        <div className="p-6 border-b border-border bg-muted/50">
          <DocumentUpload
            onUploadComplete={handleUploadComplete}
            onUploadProgress={handleUploadProgress}
            uploading={uploading}
            setUploading={setUploading}
          />
        </div>
      )}

      {/* 文档网格 */}
      <div className="flex-1 p-6">
        <DocumentGrid
          documents={documents}
          onDocumentDelete={handleDocumentDelete}
          loading={loading}
        />
      </div>
    </div>
  );
}
