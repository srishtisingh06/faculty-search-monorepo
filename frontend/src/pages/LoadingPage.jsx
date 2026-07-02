import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import SkeletonCard from "../components/SkeletonCard";

export default function LoadingPage() {
  return (
    <div className="bg-[#081225] min-h-screen text-white">

      <Navbar />

      <div className="max-w-[1650px] mx-auto px-10 py-8">

        {/* Heading */}
        <div className="mb-10">

          <div className="h-10 w-80 bg-slate-700 rounded animate-pulse mb-4"></div>

          <div className="h-5 w-96 bg-slate-700 rounded animate-pulse"></div>

        </div>

        {/* Search Bar */}
        <div className="h-14 bg-[#11203d] border border-[#27406b] rounded-xl animate-pulse mb-10"></div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">

          {[1, 2, 3, 4].map((item) => (
            <div
              key={item}
              className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6 animate-pulse"
            >
              <div className="w-14 h-14 bg-slate-700 rounded-xl mb-5"></div>

              <div className="h-8 w-24 bg-slate-700 rounded mb-3"></div>

              <div className="h-4 w-32 bg-slate-700 rounded"></div>
            </div>
          ))}

        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-8">

          {[1, 2, 3, 4, 5, 6].map((item) => (
            <SkeletonCard key={item} />
          ))}

        </div>

      </div>

      <Footer />

    </div>
  );
}