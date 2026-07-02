export default function ResearchInterests({ faculty }) {

  const interests = [
    ...(faculty.research_interests || []),
    ...(faculty.research_areas || []),
  ];

  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-xl p-6">

      <h2 className="text-xl font-semibold mb-4">
        Research Interests
      </h2>

      {interests.length > 0 ? (

        <ul className="space-y-3">

          {interests.map((item, index) => (

            <li
              key={index}
              className="text-gray-300 bg-[#0c1a33] border border-[#27406b] rounded-lg px-4 py-3"
            >
              • {item}
            </li>

          ))}

        </ul>

      ) : (

        <p className="text-gray-400">
          No research interests available.
        </p>

      )}

    </div>
  );
}