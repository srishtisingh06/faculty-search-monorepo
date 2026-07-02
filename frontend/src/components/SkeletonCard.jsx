export default function SkeletonCard() {
  return (
    <div className="bg-[#11203d] border border-[#27406b] rounded-2xl p-6 animate-pulse">

      {/* Image */}
      <div className="w-16 h-16 rounded-xl bg-slate-700 mb-5"></div>

      {/* Title */}
      <div className="h-6 w-2/3 bg-slate-700 rounded mb-4"></div>

      {/* Subtitle */}
      <div className="h-4 w-1/2 bg-slate-700 rounded mb-6"></div>

      {/* Stats */}
      <div className="space-y-3">
        <div className="h-4 bg-slate-700 rounded"></div>
        <div className="h-4 bg-slate-700 rounded"></div>
        <div className="h-4 bg-slate-700 rounded"></div>
      </div>

      {/* Button */}
      <div className="h-11 w-full bg-slate-700 rounded-xl mt-8"></div>

    </div>
  );
}