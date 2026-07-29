import { LandingHeader } from "@/components/landing/LandingHeader";
import { Hero } from "@/components/landing/Hero";
import { FeatureGrid } from "@/components/landing/FeatureGrid";
import { Process } from "@/components/landing/Process";
import { CTASection } from "@/components/landing/CTASection";
import { LandingFooter } from "@/components/landing/LandingFooter";

export default function Landing() {
  return (
    <div className="min-h-screen bg-ink-950">
      <LandingHeader />
      <main>
        <Hero />
        <FeatureGrid />
        <Process />
        <CTASection />
      </main>
      <LandingFooter />
    </div>
  );
}
