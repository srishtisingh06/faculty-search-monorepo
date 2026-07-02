export default function CoverageSummaryCards({ coverage }) {
  const cards = [
    {
      title: "IIT Coverage",
      data: coverage.iit,
    },
    {
      title: "NIT Coverage",
      data: coverage.nit,
    },
    {
      title: "BITS Coverage",
      data: coverage.bits,
    },
    {
      title: "Total Coverage",
      data: coverage.overall,
    },
  ];

  return (
    <section className="mb-14">
      <div className="grid grid-cols-4 gap-6">

        {cards.map((card) => (

          <div
            key={card.title}
            className="bg-[#12203d] border border-[#28426d] rounded-2xl p-8"
          >

            <div className="text-center">

              <h2 className="text-5xl font-bold text-yellow-400">
                {card.data.covered}/{card.data.total}
              </h2>

              <p className="text-slate-400 mt-2">
                {card.title}
              </p>

            </div>

            <div className="w-full h-3 bg-[#36445f] rounded-full mt-8">

              <div
                className="h-3 bg-yellow-500 rounded-full"
                style={{
                  width: `${card.data.percentage}%`,
                }}
              />

            </div>

            <p className="text-center mt-4 font-semibold">
              {card.data.percentage}%
            </p>

          </div>

        ))}

      </div>
    </section>
  );
}