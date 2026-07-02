export default function AboutCard({ faculty }) {

  const interests = [
    ...(faculty.research_interests || []),
    ...(faculty.research_areas || [])
  ];

  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-xl p-6">

      <h2 className="text-xl font-semibold mb-4">
        About
      </h2>

      <p className="text-gray-400 leading-7">

        <span className="font-semibold text-white">
          {faculty.faculty_name}
        </span>

        {" "}is{" "}

        <span className="text-white">
          {faculty.designation || "Faculty Member"}
        </span>

        {" "}in the{" "}

        <span className="text-white">
          {faculty.department || "Department"}
        </span>

        {" "}at{" "}

        <span className="text-white">
          {faculty.institute_name}.
        </span>

      </p>

      {interests.length > 0 && (
        <>
          <h3 className="text-lg font-semibold mt-6 mb-3">
            Research Focus
          </h3>

          <p className="text-gray-400 leading-7">
            {interests.join(", ")}
          </p>
        </>
      )}

      {faculty.education?.length > 0 && (
        <>
          <h3 className="text-lg font-semibold mt-6 mb-3">
            Education
          </h3>

          <ul className="space-y-2 text-gray-400">
            {faculty.education.map((edu, index) => (
              <li key={index}>
                • {edu}
              </li>
            ))}
          </ul>
        </>
      )}

    </div>
  );
}