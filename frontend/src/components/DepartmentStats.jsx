import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

const icons = ["💻", "📡", "⚡", "⚙️", "📐"];
const colors = [
  "bg-blue-600",
  "bg-purple-600",
  "bg-orange-500",
  "bg-green-600",
  "bg-pink-600",
];

export default function DepartmentStats() {
  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    fetch(`${API}/departments`)
      .then((res) => res.json())
      .then((data) => setDepartments(data))
      .catch(console.error);
  }, []);

  return (
    <>
      <div className="mb-10">
        <h1 className="text-5xl font-bold mb-4">
          Department Explorer
        </h1>

        <p className="text-slate-400 text-lg">
          Explore faculty and research across major engineering and science
          departments.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {departments.map((dept, index) => (
          <div
            key={dept.department}
            className="bg-[#11203d] border border-[#27406b] rounded-2xl p-8 text-center"
          >
            <div
              className={`w-20 h-20 mx-auto mb-6 rounded-xl ${
                colors[index % colors.length]
              } flex items-center justify-center text-4xl`}
            >
              {icons[index % icons.length]}
            </div>

            <h2 className="text-4xl font-bold">
              {dept.faculty}
            </h2>

            <p className="text-slate-400 mt-2">
              {dept.department}
            </p>
          </div>
        ))}
      </div>
    </>
  );
}