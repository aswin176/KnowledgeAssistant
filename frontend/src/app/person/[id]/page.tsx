"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GraphViewer } from "@/components/graph/graph-viewer";
import {
  api,
  type GraphResponse,
  type PersonDetail,
  type RelationshipSummary,
} from "@/lib/api";

export default function PersonDetailPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";
  const [person, setPerson] = useState<PersonDetail | null>(null);
  const [relationships, setRelationships] = useState<RelationshipSummary[]>([]);
  const [graph, setGraph] = useState<GraphResponse | null>(null);

  useEffect(() => {
    if (!id) return;
    api.getPerson(id).then((data) => {
      setPerson(data);
      setRelationships(data.relationships ?? []);
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
            Back to People
          </Link>
          <h1 className="mt-2 text-2xl font-semibold">{person.name ?? "Unnamed person"}</h1>
          {person.roll_number && (
            <p className="text-muted-foreground">Roll Number: {person.roll_number}</p>
          )}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {person.email && (
                <p>
                  <span className="font-medium">Email:</span> {person.email}
                </p>
              )}
              {person.mobile && (
                <p>
                  <span className="font-medium">Mobile:</span> {person.mobile}
                </p>
              )}
              {person.dob && (
                <p>
                  <span className="font-medium">DOB:</span> {person.dob}
                </p>
              )}
              {person.relationship_status && (
                <p>
                  <span className="font-medium">Status:</span> {person.relationship_status}
                </p>
              )}
              {typeof person.kids === "number" && (
                <p>
                  <span className="font-medium">Kids:</span> {person.kids}
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Relationships</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {relationships.map((relationship, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <span className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">
                      {relationship.type ?? "Related"}
                    </span>
                    <span>{relationship.node?.name ?? "Unknown"}</span>
                  </div>
                ))}
                {relationships.length === 0 && (
                  <p className="text-sm text-muted-foreground">No relationships found.</p>
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
              <GraphViewer nodes={graph.nodes} relationships={graph.relationships} centerId={id} />
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
