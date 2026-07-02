import {
  BookOpen,
  TrendingUp,
  Award,
  ExternalLink,
} from "lucide-react";

import { Link } from "react-router-dom";

export default function FacultyCard({
  id,
  name,
  title,
  department,
  institute,
  image,
  tags,
  publications,
  citations,
  hIndex,
  match,
  highlighted,
}) {
  return (
    <div
      className={`relative bg-[#11203d] border rounded-xl p-6 transition-all duration-300 ${
        highlighted
          ? "border-yellow-500"
          : "border-[#27406b]"
      }`}
    >
      <div className="absolute top-5 right-5 bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full text-xs font-bold">
        Match: {match}
      </div>

      <div className="flex gap-6">
        <img
          src={image}
          alt={name}
          className="w-24 h-24 rounded-xl object-cover"
        />

        <div className="flex-1">
          <h2 className="text-2xl font-bold text-white">
            {name}
          </h2>

          <p className="text-slate-300 mt-1">
            {title} • {department}
          </p>

          <p className="text-slate-400">
            {institute}
          </p>

          <div className="flex flex-wrap gap-2 mt-3">
            {tags.map((tag) => (
              <span
                key={tag}
                className="bg-blue-600 px-3 py-1 rounded-md text-xs"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="flex gap-8 mt-5 text-sm">
            <div className="flex items-center gap-2">
              <BookOpen size={16} />
              <span className="font-bold">
                {publications}
              </span>
              <span className="text-gray-400">
                Publications
              </span>
            </div>

            <div className="flex items-center gap-2">
              <TrendingUp size={16} />
              <span className="font-bold">
                {citations}
              </span>
              <span className="text-gray-400">
                Citations
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Award size={16} />
              <span className="font-bold">
                h-index: {hIndex}
              </span>
            </div>
          </div>

          <div className="flex gap-3 mt-5">

            <Link
              to={`/faculty/${id}`}
              className="bg-yellow-500 hover:bg-yellow-400 text-black px-4 py-2 rounded-lg font-semibold flex items-center gap-2"
            >
              View Profile
              <ExternalLink size={14} />
            </Link>

            <button className="border border-[#27406b] hover:border-yellow-500 px-4 py-2 rounded-lg">
              Contact
            </button>

          </div>

        </div>
      </div>
    </div>
  );
}