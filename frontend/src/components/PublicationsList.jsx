export default function PublicationsList({ faculty }) {

  const publications = faculty.publications || [];

  if (publications.length === 0) {
    return (
      <div className="bg-[#11203d] border border-[#27406b] rounded-xl p-8 text-center">
        <h2 className="text-2xl font-semibold mb-2">
          Publications
        </h2>

        <p className="text-gray-400">
          No publications available.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">

      {publications.map((pub, index) => (

        <div
          key={index}
          className="bg-[#11203d] border border-[#27406b] rounded-xl p-6"
        >

          <h2 className="text-2xl font-semibold">
            {pub}
          </h2>

          <p className="text-gray-400 mt-3">
            Publication #{index + 1}
          </p>

        </div>

      ))}

    </div>
  );
}