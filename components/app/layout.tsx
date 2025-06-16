import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import "@llamaindex/chat-ui/styles/markdown.css";
import "@llamaindex/chat-ui/styles/pdf.css";
import Link from "next/link";
import { Button } from "@/src/components/ui/button";
import { MessageSquare, FileText } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PyLlamaIndex Chat",
  description: "AI-powered chat interface with document citations",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <header className="border-b border-border bg-card">
            <div className="container mx-auto px-4 py-3">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-semibold text-foreground">
                  PyLlamaIndex Chat
                </h1>

                <nav className="flex items-center gap-2">
                  <Link href="/">
                    <Button variant="ghost" size="sm">
                      <MessageSquare className="h-4 w-4 mr-2" />
                      聊天
                    </Button>
                  </Link>
                  <Link href="/documents">
                    <Button variant="ghost" size="sm">
                      <FileText className="h-4 w-4 mr-2" />
                      文档管理
                    </Button>
                  </Link>
                </nav>
              </div>
            </div>
          </header>
          <main className="container mx-auto h-[calc(100vh-73px)]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
