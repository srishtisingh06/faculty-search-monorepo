export default function SearchBar() {
  return (
    <div className="mb-8">

      <h1 className="text-4xl font-bold mb-5">
        Faculty Search
      </h1>

      <div className="flex gap-3">

        <input
          type="text"
          placeholder="Search by name, research area, or keywords..."
          className="px-10 bg-[#11203d] border border-[#27406b] rounded-lg px-4 py-3"
        />

        <button className="bg-yellow-500 text-black px-6 rounded-lg font-semibold">
          Search
        </button>

      </div>

    </div>
  );
}