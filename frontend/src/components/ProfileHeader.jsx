export default function ProfileHeader({ faculty }) {
  const tags = [
    ...(faculty.research_interests || []),
    ...(faculty.research_areas || []),
  ];

  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-7">

      <div className="flex justify-between">

        {/* Left */}
        <div className="flex gap-7">

          <img
            src={
              faculty.profile_image ||
              "https://randomuser.me/api/portraits/men/32.jpg"
            }
            alt={faculty.faculty_name}
            className="w-32 h-32 rounded-xl object-cover"
          />

          <div>

            <h1 className="text-4xl font-bold mb-3">
              {faculty.faculty_name}
            </h1>

            <p className="text-gray-300 text-xl">
              {faculty.designation || "Not Available"}
            </p>

            <p className="text-gray-400 mt-1">
              {faculty.department || "Department"} •{" "}
              {faculty.institute_name || "Institute"}
            </p>

            <div className="flex flex-wrap gap-2 mt-5">

              {tags.length > 0 ? (
                tags.slice(0, 6).map((tag) => (
                  <span
                    key={tag}
                    className="bg-blue-600 px-3 py-1 rounded-md text-xs"
                  >
                    {tag}
                  </span>
                ))
              ) : (
                <span className="text-gray-400 text-sm">
                  No Research Interests Available
                </span>
              )}

            </div>

            <div className="flex gap-3 mt-6">

              <a
                href={faculty.email ? `mailto:${faculty.email}` : "#"}
                className="bg-yellow-500 text-black px-5 py-2 rounded-lg font-semibold"
              >
                Contact
              </a>

              <a
                href={faculty.personal_website || "#"}
                target="_blank"
                rel="noreferrer"
                className="border border-[#27406b] px-5 py-2 rounded-lg"
              >
                Website
              </a>

              <a
                href={faculty.google_scholar || "#"}
                target="_blank"
                rel="noreferrer"
                className="border border-[#27406b] px-5 py-2 rounded-lg"
              >
                Google Scholar
              </a>

            </div>

          </div>

        </div>

        {/* Right Stats */}
        <div className="grid grid-cols-2 gap-4">

          <div className="bg-[#0c1a33] border border-[#27406b] rounded-xl w-32 h-24 flex flex-col justify-center items-center">
            <h2 className="text-4xl font-bold text-yellow-500">
              {faculty.publications?.length || 0}
            </h2>
            <p className="text-sm text-gray-400">
              Publications
            </p>
          </div>

          <div className="bg-[#0c1a33] border border-[#27406b] rounded-xl w-32 h-24 flex flex-col justify-center items-center">
            <h2 className="text-4xl font-bold text-yellow-500">
              -
            </h2>
            <p className="text-sm text-gray-400">
              Citations
            </p>
          </div>

          <div className="bg-[#0c1a33] border border-[#27406b] rounded-xl w-32 h-24 flex flex-col justify-center items-center">
            <h2 className="text-4xl font-bold text-yellow-500">
              -
            </h2>
            <p className="text-sm text-gray-400">
              h-index
            </p>
          </div>

          <div className="bg-[#0c1a33] border border-[#27406b] rounded-xl w-32 h-24 flex flex-col justify-center items-center">
            <h2 className="text-4xl font-bold text-yellow-500">
              -
            </h2>
            <p className="text-sm text-gray-400">
              i10-index
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}