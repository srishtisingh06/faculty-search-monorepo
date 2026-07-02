export default function QuickActions() {
  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6">

      <h2 className="text-2xl font-bold mb-6">
        Quick Actions
      </h2>

      <div className="space-y-3">

        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-[#1b3156] border border-[#2b4570] hover:border-yellow-500 transition">
          👥
          <span>Browse All Faculty</span>
        </button>

        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-[#1b3156] border border-[#2b4570] hover:border-yellow-500 transition">
          📖
          <span>View by Department</span>
        </button>

        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-[#1b3156] border border-[#2b4570] hover:border-yellow-500 transition">
          ✉️
          <span>Contact Institute</span>
        </button>

      </div>

    </div>
  );
}