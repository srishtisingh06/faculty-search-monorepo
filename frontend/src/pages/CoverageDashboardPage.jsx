import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

import CoverageSummaryCards from "../components/CoverageSummaryCards";
import InstituteTypeCoverage from "../components/InstituteTypeCoverage";
import DepartmentCoverage from "../components/CoverageDepartmentCoverage";
import StateCoverage from "../components/StateCoverage";
import CoverageMap from "../components/CoverageMap";

const API = "http://127.0.0.1:8000";

export default function CoverageDashboardPage() {
  const [coverage, setCoverage] = useState(null);
  const [instituteTypes, setInstituteTypes] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/coverage`).then((res) => res.json()),
      fetch(`${API}/institute-type-coverage`).then((res) => res.json()),
      fetch(`${API}/department-coverage`).then((res) => res.json()),
    ])
      .then(([coverageData, instituteTypeData, departmentData]) => {
        setCoverage(coverageData);
        setInstituteTypes(instituteTypeData);
        setDepartments(departmentData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#081225] text-white flex items-center justify-center text-2xl">
        Loading coverage...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#081225] text-white">
      <Navbar />

      <main className="max-w-[1600px] mx-auto px-10 py-10">
        <div className="mb-10">
          <h1 className="text-5xl font-bold mb-3">
            Coverage Dashboard
          </h1>

          <p className="text-slate-400 text-lg">
            Comprehensive overview of institute and department coverage across India
          </p>
        </div>

        {coverage && <CoverageSummaryCards coverage={coverage} />}

        {instituteTypes && (
          <InstituteTypeCoverage instituteTypes={instituteTypes} />
        )}

        <DepartmentCoverage departments={departments} />

        <StateCoverage />

        {coverage && <CoverageMap coverage={coverage} />}
      </main>

      <Footer />
    </div>
  );
}