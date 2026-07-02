import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const data = [
  { month: "Jan", searches: 120 },
  { month: "Feb", searches: 180 },
  { month: "Mar", searches: 240 },
  { month: "Apr", searches: 310 },
  { month: "May", searches: 390 },
  { month: "Jun", searches: 480 },
];

export default function SearchTrendChart() {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="4 4" stroke="#334155" />

        <XAxis
          dataKey="month"
          tick={{ fill: "#cbd5e1" }}
        />

        <YAxis
          tick={{ fill: "#cbd5e1" }}
        />

        <Tooltip />

        <Line
          type="monotone"
          dataKey="searches"
          stroke="#f59e0b"
          strokeWidth={3}
          dot={{ r: 5 }}
          activeDot={{ r: 7 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}