import {
  GraduationCap,
  Search,
  Brain,
  Building2,
  BookOpen,
  BarChart3,
} from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-[#07111f] border-t border-slate-800 mt-20">

      <div className="max-w-[1600px] mx-auto px-8 py-16">

        <div className="grid md:grid-cols-4 gap-12">

          {/* Logo */}

          <div>

            <div className="flex items-center gap-3 mb-5">

              <div className="w-12 h-12 rounded-xl bg-yellow-500 flex items-center justify-center">

                <GraduationCap
                  size={24}
                  className="text-black"
                />

              </div>

              <div>

                <h2 className="text-2xl font-bold text-yellow-400">
                  ADI
                </h2>

                <p className="text-xs text-slate-400">
                  Academia Discovery India
                </p>

              </div>

            </div>

            <p className="text-slate-400 leading-7">
              India's AI-powered academic discovery platform connecting
              researchers, faculty, students and institutions.
            </p>

          </div>

          {/* Features */}

          <div>

            <h3 className="text-xl font-semibold mb-5">
              Features
            </h3>

            <ul className="space-y-4 text-slate-400">

              <li className="flex items-center gap-2">
                <Search size={16} />
                Faculty Search
              </li>

              <li className="flex items-center gap-2">
                <Brain size={16} />
                AI Assistant
              </li>

              <li className="flex items-center gap-2">
                <Building2 size={16} />
                Institutes
              </li>

              <li className="flex items-center gap-2">
                <BarChart3 size={16} />
                Analytics
              </li>

            </ul>

          </div>

          {/* Coverage */}

          <div>

            <h3 className="text-xl font-semibold mb-5">
              Coverage
            </h3>

            <ul className="space-y-4 text-slate-400">

              <li>23 IITs</li>

              <li>31 NITs</li>

              <li>BITS Pilani Campuses</li>

              <li>Tier-1 Engineering Colleges</li>

            </ul>

          </div>

          {/* Departments */}

          <div>

            <h3 className="text-xl font-semibold mb-5">
              Departments
            </h3>

            <ul className="space-y-4 text-slate-400">

              <li>Computer Science</li>

              <li>Electronics</li>

              <li>Electrical</li>

              <li>Mechanical</li>

              <li>Mathematics</li>

            </ul>

          </div>

        </div>

        {/* Bottom */}

        <div className="border-t border-slate-800 mt-14 pt-8 flex flex-col md:flex-row justify-between items-center">

          <p className="text-slate-400">
            © 2026 ADI • Academia Discovery India
          </p>

          <p className="text-slate-500 mt-4 md:mt-0">
            Built with React • Tailwind CSS • FastAPI
          </p>

        </div>

      </div>

    </footer>
  );
}