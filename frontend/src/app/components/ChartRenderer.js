"use client";
import ReactEChartsCore from "echarts-for-react/lib/core";
import * as echarts from "echarts/core";
import { BarChart, LineChart, PieChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  BarChart,
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  CanvasRenderer,
]);

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#f97316", "#14b8a6"];

export default function ChartRenderer({ chart }) {
  if (!chart) return null;

  const { chart_type } = chart;

  if (chart_type === "table") {
    return <TableView chart={chart} />;
  }

  const option = buildOption(chart);
  if (!option) return null;

  return (
    <div className="chart-container">
      <div className="chart-header">
        <span className="chart-type-badge">{chart_type} chart</span>
      </div>
      <ReactEChartsCore
        echarts={echarts}
        option={option}
        style={{ height: 320, width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
    </div>
  );
}

function buildOption(chart) {
  const { chart_type, x_data, y_data, x_axis, y_axis, pie_data } = chart;

  const baseOption = {
    backgroundColor: "transparent",
    textStyle: { color: "#94a3b8", fontFamily: "Inter, sans-serif" },
    tooltip: {
      trigger: chart_type === "pie" ? "item" : "axis",
      backgroundColor: "#1e2642",
      borderColor: "rgba(255,255,255,0.06)",
      textStyle: { color: "#f1f5f9", fontSize: 12 },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
  };

  if (chart_type === "bar") {
    return {
      ...baseOption,
      xAxis: {
        type: "category",
        data: x_data,
        axisLabel: {
          color: "#94a3b8",
          fontSize: 11,
          rotate: x_data?.length > 6 ? 35 : 0,
        },
        axisLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
      },
      yAxis: {
        type: "value",
        name: y_axis,
        nameTextStyle: { color: "#64748b", fontSize: 11 },
        axisLabel: { color: "#94a3b8", fontSize: 11 },
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.04)" } },
      },
      series: [
        {
          type: "bar",
          data: y_data,
          itemStyle: {
            borderRadius: [6, 6, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#3b82f6" },
              { offset: 1, color: "#8b5cf6" },
            ]),
          },
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowColor: "rgba(59,130,246,0.4)" },
          },
          barMaxWidth: 50,
        },
      ],
    };
  }

  if (chart_type === "line") {
    return {
      ...baseOption,
      xAxis: {
        type: "category",
        data: x_data,
        axisLabel: {
          color: "#94a3b8",
          fontSize: 11,
          rotate: x_data?.length > 8 ? 35 : 0,
        },
        axisLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
      },
      yAxis: {
        type: "value",
        name: y_axis,
        nameTextStyle: { color: "#64748b", fontSize: 11 },
        axisLabel: { color: "#94a3b8", fontSize: 11 },
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.04)" } },
      },
      series: [
        {
          type: "line",
          data: y_data,
          smooth: true,
          lineStyle: { width: 3, color: "#3b82f6" },
          itemStyle: { color: "#3b82f6" },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(59,130,246,0.3)" },
              { offset: 1, color: "rgba(59,130,246,0.02)" },
            ]),
          },
          symbol: "circle",
          symbolSize: 6,
        },
      ],
    };
  }

  if (chart_type === "pie") {
    return {
      ...baseOption,
      series: [
        {
          type: "pie",
          radius: ["40%", "70%"],
          center: ["50%", "50%"],
          data: (pie_data || []).map((d, i) => ({
            ...d,
            itemStyle: { color: COLORS[i % COLORS.length] },
          })),
          label: {
            color: "#94a3b8",
            fontSize: 12,
            formatter: "{b}: {d}%",
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: "rgba(0,0,0,0.5)",
            },
          },
          itemStyle: { borderColor: "#0a0e1a", borderWidth: 2 },
        },
      ],
    };
  }

  return null;
}

function TableView({ chart }) {
  const { columns, data } = chart;
  if (!data || data.length === 0) return null;

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {(columns || Object.keys(data[0])).map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 50).map((row, i) => (
            <tr key={i}>
              {(columns || Object.keys(row)).map((col) => (
                <td key={col}>
                  {typeof row[col] === "number"
                    ? row[col].toLocaleString()
                    : row[col] ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
