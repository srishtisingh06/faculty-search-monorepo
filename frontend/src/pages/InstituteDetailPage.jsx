import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

import InstituteHero from "../components/InstituteHero";
import InstituteStatsGrid from "../components/InstituteStatsGrid";
import DepartmentCoverage from "../components/DepartmentCoverage";
import ResearchAreas from "../components/ResearchAreas";
import TopResearchers from "../components/TopResearchers";
import QuickActions from "../components/QuickActions";
import InstituteAbout from "../components/InstituteAbout";

export default function InstituteDetailPage() {
  const { id } = useParams();

  const [institute, setInstitute] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/institutes/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load institute");
        return res.json();
      })
      .then((data) => {
        setInstitute(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#081225] text-white flex items-center justify-center text-2xl">
        Loading...
      </div>
    );
  }

  if (!institute) {
    return (
      <div className="min-h-screen bg-[#081225] text-white flex items-center justify-center text-2xl">
        Institute not found.
      </div>
    );
  }

  return (
    <div className="bg-[#081225] min-h-screen text-white">
      <Navbar />

      <div className="max-w-[1650px] mx-auto px-10 py-8">

        <InstituteHero institute={institute} />

        <InstituteStatsGrid institute={institute} />

        <div className="grid lg:grid-cols-3 gap-8 mt-8">

          <div className="lg:col-span-2 space-y-8">
            <DepartmentCoverage institute={institute} />
           <TopResearchers instituteId={id} />
          </div>

          <div className="space-y-8">
            <ResearchAreas institute={institute} />
            <QuickActions institute={institute} />
            <InstituteAbout institute={institute} />
          </div>

        </div>

      </div>

      <Footer />
    </div>
  );
}