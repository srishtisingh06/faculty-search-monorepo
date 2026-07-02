export default function InstituteTypeCoverage({ instituteTypes }) {
  const sections = [
    {
      title: "IIT",
      data: instituteTypes.iit,
    },
    {
      title: "NIT",
      data: instituteTypes.nit,
    },
    {
      title: "BITS",
      data: instituteTypes.bits,
    },
  ];

  return (
    <section className="mb-14">

      <h2 className="text-4xl font-bold mb-8">
        Institute Type Coverage
      </h2>

      <div className="grid grid-cols-3 gap-8">

        {sections.map((section) => (

          <div
            key={section.title}
            className="bg-[#12203d] border border-[#28426d] rounded-2xl p-6"
          >

            <div className="flex justify-between items-center mb-5">

              <h3 className="text-3xl font-bold">
                {section.title}
              </h3>

              <span className="bg-[#274d88] px-3 py-1 rounded-full">
                {section.data.length}
              </span>

            </div>

            <div className="space-y-5">

              {section.data.length === 0 && (
                <p className="text-slate-400">
                  No Institutes Found
                </p>
              )}

              {section.data.map((item) => (

                <div
                  key={item.name}
                  className="bg-[#1a2d4f] rounded-xl p-4"
                >

                  <div className="flex justify-between items-center">

                    <div>

                      <h4 className="font-semibold">
                        {item.name}
                      </h4>

                      <p className="text-slate-400 text-sm mt-1">
                        {item.faculty} Faculty
                      </p>

                    </div>

                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        item.coverage >= 90
                          ? "bg-green-700"
                          : item.coverage >= 60
                          ? "bg-yellow-600"
                          : "bg-red-600"
                      }`}
                    >
                      {item.coverage}%
                    </span>

                  </div>

                  <div className="w-full h-2 bg-[#2f3e5c] rounded-full mt-4">

                    <div
                      className="h-2 bg-yellow-500 rounded-full"
                      style={{
                        width: `${item.coverage}%`,
                      }}
                    />

                  </div>

                </div>

              ))}

            </div>

          </div>

        ))}

      </div>

    </section>
  );
}