"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { GraphViewer } from "@/components/graph/graph-viewer";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { api, type GraphNode, type GraphRelationship } from "@/lib/api";

export default function GraphPage() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [relationships, setRelationships] = useState<GraphRelationship[]>([]);
  const [centerId, setCenterId] = useState<string>();
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const exploreNode = async (nodeId: string) => {
    setLoading(true);
    try {
      const data = await api.exploreGraph(nodeId, 2);
      setNodes(data.nodes);
      setRelationships(data.relationships);
      setCenterId(data.center_id);
    } catch {
      // Ignore failed graph expansions and keep the previous graph visible.
    } finally {
      setLoading(false);
    }
  };

  const searchAndExplore = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const results = await api.search(searchQuery, "hybrid", 1);
      if (results.results[0]?.id) {
        await exploreNode(results.results[0].id);
      }
    } catch {
      // Ignore failed searches and keep the page responsive.
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    api.listPersons(5).then((data) => {
      if (data.items[0]?.id) {
        void exploreNode(data.items[0].id);
      }
    });
  }, []);

  return (
    <DashboardLayout>
      <div className="flex h-full flex-col">
        <div className="flex items-center gap-4 border-b border-border px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold">Graph Explorer</h1>
            <p className="text-sm text-muted-foreground">
              Interactive knowledge graph visualization
            </p>
          </div>
          <div className="ml-auto flex gap-2">
            <Input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search entity..."
              className="w-64"
              onKeyDown={(event) => event.key === "Enter" && searchAndExplore()}
            />
            <Button onClick={searchAndExplore} disabled={loading}>
              Explore
            </Button>
          </div>
        </div>
        <div className="flex-1 p-4">
          {nodes.length > 0 ? (
            <GraphViewer
              nodes={nodes}
              relationships={relationships}
              centerId={centerId}
              onNodeClick={(id) => {
                void exploreNode(id);
                router.push(`/person/${id}`);
              }}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              {loading ? "Loading graph..." : "Search for an entity to explore"}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
