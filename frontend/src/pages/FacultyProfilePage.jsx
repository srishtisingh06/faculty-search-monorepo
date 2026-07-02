import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

import ProfileHeader from "../components/ProfileHeader";
import PublicationsList from "../components/PublicationsList";
import AboutCard from "../components/AboutCard";
import ResearchInterests from "../components/ResearchInterests";
import SimilarFaculty from "../components/SimilarFaculty";

export default function FacultyProfilePage() {
  const { facultyId } = useParams();

  const [faculty, setFaculty] = useState(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/faculty/${facultyId}`)
      .then((res) => res.json())
      .then((data) => setFaculty(data))
      .catch(console.error);
  }, [facultyId]);

  if (!faculty) {
    return (
      <div className="bg-[#081225] min-h-screen text-white flex justify-center items-center">
        Loading...
      </div>
    );
  }

  return (
    <div className="bg-[#081225] min-h-screen text-white">
      <Navbar />

      <div className="max-w-7xl mx-auto px-6 py-8">

        <ProfileHeader faculty={faculty} />

        <div className="grid grid-cols-12 gap-6 mt-8">

          <div className="col-span-8">
            <PublicationsList faculty={faculty} />
          </div>

          <div className="col-span-4 space-y-6">
            <AboutCard faculty={faculty} />
            <ResearchInterests faculty={faculty} />
            <SimilarFaculty />
          </div>

        </div>

      </div>

      <Footer />
    </div>
  );
}