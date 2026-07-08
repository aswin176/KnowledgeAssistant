"use client";

import { useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, type SearchResult } from "@/lib/api";

function getResultHref(result: SearchResult): string {
  if (!result.id) {
    return "#";
  }

  const label = result._labels?.[0];
  if (label === "Person") {
    return `/person/${result.id}`;
  }

  if (label === "Company") {
    return `/company/${result.id}`;
  }

  return `/graph?nodeId=${result.id}`;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("hybrid");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await api.search(query, mode);
      setResults(data.results ?? []);
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

        <div className="flex max-w-2xl gap-2">
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search people, companies, classes, cities..."
            onKeyDown={(event) => event.key === "Enter" && search()}
          />
          <select
            value={mode}
            onChange={(event) => setMode(event.target.value)}
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
          {results.map((result, index) => (
            <Card key={index}>
              <CardContent className="flex items-center justify-between p-4">
                <div>
                  <Link href={getResultHref(result)} className="font-medium hover:text-primary">
                    {result.name ?? "Unknown"}
                  </Link>
                  <p className="text-sm text-muted-foreground">
                    {(result._labels ?? []).join(", ")} - Score: {(result.score ?? 0).toFixed(2)}
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
