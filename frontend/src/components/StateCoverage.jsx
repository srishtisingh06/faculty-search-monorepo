export default function StateCoverage() {
  const states = [
    {
      state: "Maharashtra",
      institutes: 4,
      faculty: 285,
    },
    {
      state: "Delhi",
      institutes: 2,
      faculty: 198,
    },
    {
      state: "Tamil Nadu",
      institutes: 3,
      faculty: 240,
    },
    {
      state: "Karnataka",
      institutes: 2,
      faculty: 121,
    },
    {
      state: "Uttar Pradesh",
      institutes: 2,
      faculty: 71,
    },
  ];

  return (
    <section className="mb-14">

      <h2 className="text-4xl font-bold mb-8">
        State-wise Coverage
      </h2>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-6">

        {states.map((item) => (

          <div
            key={item.state}
            className="bg-[#12203d] border border-[#28426d] rounded-2xl p-6"
          >

            <h3 className="text-2xl font-bold mb-5">
              {item.state}
            </h3>

            <div className="space-y-3 text-slate-300">

              <div className="flex justify-between">
                <span>Institutes</span>
                <span>{item.institutes}</span>
              </div>

              <div className="flex justify-between">
                <span>Faculty</span>
                <span>{item.faculty}</span>
              </div>

            </div>

          </div>

        ))}

      </div>

    </section>
  );
}