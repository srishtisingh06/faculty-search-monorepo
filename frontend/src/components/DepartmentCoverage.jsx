import { useEffect, useState } from "react";

const colors = [
  {
    color: "bg-yellow-500",
    dot: "bg-yellow-500",
  },
  {
    color: "bg-blue-500",
    dot: "bg-blue-500",
  },
  {
    color: "bg-green-500",
    dot: "bg-green-500",
  },
  {
    color: "bg-purple-500",
    dot: "bg-purple-500",
  },
  {
    color: "bg-pink-500",
    dot: "bg-pink-500",
  },
];

export default function DepartmentCoverage({ institute }) {
  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    fetch(
      `http://127.0.0.1:8000/institutes/${institute.id}/departments`
    )
      .then((res) => res.json())
      .then((data) => setDepartments(data))
      .catch(console.error);
  }, [institute]);

  const maxFaculty =
    departments.length > 0
      ? Math.max(...departments.map((d) => d.faculty_count))
      : 1;

  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6">

      <h2 className="text-2xl font-bold mb-8">
        Department Coverage
      </h2>

      <div className="space-y-8">

        {departments.map((dept, index) => {
          const style = colors[index % colors.length];

          const progress =
            (dept.faculty_count / maxFaculty) * 100;

          return (
            <div key={dept.id}>

              <div className="flex justify-between items-center mb-3">

                <div className="flex items-center gap-3">

                  <div
                    className={`w-3 h-3 rounded-full ${style.dot}`}
                  ></div>

                  <h3 className="font-semibold text-lg">
                    {dept.canonical_name}
                  </h3>

                </div>

                <p className="text-slate-400 text-sm">

                  {dept.faculty_count} faculty

                  &nbsp;&nbsp;

                  {dept.publication_count} publications

                </p>

              </div>

              <div className="h-3 rounded-full bg-[#4a412c] overflow-hidden">

                <div
                  className={style.color}
                  style={{
                    width: `${progress}%`,
                    height: "100%",
                  }}
                />

              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
}