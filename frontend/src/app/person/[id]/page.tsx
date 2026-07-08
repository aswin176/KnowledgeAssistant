"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GraphViewer } from "@/components/graph/graph-viewer";
import { api } from "@/lib/api";

type PersonDetail = {
  id?: string;
  name?: string;
  title?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  marital_status?: string;
  has_children?: boolean;
  bio?: string;
  relationships?: Array<{ type?: string; node?: { name?: string } }>;
};

type GraphData = {
  nodes: Array<{ id: string; name?: string; _labels?: string[] }>;
  relationships: Array<{ type: string; start?: string; end?: string }>;
};

export default function PersonDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [person, setPerson] = useState<PersonDetail | null>(null);
  const [relationships, setRelationships] = useState<Array<{ type?: string; node?: { name?: string } }>>([]);
  const [graph, setGraph] = useState<GraphData | null>(null);

  useEffect(() => {
    if (!id) return;
    api.getPerson(id).then((data) => {
      setPerson(data);
      setRelationships(data.relationships || []);
    });
    api.exploreGraph(id, 1).then(setGraph);
  }, [id]);

  if (!person) {
    return (
      <DashboardLayout>
        <div className="p-6">Loading...</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <Link href="/person" className="text-sm text-muted-foreground hover:text-primary">
            ← Back to People
          </Link>
          <h1 className="text-2xl font-semibold mt-2">{person.name ?? "Unnamed person"}</h1>
          {person.title && <p className="text-muted-foreground">{person.title}</p>}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {person.email && <p><span className="font-medium">Email:</span> {person.email}</p>}
              {person.phone && <p><span className="font-medium">Phone:</span> {person.phone}</p>}
              {person.linkedin_url && (
                <p>
                  <span className="font-medium">LinkedIn:</span>{" "}
                  <a href={person.linkedin_url} className="text-primary hover:underline" target="_blank" rel="noopener">
                    {person.linkedin_url}
                  </a>
                </p>
              )}
              {person.marital_status && <p><span className="font-medium">Status:</span> {person.marital_status}</p>}
              {person.has_children != null && <p><span className="font-medium">Children:</span> {person.has_children ? "Yes" : "No"}</p>}
              {person.bio && <p className="mt-4 text-muted-foreground">{person.bio}</p>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Relationships</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {relationships.map((rel, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">
                      {rel.type ?? "Related"}
                    </span>
                    <span>{rel.node?.name ?? "Unknown"}</span>
                  </div>
                ))}
                {relationships.length === 0 && (
                  <p className="text-muted-foreground text-sm">No relationships found.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {graph && (
          <Card>
            <CardHeader>
              <CardTitle>Connection Graph</CardTitle>
            </CardHeader>
            <CardContent className="h-96">
              <GraphViewer
                nodes={graph.nodes}
                relationships={graph.relationships}
                centerId={id}
              />
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
