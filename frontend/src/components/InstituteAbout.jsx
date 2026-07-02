import {
  Award,
  Calendar,
  Globe,
  GraduationCap,
} from "lucide-react";

export default function InstituteAbout({ institute }) {
  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6 mt-8">

      <h2 className="text-2xl font-bold mb-6">
        About Institute
      </h2>

      <p className="text-slate-400 leading-8 mb-8">
        {institute.name} is one of India's premier engineering institutes.
        Faculty and institute information is loaded directly from the Faculty
        Search API.
      </p>

      <div className="space-y-5">

        <div className="flex items-center gap-4">
          <Calendar className="text-yellow-500" size={20} />
          <div>
            <p className="text-sm text-slate-400">City</p>
            <h4 className="font-semibold">
              {institute.city || "N/A"}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <GraduationCap className="text-yellow-500" size={20} />
          <div>
            <p className="text-sm text-slate-400">Institute Type</p>
            <h4 className="font-semibold">
              {institute.type}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Award className="text-yellow-500" size={20} />
          <div>
            <p className="text-sm text-slate-400">State</p>
            <h4 className="font-semibold">
              {institute.state || "N/A"}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Globe className="text-yellow-500" size={20} />
          <div>
            <p className="text-sm text-slate-400">Website</p>

            <a
              href={institute.website_url}
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-blue-400 hover:underline break-all"
            >
              {institute.website_url}
            </a>
          </div>
        </div>

      </div>

    </div>
  );
}