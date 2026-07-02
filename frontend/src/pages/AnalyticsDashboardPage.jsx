import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

import AnalyticsSummaryCards from "../components/AnalyticsSummaryCards";
import FacultyInstitutePieChart from "../components/FacultyInstitutePieChart";
import FacultyDepartmentBarChart from "../components/FacultyDepartmentBarChart";
import StateWiseBarChart from "../components/StateWiseBarChart";
import SearchTrendChart from "../components/SearchTrendChart";

const API = "http://127.0.0.1:8000";

export default function AnalyticsDashboardPage() {
  const [summary, setSummary] = useState(null);
  const [types, setTypes] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [states, setStates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/analytics/summary`).then((res) => res.json()),
      fetch(`${API}/analytics/institute-types`).then((res) => res.json()),
      fetch(`${API}/analytics/departments`).then((res) => res.json()),
      fetch(`${API}/analytics/states`).then((res) => res.json()),
    ])
      .then(([summaryData, typeData, departmentData, stateData]) => {
        setSummary(summaryData);
        setTypes(typeData);
        setDepartments(departmentData);
        setStates(stateData);
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
        Loading analytics...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#081225] text-white">
      <Navbar />

      <main className="max-w-[1600px] mx-auto px-10 py-10">
        <div className="mb-10">
          <h1 className="text-5xl font-bold mb-3">
            Analytics Dashboard
          </h1>

          <p className="text-slate-400 text-lg">
            Comprehensive insights into faculty data, publications and institutes.
          </p>
        </div>

        <AnalyticsSummaryCards summary={summary} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-10">
          <div className="bg-[#152542] rounded-2xl p-6 border border-[#29456d]">
            <h2 className="text-xl font-semibold mb-4">
              Faculty by Institute Type
            </h2>

            <FacultyInstitutePieChart data={types} />
          </div>

          <div className="bg-[#152542] rounded-2xl p-6 border border-[#29456d]">
            <h2 className="text-xl font-semibold mb-4">
              Faculty by Department
            </h2>

            <FacultyDepartmentBarChart data={departments} />
          </div>
        </div>

        <div className="mt-10 bg-[#152542] rounded-2xl p-6 border border-[#29456d]">
          <h2 className="text-xl font-semibold mb-4">
            State-wise Faculty Distribution
          </h2>

          <StateWiseBarChart data={states} />
        </div>

        <div className="mt-10 bg-[#152542] rounded-2xl p-6 border border-[#29456d]">
          <h2 className="text-xl font-semibold mb-4">
            Search Trends
          </h2>

          <SearchTrendChart />
        </div>
      </main>

      <Footer />
    </div>
  );
}