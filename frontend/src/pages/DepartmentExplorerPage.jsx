import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import DepartmentStats from "../components/DepartmentStats";
import DepartmentCard from "../components/DepartmentCard";

const API = "http://127.0.0.1:8000";

const colors = [
  {
    color: "bg-blue-600",
    border: "border-t-4 border-blue-500",
    icon: "💻",
  },
  {
    color: "bg-purple-600",
    border: "border-t-4 border-purple-500",
    icon: "📡",
  },
  {
    color: "bg-orange-500",
    border: "border-t-4 border-orange-500",
    icon: "⚡",
  },
  {
    color: "bg-green-600",
    border: "border-t-4 border-green-500",
    icon: "⚙️",
  },
  {
    color: "bg-pink-600",
    border: "border-t-4 border-pink-500",
    icon: "📐",
  },
];

export default function DepartmentExplorerPage() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/departments`)
      .then((res) => res.json())
      .then((data) => {
        setDepartments(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#081225] text-white">
      <Navbar />

      <main className="max-w-[1650px] mx-auto px-10 py-8">
        <DepartmentStats />

        {loading ? (
          <div className="text-center text-gray-400 py-20">
            Loading departments...
          </div>
        ) : (
          <div className="mt-10 space-y-8">
            {departments.map((dept, index) => {
              const theme = colors[index % colors.length];

              return (
                <DepartmentCard
                  key={dept.department}
                  color={theme.color}
                  border={theme.border}
                  icon={theme.icon}
                  title={dept.department}
                  faculty={dept.faculty}
                  publications={dept.publications}
                  institutes={dept.top_institutes}
                  researchAreas={dept.research_areas}
                />
              );
            })}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}