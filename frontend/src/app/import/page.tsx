"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function ImportPage() {
  const [dragging, setDragging] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);

  const loadHistory = () => {
    api.listImports().then((data) => setHistory(data.items || []));
  };

  const handleFile = async (file: File) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await api.uploadFile(file);
      setResult(res);
      loadHistory();
    } catch (err) {
      setResult({ status: "failed", errors: [String(err)] });
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Import Data</h1>
          <p className="text-muted-foreground">Upload CSV, Excel, JSON, Markdown, PDF, or Word files</p>
        </div>

        <Card
          className={`border-2 border-dashed transition-colors ${dragging ? "border-primary bg-primary/5" : "border-border"}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
        >
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Upload className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">Drop files here or click to upload</p>
            <p className="text-sm text-muted-foreground mt-1">CSV, XLSX, JSON, MD, PDF, DOCX</p>
            <input
              type="file"
              className="hidden"
              id="file-upload"
              accept=".csv,.xlsx,.xls,.json,.md,.markdown,.pdf,.docx"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
            <Button className="mt-4" onClick={() => document.getElementById("file-upload")?.click()} disabled={loading}>
              {loading ? "Importing..." : "Select File"}
            </Button>
          </CardContent>
        </Card>

        {result && (
          <Card>
            <CardContent className="p-4 flex items-start gap-3">
              {result.status === "completed" ? (
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
              ) : (
                <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              )}
              <div>
                <p className="font-medium">Import {result.status as string}</p>
                <p className="text-sm text-muted-foreground">
                  Processed: {result.records_processed as number} · Created: {result.records_created as number} · Merged: {result.records_merged as number}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Import History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="outline" size="sm" onClick={loadHistory} className="mb-4">
              Refresh
            </Button>
            <div className="space-y-2">
              {history.map((item, i) => (
                <div key={i} className="flex justify-between text-sm border-b border-border pb-2">
                  <span>{item.filename as string}</span>
                  <span className="text-muted-foreground">{item.status as string}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
