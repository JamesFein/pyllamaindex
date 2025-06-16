import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import '@llamaindex/chat-ui/styles/markdown.css'
import '@llamaindex/chat-ui/styles/pdf.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PyLlamaIndex Chat',
  description: 'AI-powered chat interface with document citations',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <header className="border-b border-border bg-card">
            <div className="container mx-auto px-4 py-3">
              <h1 className="text-xl font-semibold text-foreground">
                PyLlamaIndex Chat
              </h1>
            </div>
          </header>
          <main className="container mx-auto h-[calc(100vh-73px)]">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
