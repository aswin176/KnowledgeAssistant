"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function CompanyListPage() {
  const [companies, setCompanies] = useState<{ id: string; name: string; industry?: string }[]>([]);

  useEffect(() => {
    api.listCompanies().then((data) => setCompanies(data.items || []));
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-semibold">Companies</h1>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {companies.map((c) => (
            <Link key={c.id} href={`/company/${c.id}`}>
              <Card className="hover:border-primary transition-colors cursor-pointer">
                <CardContent className="p-4">
                  <h3 className="font-medium">{c.name}</h3>
                  {c.industry && <p className="text-sm text-muted-foreground">{c.industry}</p>}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
