"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function PersonListPage() {
  const [persons, setPersons] = useState<{ id: string; name: string; title?: string; email?: string }[]>([]);

  useEffect(() => {
    api.listPersons().then((data) => setPersons(data.items || []));
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-semibold">People</h1>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {persons.map((p) => (
            <Link key={p.id} href={`/person/${p.id}`}>
              <Card className="hover:border-primary transition-colors cursor-pointer">
                <CardContent className="p-4">
                  <h3 className="font-medium">{p.name}</h3>
                  {p.title && <p className="text-sm text-muted-foreground">{p.title}</p>}
                  {p.email && <p className="text-xs text-muted-foreground mt-1">{p.email}</p>}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
