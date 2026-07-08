"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent } from "@/components/ui/card";
import { api, type PersonListItem } from "@/lib/api";

export default function PersonListPage() {
  const [persons, setPersons] = useState<PersonListItem[]>([]);

  useEffect(() => {
    api.listPersons().then((data) => setPersons(data.items ?? []));
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-semibold">People</h1>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {persons.map((person) => (
            <Link key={person.id} href={`/person/${person.id}`}>
              <Card className="cursor-pointer transition-colors hover:border-primary">
                <CardContent className="p-4">
                  <h3 className="font-medium">{person.name}</h3>
                  {person.roll_number && (
                    <p className="text-sm text-muted-foreground">Roll No: {person.roll_number}</p>
                  )}
                  {person.email && (
                    <p className="mt-1 text-xs text-muted-foreground">{person.email}</p>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
