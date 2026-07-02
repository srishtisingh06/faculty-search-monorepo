import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function TopResearchers({ instituteId }) {
  const [faculty, setFaculty] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/institutes/${instituteId}/faculty`)
      .then((res) => res.json())
      .then((data) => {
        setFaculty(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [instituteId]);

  if (loading) {
    return (
      <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6">
        <h2 className="text-xl font-bold mb-6">Top Researchers</h2>
        <p className="text-slate-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6">

      <h2 className="text-xl font-bold mb-6">
        Faculty Members
      </h2>

      <div className="space-y-4">

        {faculty.map((f) => (

          <div
            key={f.id}
            className="bg-[#162847] border border-[#2b4570] rounded-xl p-4 flex justify-between items-center hover:border-yellow-500 transition"
          >

            <div className="flex gap-4">

              <img
                src={
                  f.profile_image ||
                  "https://ui-avatars.com/api/?name=" +
                    encodeURIComponent(f.faculty_name)
                }
                alt={f.faculty_name}
                className="w-14 h-14 rounded-lg object-cover"
              />

              <div>

                <h3 className="font-bold text-lg">
                  {f.faculty_name}
                </h3>

                <p className="text-slate-400 text-sm">
                  {f.designation || "Faculty"} •{" "}
                  {f.department || "Department"}
                </p>

              </div>

            </div>

            <Link
              to={`/faculty/${f.id}`}
              className="border border-[#36578f] hover:border-yellow-500 rounded-lg px-5 py-2 transition"
            >
              View Profile
            </Link>

          </div>

        ))}

      </div>

      <Link
        to="/faculty"
        className="block text-center w-full mt-6 bg-[#1b3156] hover:bg-[#27406b] rounded-xl py-3 font-semibold transition"
      >
        View All Faculty
      </Link>

    </div>
  );
}