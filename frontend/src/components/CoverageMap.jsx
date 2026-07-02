export default function CoverageMap({ coverage }) {
  return (
    <section className="mb-10">

      <h2 className="text-4xl font-bold mb-8">
        India Coverage Overview
      </h2>

      <div className="bg-[#12203d] border border-[#28426d] rounded-2xl p-10">

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">

          <div className="text-center">
            <h3 className="text-5xl font-bold text-yellow-400">
              {coverage.institutes}
            </h3>
            <p className="text-slate-400 mt-2">
              Institutes
            </p>
          </div>

          <div className="text-center">
            <h3 className="text-5xl font-bold text-yellow-400">
              {coverage.faculty}
            </h3>
            <p className="text-slate-400 mt-2">
              Faculty
            </p>
          </div>

          <div className="text-center">
            <h3 className="text-5xl font-bold text-yellow-400">
              {coverage.departments}
            </h3>
            <p className="text-slate-400 mt-2">
              Departments
            </p>
          </div>

          <div className="text-center">
            <h3 className="text-5xl font-bold text-yellow-400">
              {coverage.publications}
            </h3>
            <p className="text-slate-400 mt-2">
              Publications
            </p>
          </div>

        </div>

        <div className="mt-12 border-2 border-dashed border-[#3c5b91] rounded-2xl h-[400px] flex items-center justify-center">

          <div className="text-center">

            <h3 className="text-3xl font-bold mb-3">
              🗺 India Coverage Map
            </h3>

            <p className="text-slate-400">
              Interactive India map will be integrated here.
            </p>

          </div>

        </div>

      </div>

    </section>
  );
}