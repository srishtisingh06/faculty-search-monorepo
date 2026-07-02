import {
  MapPin,
  Users,
  Building2,
  BookOpen,
  ArrowRight,
  Globe,
} from "lucide-react";
import { Link } from "react-router-dom";

export default function InstituteCard({
  id,
  name,
  city,
  faculty,
  departments,
  publications,
  logo,
}) {
  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-8 hover:border-yellow-500 transition-all duration-300">

      {/* Header */}
      <div className="flex justify-between items-start">

        <div className="flex gap-5">

          <div className="w-16 h-16 rounded-2xl bg-[#1b3156] flex items-center justify-center text-3xl">
            {logo}
          </div>

          <div>

            <h2 className="text-3xl font-bold">
              {name}
            </h2>

            <div className="flex items-center gap-2 mt-2 text-slate-400">
              <MapPin size={16} />
              <span>{city}</span>
            </div>

          </div>

        </div>

        <Link
          to={`/institute/${id}`}
          className="bg-yellow-500 hover:bg-yellow-400 transition px-5 py-3 rounded-xl text-black font-semibold flex items-center gap-2"
        >
          View Institute
          <ArrowRight size={18} />
        </Link>

      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-5 mt-8">

        <div className="bg-[#1b3156] rounded-xl p-5">

          <div className="flex items-center gap-2 text-slate-300 mb-3">
            <Users size={18} />
            Faculty
          </div>

          <h3 className="text-3xl font-bold">
            {faculty}
          </h3>

        </div>

        <div className="bg-[#1b3156] rounded-xl p-5">

          <div className="flex items-center gap-2 text-slate-300 mb-3">
            <Building2 size={18} />
            Departments
          </div>

          <h3 className="text-3xl font-bold">
            {departments}
          </h3>

        </div>

        <div className="bg-[#1b3156] rounded-xl p-5">

          <div className="flex items-center gap-2 text-slate-300 mb-3">
            <BookOpen size={18} />
            Publications
          </div>

          <h3 className="text-3xl font-bold">
            {publications > 0 ? publications : "N/A"}
          </h3>

        </div>

      </div>

      {/* Footer */}
      <div className="mt-8 flex justify-between items-center">

        <p className="text-gray-400">
          Institute information loaded from Faculty Search API
        </p>

        <button className="flex items-center gap-2 border border-[#27406b] px-4 py-2 rounded-lg hover:border-yellow-500 transition">
          <Globe size={16} />
          Website
        </button>

      </div>

    </div>
  );
}