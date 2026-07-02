import {
  MapPin,
  Globe,
} from "lucide-react";

export default function InstituteHero({ institute }) {
  if (!institute) return null;

  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-8 mb-8">

      <div className="flex justify-between items-start">

        <div className="flex gap-6">

          <div className="w-20 h-20 rounded-2xl bg-yellow-500 flex items-center justify-center text-5xl">
            {institute.type === "BITS" ? "🎓" : "🏛"}
          </div>

          <div>

            <h1 className="text-5xl font-bold text-white mb-2">
              {institute.name}
            </h1>

            <p className="text-xl text-slate-300 mb-3">
              {institute.type} Institute
            </p>

            <div className="flex flex-wrap gap-6 text-slate-400">

              <div className="flex items-center gap-2">
                <MapPin size={18} />
                {institute.city}, {institute.state}
              </div>

              {institute.website_url && (
                <a
                  href={institute.website_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 hover:text-yellow-400"
                >
                  <Globe size={18} />
                  Website
                </a>
              )}

            </div>

          </div>

        </div>

        <div className="bg-yellow-500/20 text-yellow-400 px-4 py-2 rounded-full text-sm font-semibold">
          {institute.type}
        </div>

      </div>

    </div>
  );
}