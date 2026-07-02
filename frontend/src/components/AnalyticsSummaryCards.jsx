import {
  Building2,
  Users,
  GraduationCap,
  BookOpen,
} from "lucide-react";

export default function AnalyticsSummaryCards({ summary }) {
  if (!summary) return null;

  const cards = [
    {
      title: "Total Institutes",
      value: summary.institutes,
      icon: Building2,
      color: "text-blue-400",
    },
    {
      title: "Total Faculty",
      value: summary.faculty,
      icon: Users,
      color: "text-purple-400",
    },
    {
      title: "Departments",
      value: summary.departments,
      icon: GraduationCap,
      color: "text-green-400",
    },
    {
      title: "Publications",
      value: summary.publications,
      icon: BookOpen,
      color: "text-yellow-400",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      {cards.map((card) => {
        const Icon = card.icon;

        return (
          <div
            key={card.title}
            className="bg-[#152542] border border-[#2d4b78] rounded-2xl p-6"
          >
            <div className="flex justify-between items-center">
              <Icon className={`w-8 h-8 ${card.color}`} />

              <span className="text-green-400 text-sm font-semibold">
                Live
              </span>
            </div>

            <h2 className="text-4xl font-bold text-white mt-6">
              {card.value}
            </h2>

            <p className="text-slate-400 mt-2">
              {card.title}
            </p>
          </div>
        );
      })}
    </div>
  );
}