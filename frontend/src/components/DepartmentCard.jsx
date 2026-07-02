export default function DepartmentCard({
  color = "bg-blue-500",
  border = "border-t-4 border-blue-500",
  icon = "💻",
  title = "Computer Science",
  faculty = "1245",
  publications = "12,567",
  institutes = ["IIT Bombay", "IIT Delhi", "IIT Madras"],
 researchAreas = [],
}) {
  return (
    <div
      className={`bg-[#11203d] rounded-2xl ${border} border border-[#27406b] p-7`}
    >
      <div className="grid grid-cols-2 gap-8">

        {/* LEFT */}
        <div>

          <div className="flex items-center gap-5 mb-7">

            <div
              className={`w-16 h-16 rounded-xl ${color} flex items-center justify-center text-3xl`}
            >
              {icon}
            </div>

            <div>
              <h2 className="text-4xl font-bold">{title}</h2>

              <p className="text-slate-400">
                Engineering & Technology
              </p>
            </div>

          </div>

          {/* Faculty */}
          <div className="bg-[#1b3156] rounded-lg px-5 py-4 flex justify-between mb-4">
            <span className="text-slate-300">
              👥 Total Faculty
            </span>

            <span className="font-bold text-xl">
              {faculty}
            </span>
          </div>

          {/* Publications */}
          <div className="bg-[#1b3156] rounded-lg px-5 py-4 flex justify-between mb-6">
            <span className="text-slate-300">
              📖 Publications
            </span>

            <span className="font-bold text-xl">
              {publications}
            </span>
          </div>

          {/* Institutes */}

          <h3 className="font-semibold mb-3">
            🏛 Top Institutes
          </h3>

          <div className="space-y-2 mb-8">

            {institutes.map((item) => (
              <p
                key={item}
                className="text-slate-300"
              >
                ↝ {item}
              </p>
            ))}

          </div>

          <button className="bg-yellow-500 hover:bg-yellow-400 transition w-full py-4 rounded-xl text-black font-bold text-lg">
            View All Faculty
          </button>

        </div>

        {/* RIGHT */}

        <div>

          <h3 className="text-2xl font-bold mb-5">
            Research Areas
          </h3>

          <div className="grid grid-cols-2 gap-4">

{researchAreas.map((area) => (

  <div
    key={area.name}
    className="border border-[#2d4674] rounded-xl p-5 flex justify-between items-center hover:border-yellow-500 transition cursor-pointer"
  >

    <span className="font-medium">
      {area.name}
    </span>

    <span className="bg-[#274d88] px-3 py-1 rounded-full text-sm">
      {area.count}
    </span>

  </div>

))}

          </div>

        </div>

      </div>
    </div>
  );
}