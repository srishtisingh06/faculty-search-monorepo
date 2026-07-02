import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import FacultyFilters from "../components/FacultyFilters";
import FacultyCard from "../components/FacultyCard";

import { useSearchParams } from "react-router-dom";
const API_BASE = "http://127.0.0.1:8000";

export default function FacultySearchPage() {
  const [query, setQuery] = useState("machine");
  const [facultyList, setFacultyList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchParams] = useSearchParams();

  const initialQuery = searchParams.get("q") || "";
  const initialDepartment = searchParams.get("department") || "";

  
  async function fetchFaculty(searchText = query) {
    const text = searchText.trim();

if (!text) {
  setFacultyList([]);
  return;
}

    try {
      setLoading(true);
      setError("");

      const res = await fetch(
        `${API_BASE}/search?q=${encodeURIComponent(text)}&top_k=10`
      );

      if (!res.ok) {
        throw new Error("Failed to fetch faculty");
      }

      const data = await res.json();

      const mappedData = data.map((item, index) => ({
        id: item.faculty_id,
        name: item.faculty_name,
        title: item.designation || "Faculty",
        department: item.department || "Not Available",
        institute: item.institute || "Not Available",
        image:
          index % 2 === 0
            ? "https://randomuser.me/api/portraits/men/32.jpg"
            : "https://randomuser.me/api/portraits/women/44.jpg",
        tags: [item.department || "Research"],
        publications: "-",
        citations: "-",
        hIndex: "-",
        match: `${Math.round(item.score * 100)}%`,
        highlighted: index === 0,
      }));

      setFacultyList(mappedData);
    } catch (err) {
      setError("Unable to load faculty data.");
      setFacultyList([]);
    } finally {
      setLoading(false);
    }
  }

 useEffect(() => {
  if (initialDepartment) {
    fetchFaculty(initialDepartment);
  } else if (initialQuery) {
    fetchFaculty(initialQuery);
  }
}, [initialQuery, initialDepartment]);

  function handleSearch(e) {
    e.preventDefault();
    fetchFaculty(query);
  }

  return (
    <div className="bg-[#081225] min-h-screen text-white">
      <Navbar />

      <div className="max-w-[1200px] mx-auto px-6 py-8">
        <h1 className="text-5xl font-bold mb-8">Faculty Search</h1>

        <form onSubmit={handleSearch} className="flex gap-4 mb-8">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name, research area, or keywords..."
            className="flex-1 bg-[#11203d] border border-[#27406b] rounded-xl px-5 py-4 text-white outline-none focus:border-yellow-500"
          />

          <button
            type="submit"
            className="bg-yellow-500 hover:bg-yellow-400 text-black px-8 rounded-xl font-semibold"
          >
            Search
          </button>
        </form>

        <div className="mt-8 flex justify-between items-center mb-6">
          <p className="text-gray-400">
            Found{" "}
            <span className="font-bold text-white">
              {facultyList.length}
            </span>{" "}
            faculty members
          </p>

          <select className="bg-[#11203d] border border-[#27406b] px-4 py-3 rounded-lg">
            <option>Sort by Relevance</option>
            <option>Publications</option>
            <option>Citations</option>
          </select>
        </div>

        {loading && (
          <p className="text-yellow-400 text-lg mb-6">Loading faculty...</p>
        )}

        {error && (
          <p className="text-red-400 text-lg mb-6">{error}</p>
        )}

        {!loading && !error && facultyList.length === 0 && (
          <p className="text-slate-400 text-lg">No faculty found.</p>
        )}

        {!loading && facultyList.length > 0 && (
          <div className="flex gap-8 items-start">
            <FacultyFilters />

            <div className="flex-1 space-y-8">
              {facultyList.map((faculty) => (
                <FacultyCard key={faculty.id} {...faculty} />
              ))}
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
}