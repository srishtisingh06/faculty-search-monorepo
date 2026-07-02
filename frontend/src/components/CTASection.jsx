import { useNavigate } from "react-router-dom";

export default function CTASection() {
  const navigate = useNavigate();

  return (
    <section className="py-20">
      <div className="max-w-6xl mx-auto px-6">

        <div className="bg-gradient-to-r from-slate-800 to-slate-700 border border-amber-600 rounded-3xl p-16 text-center hover:shadow-2xl transition-all duration-300">

          <h2 className="text-5xl font-bold text-white">
            Ready to Discover Researchers?
          </h2>

          <p className="text-slate-300 text-xl mt-6">
            Join thousands of students, researchers and academics.
          </p>

          <div className="flex justify-center gap-4 mt-10">
            <button
              onClick={() => navigate("/faculty")}
              className="bg-amber-500 hover:bg-amber-400 hover:scale-105 transition-all duration-200 px-8 py-3 rounded-lg font-semibold"
            >
              Start Searching
            </button>

            <button
              onClick={() => navigate("/institutes")}
              className="border border-slate-500 hover:border-amber-500 hover:scale-105 transition-all duration-200 px-8 py-3 rounded-lg text-white"
            >
              Browse Institutes
            </button>
          </div>

        </div>
      </div>
    </section>
  );
}