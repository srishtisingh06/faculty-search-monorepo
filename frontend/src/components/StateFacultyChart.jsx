import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export default function StateFacultyChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data}>
        <XAxis
          dataKey="state"
          tick={{ fill: "#cbd5e1" }}
        />

        <YAxis tick={{ fill: "#cbd5e1" }} />

        <Tooltip />

        <Bar
          dataKey="faculty"
          fill="#f59e0b"
          radius={[6,6,0,0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}