export default function InstituteTabs({
  selected,
  setSelected,
}) {
  const tabs = [
    { label: "All", value: "ALL" },
    { label: "IIT", value: "IIT" },
    { label: "NIT", value: "NIT" },
    { label: "BITS", value: "BITS" },
  ];

  return (
    <div className="mt-8 mb-10">
      <div className="inline-flex bg-[#1b3156] rounded-xl p-1 border border-[#27406b]">

        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setSelected(tab.value)}
            className={`px-10 py-3 rounded-lg font-semibold transition ${
              selected === tab.value
                ? "bg-[#2d4f87] text-white"
                : "text-slate-300 hover:text-white hover:bg-[#243d69]"
            }`}
          >
            {tab.label}
          </button>
        ))}

      </div>
    </div>
  );
}