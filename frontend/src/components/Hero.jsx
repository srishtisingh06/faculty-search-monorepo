import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Hero() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    const q = query.trim();

    if (q) {
      navigate(`/faculty?q=${encodeURIComponent(query)}`);
    } else {
      navigate("/faculty");;
    }
  };

  const goToDepartment = (department) => {
    navigate(`/faculty?department=${encodeURIComponent(department)}`);
  };

  return (
    <section className="text-center py-24 px-6">

      <div className="inline-block px-4 py-1 rounded-full bg-amber-500/20 text-amber-400 text-sm mb-6">
        AI Powered Academic Search
      </div>

      <h1 className="text-5xl font-bold text-white max-w-4xl mx-auto">
        Discover India's Top Academic Researchers
      </h1>

      <p className="text-slate-400 mt-6 max-w-2xl mx-auto">
        Search faculty profiles from IITs, NITs, BITS and premier engineering colleges.
      </p>

      <div className="mt-10 flex justify-center">

        <input
          autoFocus
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearch();
          }}
          placeholder="Search faculty by name, research area..."
          className="w-[500px] px-4 py-3 bg-[#0d1b34] border border-slate-700 rounded-l-lg text-white"
        />

        <button
          onClick={handleSearch}
          className="bg-amber-500 hover:bg-amber-400 transition px-6 rounded-r-lg font-semibold"
        >
          Search
        </button>

      </div>

      <div className="mt-6 flex justify-center gap-2 flex-wrap">

        <button
          onClick={() => goToDepartment("Computer Science")}
          className="px-3 py-1 text-sm bg-[#11203d] border border-slate-700 rounded-md text-white hover:border-amber-500 hover:scale-105 transition"
        >
          Computer Science
        </button>

        <button
          onClick={() => goToDepartment("Electronics")}
          className="px-3 py-1 text-sm bg-[#11203d] border border-slate-700 rounded-md text-white hover:border-amber-500 hover:scale-105 transition"
        >
          Electronics
        </button>

        <button
          onClick={() => goToDepartment("Electrical")}
          className="px-3 py-1 text-sm bg-[#11203d] border border-slate-700 rounded-md text-white hover:border-amber-500 hover:scale-105 transition"
        >
          Electrical
        </button>

        <button
          onClick={() => goToDepartment("Mechanical")}
          className="px-3 py-1 text-sm bg-[#11203d] border border-slate-700 rounded-md text-white hover:border-amber-500 hover:scale-105 transition"
        >
          Mechanical
        </button>

        <button
          onClick={() => goToDepartment("Mathematics")}
          className="px-3 py-1 text-sm bg-[#11203d] border border-slate-700 rounded-md text-white hover:border-amber-500 hover:scale-105 transition"
        >
          Mathematics
        </button>

      </div>

    </section>
  );
}