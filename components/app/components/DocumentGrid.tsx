'use client'

import React from 'react'
import { DocumentCard } from './DocumentCard'
import { LoadingSpinner } from './LoadingSpinner'

interface Document {
  id: string
  name: string
  size: number
  type: string
  upload_date: string
  created_at: string
  updated_at: string
}

interface DocumentGridProps {
  documents: Document[]
  onDocumentDelete: (id: string) => void
  loading: boolean
}

export function DocumentGrid({ documents, onDocumentDelete, loading }: DocumentGridProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
        <span className="ml-2 text-muted-foreground">加载文档中...</span>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <div className="text-6xl mb-4">📄</div>
        <h3 className="text-lg font-medium text-foreground mb-2">
          暂无文档
        </h3>
        <p className="text-muted-foreground">
          点击上方的"批量上传"按钮开始添加文档
        </p>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="mb-4 text-sm text-muted-foreground">
        共 {documents.length} 个文档，按上传时间倒序排列
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {documents.map((document) => (
          <DocumentCard
            key={document.id}
            document={document}
            onDelete={onDocumentDelete}
          />
        ))}
      </div>
    </div>
  )
}
