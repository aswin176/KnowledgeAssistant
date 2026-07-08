"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

type ImportResult = {
  status?: string;
  records_processed?: number;
  records_created?: number;
  records_merged?: number;
  errors?: string[];
};

type ImportHistoryItem = {
  filename?: string;
  status?: string;
};

export default function ImportPage() {
  const [dragging, setDragging] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<ImportHistoryItem[]>([]);

  const loadHistory = () => {
    api.listImports().then((data) => setHistory(data.items ?? []));
  };

  const handleFile = async (file: File) => {
    setLoading(true);
    setResult(null);
    try {
      const response = await api.uploadFile(file);
      setResult(response);
      loadHistory();
    } catch (error) {
      setResult({ status: "failed", errors: [String(error)] });
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) void handleFile(file);
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Import Data</h1>
          <p className="text-muted-foreground">
            Upload CSV, Excel, JSON, Markdown, PDF, or Word files
          </p>
        </div>

        <Card
          className={`border-2 border-dashed transition-colors ${dragging ? "border-primary bg-primary/5" : "border-border"}`}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
        >
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Upload className="mb-4 h-12 w-12 text-muted-foreground" />
            <p className="text-lg font-medium">Drop files here or click to upload</p>
            <p className="mt-1 text-sm text-muted-foreground">CSV, XLSX, JSON, MD, PDF, DOCX</p>
            <input
              type="file"
              className="hidden"
              id="file-upload"
              accept=".csv,.xlsx,.xls,.json,.md,.markdown,.pdf,.docx"
              onChange={(event) => event.target.files?.[0] && handleFile(event.target.files[0])}
            />
            <Button
              className="mt-4"
              onClick={() => document.getElementById("file-upload")?.click()}
              disabled={loading}
            >
              {loading ? "Importing..." : "Select File"}
            </Button>
          </CardContent>
        </Card>

        {result && (
          <Card>
            <CardContent className="flex items-start gap-3 p-4">
              {result.status === "completed" ? (
                <CheckCircle className="mt-0.5 h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="mt-0.5 h-5 w-5 text-destructive" />
              )}
              <div>
                <p className="font-medium">Import {result.status ?? "unknown"}</p>
                <p className="text-sm text-muted-foreground">
                  Processed: {result.records_processed ?? 0} - Created:{" "}
                  {result.records_created ?? 0} - Merged: {result.records_merged ?? 0}
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
              {history.map((item, index) => (
                <div key={index} className="flex justify-between border-b border-border pb-2 text-sm">
                  <span>{item.filename ?? "Unnamed import"}</span>
                  <span className="text-muted-foreground">{item.status ?? "unknown"}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
