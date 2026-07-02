import { useEffect, useState } from "react";

const colors = [
  "bg-blue-500",
  "bg-green-500",
  "bg-purple-500",
  "bg-orange-500",
  "bg-pink-500",
  "bg-yellow-500",
];

export default function ResearchAreas({ institute }) {
  const [areas, setAreas] = useState([]);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/institutes/${institute.id}/research-areas`)
      .then((res) => res.json())
      .then((data) => setAreas(data))
      .catch(console.error);
  }, [institute]);

  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6">
      <h2 className="text-2xl font-bold mb-6">
        Popular Research Areas
      </h2>

      <div className="space-y-5">
        {areas.length > 0 ? (
          areas.map((area, index) => (
            <div
              key={area.name}
              className="bg-[#1b3156] rounded-xl p-4 hover:border hover:border-yellow-500 transition-all cursor-pointer"
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      colors[index % colors.length]
                    }`}
                  ></div>

                  <h3 className="font-semibold">
                    {area.name}
                  </h3>
                </div>

                <span className="bg-[#27406b] px-3 py-1 rounded-full text-sm">
                  {area.faculty_count}
                </span>
              </div>
            </div>
          ))
        ) : (
          <p className="text-slate-400">
            No research areas available.
          </p>
        )}
      </div>
    </div>
  );
}