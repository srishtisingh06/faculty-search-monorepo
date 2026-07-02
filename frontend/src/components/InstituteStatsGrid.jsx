import {
  Users,
  BookOpen,
  Award,
  Trophy,
} from "lucide-react";

export default function InstituteStatsGrid({ institute }) {
  const stats = [
    {
      icon: <Users size={28} />,
      value: institute.faculty_count,
      label: "Faculty Members",
    },
    {
      icon: <BookOpen size={28} />,
      value:
        institute.publication_count > 0
          ? institute.publication_count
          : "N/A",
      label: "Publications",
    },
    {
      icon: <Award size={28} />,
      value: "Coming Soon",
      label: "Citations",
    },
    {
      icon: <Trophy size={28} />,
      value: "Coming Soon",
      label: "Avg h-index",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((item) => (
        <div
          key={item.label}
          className="bg-[#11203d] border border-[#27406b] rounded-2xl p-8 text-center hover:border-yellow-500 transition-all"
        >
          <div className="text-yellow-500 flex justify-center mb-4">
            {item.icon}
          </div>

          <h2 className="text-4xl font-bold text-white">
            {item.value}
          </h2>

          <p className="text-slate-400 mt-2">
            {item.label}
          </p>
        </div>
      ))}
    </div>
  );
}