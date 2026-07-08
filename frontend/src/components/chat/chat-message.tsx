"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";

interface Source {
  id?: string;
  name?: string;
  type?: string;
}

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export function ChatMessage({ role, content, sources }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-4 py-6 ${isUser ? "" : "bg-secondary/30"}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
          isUser ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
        }`}
      >
        {isUser ? "U" : "AI"}
      </div>
      <div className="flex-1 space-y-2 overflow-hidden">
        <p className="text-xs font-medium text-muted-foreground">{isUser ? "You" : "Eutridats"}</p>
        <div className="markdown-body prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
        {sources && sources.length > 0 && (
          <details className="mt-3 rounded-md border border-border p-3">
            <summary className="cursor-pointer text-sm font-medium text-muted-foreground">
              Sources ({sources.length})
            </summary>
            <div className="mt-2 flex flex-wrap gap-2">
              {sources.map((source, i) => (
                <Link
                  key={i}
                  href={source.id ? `/person/${source.id}` : "#"}
                  className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs text-primary hover:bg-primary/20"
                >
                  {source.name || "Unknown"} · {source.type}
                </Link>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
