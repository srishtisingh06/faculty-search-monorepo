import { Link } from "react-router-dom";

export default function SimilarFaculty() {
  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-xl p-6">

      <h2 className="text-xl font-semibold mb-5">
        Similar Faculty
      </h2>

      <div className="flex flex-col items-center justify-center py-8">

        <div className="w-20 h-20 rounded-full bg-[#1c335a] flex items-center justify-center text-3xl mb-4">
          👨‍🏫
        </div>

        <h3 className="text-lg font-semibold mb-2">
          Coming Soon
        </h3>

        <p className="text-center text-gray-400 text-sm leading-6">
          Similar faculty recommendations will be available in the
          next version using semantic similarity search.
        </p>

        <Link
          to="/faculty"
          className="mt-6 bg-yellow-500 hover:bg-yellow-400 text-black px-5 py-2 rounded-lg font-semibold"
        >
          Back to Search
        </Link>

      </div>

    </div>
  );
}