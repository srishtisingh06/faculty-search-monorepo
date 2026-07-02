export default function CoverageDepartmentCoverage({ departments }) {
  return (
    <section className="mb-14">

      <h2 className="text-4xl font-bold mb-8">
        Department Coverage
      </h2>

      <div className="bg-[#12203d] border border-[#28426d] rounded-2xl p-8">

        <div className="space-y-8">

          {departments.map((dept) => {

            // Temporary coverage calculation
            const percentage = Math.min(
              100,
              Math.round((dept.faculty / 412) * 100)
            );

            return (
              <div key={dept.department}>

                <div className="flex justify-between items-center mb-3">

                  <div>

                    <h3 className="text-xl font-semibold">
                      {dept.department}
                    </h3>

                    <p className="text-slate-400 text-sm">
                      {dept.faculty} Faculty • {dept.publications} Publications
                    </p>

                  </div>

                  <div className="text-right">

                    <p className="font-bold text-lg">
                      {percentage}%
                    </p>

                  </div>

                </div>

                <div className="w-full h-3 bg-[#2f3e5c] rounded-full">

                  <div
                    className="h-3 bg-yellow-500 rounded-full transition-all"
                    style={{
                      width: `${percentage}%`,
                    }}
                  />

                </div>

              </div>
            );
          })}

        </div>

      </div>

    </section>
  );
}