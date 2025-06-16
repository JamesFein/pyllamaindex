"use client";

import React, { useState, useRef } from "react";
import { Button } from "@/src/components/ui/button";
import { Upload, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface UploadResult {
  filename: string;
  status: "success" | "error";
  message: string;
  chunks?: number;
}

interface UploadProgress {
  filename: string;
  status: "uploading" | "processing" | "completed" | "error";
  progress?: number;
}

interface DocumentUploadProps {
  onUploadComplete: (results: UploadResult[]) => void;
  onUploadProgress: (progress: UploadProgress) => void;
  uploading: boolean;
  setUploading: (uploading: boolean) => void;
}

export function DocumentUpload({
  onUploadComplete,
  onUploadProgress,
  uploading,
  setUploading,
}: DocumentUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);
  const [showResults, setShowResults] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 处理文件选择
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles((prev) => [...prev, ...files]);
  };

  // 移除选中的文件
  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // 清空所有文件
  const clearFiles = () => {
    setSelectedFiles([]);
    setUploadResults([]);
    setShowResults(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // 上传文件
  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setUploadResults([]);
    setShowResults(true);

    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => {
        formData.append("files", file);
      });

      // 模拟进度更新
      selectedFiles.forEach((file) => {
        onUploadProgress({
          filename: file.name,
          status: "uploading",
          progress: 0,
        });
      });

      const response = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadResults(data.results || []);
        onUploadComplete(data.results || []);
      } else {
        const errorData = await response.json();
        setUploadResults([
          {
            filename: "Upload Error",
            status: "error",
            message: errorData.error || "Upload failed",
          },
        ]);
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadResults([
        {
          filename: "Network Error",
          status: "error",
          message: "Network error occurred during upload",
        },
      ]);
    } finally {
      setUploading(false);
    }
  };

  // 重试失败的上传
  const retryFailedUploads = () => {
    const failedFiles = uploadResults
      .filter((result) => result.status === "error")
      .map((result) =>
        selectedFiles.find((file) => file.name === result.filename)
      )
      .filter(Boolean) as File[];

    if (failedFiles.length > 0) {
      setSelectedFiles(failedFiles);
      setShowResults(false);
      uploadFiles();
    }
  };

  const successCount = uploadResults.filter(
    (r) => r.status === "success"
  ).length;
  const errorCount = uploadResults.filter((r) => r.status === "error").length;

  return (
    <div className="space-y-4">
      {/* 文件选择区域 */}
      <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
        <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-lg font-medium mb-2">上传文档</h3>
        <p className="text-muted-foreground mb-4">
          支持 PDF、TXT、DOC、DOCX 等格式，可同时选择多个文件
        </p>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.doc,.docx,.md"
          onChange={handleFileSelect}
          className="hidden"
        />

        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          选择文件
        </Button>
      </div>

      {/* 已选择的文件列表 */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">
              已选择 {selectedFiles.length} 个文件
            </h4>
            <Button variant="ghost" size="sm" onClick={clearFiles}>
              清空
            </Button>
          </div>

          <div className="max-h-32 overflow-y-auto space-y-1">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-muted rounded"
              >
                <span className="text-sm truncate flex-1">{file.name}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(index)}
                  disabled={uploading}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>

          <Button onClick={uploadFiles} disabled={uploading} className="w-full">
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                上传中...
              </>
            ) : (
              "开始上传"
            )}
          </Button>
        </div>
      )}

      {/* 上传结果 */}
      {showResults && uploadResults.length > 0 && (
        <div className="border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium">上传结果</h4>
            <div className="text-sm text-muted-foreground">
              成功: {successCount} | 失败: {errorCount}
            </div>
          </div>

          <div className="max-h-40 overflow-y-auto space-y-2">
            {uploadResults.map((result, index) => (
              <div
                key={index}
                className="flex items-center gap-2 p-2 bg-muted rounded"
              >
                {result.status === "success" ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-500" />
                )}
                <div className="flex-1">
                  <div className="text-sm font-medium">{result.filename}</div>
                  <div className="text-xs text-muted-foreground">
                    {result.message}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-2 mt-3">
            <Button variant="outline" size="sm" onClick={clearFiles}>
              关闭
            </Button>
            {errorCount > 0 && (
              <Button variant="outline" size="sm" onClick={retryFailedUploads}>
                重试失败项
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
