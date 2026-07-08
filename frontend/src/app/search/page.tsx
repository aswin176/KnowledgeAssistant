"use client";

import { useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("hybrid");
  const [results, setResults] = useState<{ id?: string; name?: string; _labels?: string[]; score?: number }[]>([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await api.search(query, mode);
      setResults(data.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Search</h1>
          <p className="text-muted-foreground">Graph, full-text, and hybrid search</p>
        </div>

        <div className="flex gap-2 max-w-2xl">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search people, companies, skills..."
            onKeyDown={(e) => e.key === "Enter" && search()}
          />
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="rounded-md border border-border bg-background px-3 text-sm"
          >
            <option value="hybrid">Hybrid</option>
            <option value="fulltext">Full Text</option>
            <option value="graph">Graph</option>
          </select>
          <Button onClick={search} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </Button>
        </div>

        <div className="grid gap-3">
          {results.map((r, i) => (
            <Card key={i}>
              <CardContent className="flex items-center justify-between p-4">
                <div>
                  <Link
                    href={r.id ? `/person/${r.id}` : "#"}
                    className="font-medium hover:text-primary"
                  >
                    {r.name || "Unknown"}
                  </Link>
                  <p className="text-sm text-muted-foreground">
                    {(r._labels || []).join(", ")} · Score: {(r.score || 0).toFixed(2)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
          {results.length === 0 && query && !loading && (
            <p className="text-muted-foreground">No results found.</p>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
