import { useEffect, useMemo, useState } from "react";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import InstituteStats from "../components/InstituteStats";
import InstituteTabs from "../components/InstituteTabs";
import InstituteCard from "../components/InstituteCard";

const API = "http://127.0.0.1:8000";

export default function InstitutesDirectoryPage() {
  const [institutes, setInstitutes] = useState([]);
  const [selectedType, setSelectedType] = useState("ALL");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
  fetch(`${API}/institutes`)
    .then((res) => res.json())
    .then((data) => {
      console.log("Institutes API:", data);

      setInstitutes(data);
      setLoading(false);
    })
    .catch((err) => {
      console.error(err);
      setLoading(false);
    });
}, []);

  const filtered = useMemo(() => {
    return institutes.filter((item) => {
      const typeMatch =
        selectedType === "ALL" || item.type === selectedType;

      const searchMatch =
        item.name.toLowerCase().includes(search.toLowerCase());

      return typeMatch && searchMatch;
    });
  }, [institutes, selectedType, search]);

  return (
    <div className="min-h-screen bg-[#081225] text-white">
      <Navbar />

      <main className="max-w-[1650px] mx-auto px-10 py-8">

        <InstituteStats
          search={search}
          setSearch={setSearch}
        />

        <InstituteTabs
          selected={selectedType}
          setSelected={setSelectedType}
        />

        {loading ? (
          <div className="text-center text-gray-400 py-20">
            Loading institutes...
          </div>
        ) : (
          <div className="space-y-8">

            {filtered.map((item) => (
              <InstituteCard
                key={item.id}
                id={item.id}
                name={item.name}
                city={`${item.city}, ${item.state}`}
                faculty={item.faculty_count}
                departments={item.department_count}
                publications={item.publication_count}
                type={item.type}
                logo={item.type === "BITS" ? "🎓" : "🏛"}
              />
            ))}

          </div>
        )}

      </main>

      <Footer />
    </div>
  );
}