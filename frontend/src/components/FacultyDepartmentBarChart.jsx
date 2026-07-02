import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function FacultyDepartmentBarChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-slate-400">
        No Data
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={350}>
  <BarChart
    data={data}
    layout="vertical"
    margin={{ top: 10, right: 30, left: 40, bottom: 10 }}
  >
        <CartesianGrid stroke="#334155" strokeDasharray="3 3" />

        <XAxis
            type="number"
            tick={{ fill: "#cbd5e1" }}
        />

        <YAxis
            type="category"
            dataKey="department"
            width={220}
            tick={{ fill: "#cbd5e1", fontSize: 12 }}
        />

        <Tooltip />

        <Bar
            dataKey="faculty"
            fill="#f59e0b"
            radius={[0, 6, 6, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}