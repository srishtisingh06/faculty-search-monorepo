export default function FacultyFilters() {
  return (
    <div className="w-64 bg-[#11203d] border border-[#27406b] rounded-xl p-6 h-fit">

      <h2 className="text-white text-2xl font-bold mb-8">
        Filters
      </h2>

      {/* Institute Type */}

      <div className="mb-10">

        <h3 className="text-slate-300 text-sm uppercase tracking-wide mb-4">
          Institute Type
        </h3>

        <div className="space-y-3 text-slate-300">

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>IIT</span>
            </div>

            <span className="text-xs text-slate-500">
              20
            </span>
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>NIT</span>
            </div>

            <span className="text-xs text-slate-500">
              35
            </span>
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>BITS</span>
            </div>

            <span className="text-xs text-slate-500">
              5
            </span>
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>Tier-1</span>
            </div>

            <span className="text-xs text-slate-500">
              10
            </span>
          </label>

        </div>

      </div>

      {/* Department */}

      <div className="mb-8">

        <h3 className="text-slate-300 text-sm uppercase tracking-wide mb-4">
          Department
        </h3>

        <div className="space-y-3 text-slate-300">

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>Computer Science</span>
            </div>

            <span className="text-xs text-slate-500">
              1200
            </span>
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>Electronics</span>
            </div>

            <span className="text-xs text-slate-500">
              950
            </span>
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>Electrical</span>
            </div>

            <span className="text-xs text-slate-500">
              890
            </span>
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>Mechanical</span>
            </div>

            <span className="text-xs text-slate-500">
              1100
            </span>
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div className="flex items-center gap-2">
              <input type="checkbox" />
              <span>Mathematics</span>
            </div>

            <span className="text-xs text-slate-500">
              860
            </span>
          </label>

        </div>

      </div>

      {/* Button */}

      <button className="w-full mt-4 border border-[#27406b] rounded-lg py-2 hover:border-yellow-500 transition-all">
        Clear All Filters
      </button>

    </div>
  );
}