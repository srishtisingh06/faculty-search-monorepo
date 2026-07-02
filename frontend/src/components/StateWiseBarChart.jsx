import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function StateWiseBarChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-slate-400">
        No Data
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data}>
        <CartesianGrid stroke="#334155" strokeDasharray="3 3" />

        <XAxis
          dataKey="state"
          tick={{ fill: "#cbd5e1" }}
        />

        <YAxis
          tick={{ fill: "#cbd5e1" }}
        />

        <Tooltip />

        <Bar
          dataKey="faculty"
          fill="#3b82f6"
          radius={[6, 6, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}