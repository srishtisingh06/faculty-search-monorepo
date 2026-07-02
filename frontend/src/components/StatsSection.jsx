import { useEffect, useState } from "react";
import { Building2, Users, BookOpen, Database } from "lucide-react";

const API = "http://127.0.0.1:8000";

export default function StatsSection() {
  const [stats, setStats] = useState({
    institutes: 0,
    faculty: 0,
    publications: 0,
    departments: 0,
  });

  useEffect(() => {
    fetch(`${API}/stats`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load stats");
        return res.json();
      })
      .then((data) => {
        setStats(data);
      })
      .catch((err) => {
        console.error(err);
      });
  }, []);

  const cards = [
    {
      title: stats.institutes,
      label: "Institutes",
      icon: Building2,
    },
    {
      title: stats.faculty,
      label: "Faculty Profiles",
      icon: Users,
    },
    {
      title: stats.publications,
      label: "Publications",
      icon: BookOpen,
    },
    {
      title: stats.departments,
      label: "Departments",
      icon: Database,
    },
  ];

  return (
    <section className="py-16 bg-[#08142d]">
      <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-4 gap-6">
        {cards.map((item) => (
          <div
            key={item.label}
            className="border border-slate-700 rounded-xl p-6 text-center bg-[#101a36]"
          >
            <item.icon
              className="mx-auto text-amber-400 mb-3"
              size={32}
            />

            <h2 className="text-3xl font-bold text-white">
              {item.title}
            </h2>

            <p className="text-slate-400 text-sm mt-1">
              {item.label}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}