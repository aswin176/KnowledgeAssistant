"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent } from "@/components/ui/card";
import { api, type CompanyListItem } from "@/lib/api";

export default function CompanyListPage() {
  const [companies, setCompanies] = useState<CompanyListItem[]>([]);

  useEffect(() => {
    api.listCompanies().then((data) => setCompanies(data.items ?? []));
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-semibold">Companies</h1>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {companies.map((company) => (
            <Link key={company.id} href={`/company/${company.id}`}>
              <Card className="cursor-pointer transition-colors hover:border-primary">
                <CardContent className="p-4">
                  <h3 className="font-medium">{company.name}</h3>
                  {company.industry && (
                    <p className="text-sm text-muted-foreground">{company.industry}</p>
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
