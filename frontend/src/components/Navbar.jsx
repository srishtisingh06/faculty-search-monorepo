import { NavLink } from "react-router-dom";
import {
  Search,
  Brain,
  Building2,
  BookOpen,
  BarChart3,
  Shield,
  GraduationCap,
} from "lucide-react";

export default function Navbar() {
  const navItem =
    "flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200";

  const active =
    "bg-yellow-500 text-black font-semibold";

  const inactive =
    "text-slate-300 hover:text-yellow-400";

  return (
    <nav className="bg-[#081224] border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-[1650px] mx-auto px-8 h-16 flex items-center justify-between">

        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-yellow-500 flex items-center justify-center">
            <GraduationCap className="text-black" size={22} />
          </div>

          <div>
            <h1 className="text-yellow-400 font-bold text-xl">
              ADI
            </h1>

            <p className="text-[10px] text-slate-400">
              Academia Discovery India
            </p>
          </div>
        </NavLink>

        {/* Navigation */}
        <div className="hidden lg:flex items-center gap-2">

          <NavLink
            to="/faculty"
            className={({ isActive }) =>
              `${navItem} ${isActive ? active : inactive}`
            }
          >
            <Search size={17} />
            Search
          </NavLink>

          <NavLink
            to="/ai-assistant"
            className={({ isActive }) =>
              `${navItem} ${isActive ? active : inactive}`
            }
          >
            <Brain size={17} />
            AI Assistant
          </NavLink>

          <NavLink
            to="/institutes"
            className={({ isActive }) =>
              `${navItem} ${isActive ? active : inactive}`
            }
          >
            <Building2 size={17} />
            Institutes
          </NavLink>

          <NavLink
            to="/departments"
            className={({ isActive }) =>
              `${navItem} ${isActive ? active : inactive}`
            }
          >
            <BookOpen size={17} />
            Departments
          </NavLink>

          <NavLink
            to="/coverage"
            className={({ isActive }) =>
              `${navItem} ${isActive ? active : inactive}`
            }
          >
            <BarChart3 size={17} />
            Coverage
          </NavLink>

          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              `${navItem} ${isActive ? active : inactive}`
            }
          >
            <BarChart3 size={17} />
            Analytics
          </NavLink>

          <NavLink
            to="/admin"
            className={({ isActive }) =>
              `${navItem} ${isActive ? active : inactive}`
            }
          >
            <Shield size={17} />
            Admin
          </NavLink>

        </div>
      </div>
    </nav>
  );
}