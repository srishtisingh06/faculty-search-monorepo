export default function InstituteTypeCard({
  title,
  institutes,
}) {
  return (
    <div className="bg-[#12203d] rounded-2xl border border-[#27406b] p-6">

      <h2 className="text-3xl font-bold mb-6">
        {title}
      </h2>

      <div className="space-y-5">

        {institutes.length === 0 && (
          <p className="text-slate-400">
            No institutes found
          </p>
        )}

        {institutes.map((item) => (

          <div
            key={item.name}
            className="bg-[#1a2d4f] rounded-xl p-4"
          >

            <div className="flex justify-between">

              <h3 className="font-semibold">
                {item.name}
              </h3>

              <span className="bg-green-600 px-3 py-1 rounded-full text-sm">
                {item.coverage}%
              </span>

            </div>

            <p className="text-slate-400 mt-2">
              {item.faculty} Faculty
            </p>

            <div className="w-full h-2 bg-gray-700 rounded-full mt-3">

              <div
                className="bg-yellow-500 h-2 rounded-full"
                style={{
                  width: `${item.coverage}%`,
                }}
              />

            </div>

          </div>

        ))}

      </div>

    </div>
  );
}