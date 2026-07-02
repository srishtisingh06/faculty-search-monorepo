import { Sparkles, Database, Search } from "lucide-react";

export default function HowItWorks() {
  const items = [
    {
      icon: <Sparkles size={32} />,
      title: "AI-Powered Search",
      desc: "Natural language queries to find faculty by research interests, expertise and publications.",
    },
    {
      icon: <Database size={32} />,
      title: "Comprehensive Coverage",
      desc: "IITs, NITs, BITS and selected Tier-1/Tier-2 engineering colleges.",
    },
    {
      icon: <Search size={32} />,
      title: "RAG Assistant",
      desc: "Chat with our AI assistant to discover researchers and get recommendations.",
    },
  ];

  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-6">

        <h2 className="text-5xl font-bold text-center text-white">
          How ADI Works
        </h2>

        <p className="text-center text-slate-400 mt-6 text-xl">
          Our platform crawls and indexes faculty data from premier institutions.
        </p>

        <div className="grid md:grid-cols-3 gap-8 mt-20">

          {items.map((item, index) => (
            <div
              key={index}
              className="relative bg-[#101c37] border border-slate-700 rounded-2xl p-8"
            >
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-amber-500 rounded-full flex items-center justify-center font-bold text-black">
                {index + 1}
              </div>

              <div className="text-amber-400 mb-6">
                {item.icon}
              </div>

              <h3 className="text-3xl font-semibold text-white">
                {item.title}
              </h3>

              <p className="text-slate-400 mt-4">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}