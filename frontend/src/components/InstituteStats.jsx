import { useEffect, useState } from "react";

export default function InstituteStats({ search, setSearch }) {
  const [stats, setStats] = useState({
    institutes: 0,
    faculty: 0,
    departments: 5,
    publications: 0,
  });

 useEffect(() => {
  fetch("http://127.0.0.1:8000/stats")
    .then((res) => res.json())
    .then((data) => {
      setStats({
        institutes: data.institutes,
        faculty: data.faculty,
        departments: data.departments,
        publications: data.publications,
      });
    })
    .catch((err) => console.error(err));
}, []);

  const cards = [
    {
      value: stats.institutes,
      label: "Total Institutes",
      icon: "🏛",
    },
    {
      value: stats.faculty,
      label: "Faculty Members",
      icon: "👨‍🏫",
    },
    {
      value: stats.departments,
      label: "Departments",
      icon: "🏢",
    },
    {
      value: stats.publications,
      label: "Publications",
      icon: "📈",
    },
  ];

  return (
    <>
      {/* Heading */}
      <div className="mb-8">
        <h1 className="text-5xl font-bold text-white mb-3">
          Institutes Directory
        </h1>

        <p className="text-slate-400 text-lg">
          Browse faculty profiles from premier engineering institutes across
          India.
        </p>
      </div>

      {/* Search */}
      <div className="mb-8">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search institutes..."
          className="w-full max-w-xl bg-[#11203d] border border-[#27406b] rounded-xl px-5 py-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-yellow-500 transition"
        />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {cards.map((item) => (
          <div
            key={item.label}
            className="bg-[#11203d] border border-[#27406b] rounded-2xl p-8 text-center hover:border-yellow-500 hover:-translate-y-1 transition-all duration-300"
          >
            <div className="w-16 h-16 mx-auto mb-5 rounded-xl bg-[#1b3156] flex items-center justify-center text-3xl">
              {item.icon}
            </div>

            <h2 className="text-4xl font-bold text-white mb-2">
              {item.value}
            </h2>

            <p className="text-slate-400">{item.label}</p>
          </div>
        ))}
      </div>
    </>
  );
}