import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import StatsSection from "../components/StatsSection";
import HowItWorks from "../components/HowItWorks";
import Benefits from "../components/Benefits";
import CTASection from "../components/CTASection";
import Footer from "../components/Footer";
export default function LandingPage() {
  return (
    <div className="bg-[#071126] min-h-screen">
      <Navbar />
      <Hero />
      <StatsSection />
      <HowItWorks />
      <Benefits />
      <CTASection />
      
<Footer />
    </div>
  );
}
