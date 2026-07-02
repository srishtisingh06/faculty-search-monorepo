import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { SearchX, RotateCcw, Home } from "lucide-react";

export default function NoResultsPage() {
  return (
    <div className="bg-[#081225] min-h-screen text-white">

      <Navbar />

      <div className="max-w-[1650px] mx-auto px-10 py-20 flex justify-center">

        <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-12 text-center max-w-2xl w-full">

          {/* Icon */}
          <div className="w-24 h-24 mx-auto rounded-full bg-[#1b3156] flex items-center justify-center mb-8">
            <SearchX size={50} className="text-yellow-500" />
          </div>

          {/* Heading */}
          <h1 className="text-5xl font-bold mb-5">
            No Results Found
          </h1>

          {/* Description */}
          <p className="text-slate-400 text-lg leading-8 mb-10">
            We couldn't find any faculty members, institutes or departments
            matching your search. Try changing your keywords or filters and
            search again.
          </p>

          {/* Suggestions */}
          <div className="bg-[#1b3156] rounded-xl p-6 text-left mb-10">

            <h2 className="text-xl font-semibold mb-4">
              Suggestions
            </h2>

            <ul className="space-y-3 text-slate-300">

              <li>• Check for spelling mistakes.</li>

              <li>• Use broader keywords.</li>

              <li>• Remove some filters.</li>

              <li>• Search by institute or department.</li>

            </ul>

          </div>

          {/* Buttons */}
          <div className="flex flex-wrap justify-center gap-4">

            <button className="bg-yellow-500 hover:bg-yellow-400 transition px-6 py-3 rounded-xl text-black font-semibold flex items-center gap-2">

              <RotateCcw size={18} />

              Clear Filters

            </button>

            <button className="border border-[#27406b] hover:border-yellow-500 transition px-6 py-3 rounded-xl flex items-center gap-2">

              <Home size={18} />

              Back Home

            </button>

          </div>

        </div>

      </div>

      <Footer />

    </div>
  );
}