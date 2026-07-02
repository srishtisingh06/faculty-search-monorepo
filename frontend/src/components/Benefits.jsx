import { CheckCircle, Database } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Benefits() {
  const navigate = useNavigate();

  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16">

        <div>
          <h2 className="text-5xl font-bold text-white mb-10">
            Why Choose ADI?
          </h2>

          <div className="space-y-6 text-xl">

            <div className="flex gap-4 items-center text-slate-300">
              <CheckCircle className="text-amber-400" />
              Comprehensive coverage of 70+ premier institutions
            </div>

            <div className="flex gap-4 items-center text-slate-300">
              <CheckCircle className="text-amber-400" />
              AI-powered semantic search
            </div>

            <div className="flex gap-4 items-center text-slate-300">
              <CheckCircle className="text-amber-400" />
              Updated faculty profiles
            </div>

            <div className="flex gap-4 items-center text-slate-300">
              <CheckCircle className="text-amber-400" />
              Research collaboration discovery
            </div>

            <div className="flex gap-4 items-center text-slate-300">
              <CheckCircle className="text-amber-400" />
              Department-wise exploration
            </div>

            <div className="flex gap-4 items-center text-slate-300">
              <CheckCircle className="text-amber-400" />
              Real-time analytics and insights
            </div>

          </div>
        </div>

        <div className="bg-[#101c37] border border-slate-700 rounded-2xl p-10 hover:border-amber-500 hover:shadow-xl transition-all duration-300">
          <Database size={80} className="text-amber-400" />

          <h3 className="text-4xl font-bold text-white mt-6">
            Start Exploring
          </h3>

          <p className="text-slate-400 mt-4 text-lg">
            Access thousands of faculty profiles and discover research opportunities.
          </p>

          <div className="flex gap-4 mt-8">
            <button
              onClick={() => navigate("/faculty")}
              className="bg-amber-500 hover:bg-amber-400 hover:scale-105 transition-all duration-200 px-8 py-3 rounded-lg font-semibold"
            >
              Search Faculty
            </button>

            <button
              onClick={() => alert("AI Assistant coming soon!")}
              className="border border-slate-600 hover:border-amber-500 hover:scale-105 transition-all duration-200 px-8 py-3 rounded-lg text-white"
            >
              Try AI Assistant
            </button>
          </div>
        </div>

      </div>
    </section>
  );
}