import { SiteFooter } from "@/components/SiteFooter";
import { SiteNav } from "@/components/SiteNav";

export default function SiteLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <SiteNav />
      <main>{children}</main>
      <SiteFooter />
    </div>
  );
}
