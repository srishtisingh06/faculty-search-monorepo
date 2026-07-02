import { Link } from "react-router-dom";
import { Home, Search } from "lucide-react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function NotFoundPage() {
  return (
    <div className="bg-[#081225] min-h-screen text-white flex flex-col">
      <Navbar />

      <main className="flex-1 flex items-center justify-center px-6">
        <div className="text-center max-w-2xl">

          <h1 className="text-8xl md:text-9xl font-extrabold text-yellow-500">
            404
          </h1>

          <h2 className="text-4xl font-bold mt-6">
            Page Not Found
          </h2>

          <p className="text-slate-400 text-lg mt-4 leading-8">
            Sorry, the page you are looking for doesn't exist or has been moved.
            Please check the URL or return to the homepage.
          </p>

          <div className="flex flex-wrap justify-center gap-4 mt-10">

            <Link
              to="/"
              className="bg-yellow-500 hover:bg-yellow-400 text-black font-semibold px-6 py-3 rounded-xl flex items-center gap-2 transition"
            >
              <Home size={18} />
              Go Home
            </Link>

            <Link
              to="/faculty"
              className="border border-slate-600 hover:border-yellow-500 px-6 py-3 rounded-xl flex items-center gap-2 transition"
            >
              <Search size={18} />
              Search Faculty
            </Link>

          </div>

        </div>
      </main>

      <Footer />
    </div>
  );
}