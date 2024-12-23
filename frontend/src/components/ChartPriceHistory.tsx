import { QueryLoader, useQueryChartHistory } from "@Api";
import { Box } from "@mui/material";
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { Chart, ChartDataset, ChartMeta } from "chart.js";
import React from "react";
import { Line } from "react-chartjs-2";
import { useParams } from "react-router-dom";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
);

const customPlugin = {
  id: "showBuySellMarkers",
  afterDatasetsDraw: (chart: Chart) => {
    const ctx = chart.ctx;
    chart.data.datasets.forEach(
      (dataset: ChartDataset, datasetIndex: number) => {
        const meta = chart.getDatasetMeta(datasetIndex) as ChartMeta;
        meta.data.forEach((point, index) => {
          const item = dataset.data[index] as {
            volumeBuy?: number;
            volumeSell?: number;
          };
          const volumeBuy = item.volumeBuy ?? 0;
          const volumeSell = item.volumeSell ?? 0;
          const label = volumeBuy > 0 ? "B" : volumeSell > 0 ? "S" : "";
          if (label) {
            ctx.fillStyle = "white";
            ctx.font = "10px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(label, point.x, point.y);
          }
        });
      },
    );
  },
};

// Register the custom plugin globally
ChartJS.register(customPlugin);

/**
 * Component to display the price history chart for a given ISIN code.
 * @param props - The component props.
 * @param props.isinCode - The ISIN code for which to fetch and display the price history.
 * @returns The rendered component.
 * @example
 * <ChartPriceHistory isinCode="US0378331005" />
 */
function ChartPriceHistory({ isinCode }: { isinCode: string }) {
  const variables = {
    isinCode: isinCode,
    startDate: "2024-01-01",
    endDate: "2024-12-23",
  };

  const { loading, error, data } = useQueryChartHistory(variables);

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      {data && (
        <Box sx={{ width: "1200px", height: "700px", margin: "20px" }}>
          <Line
            data={{
              labels: data.chartHistory.map((item) => item.xVal),
              datasets: [
                {
                  data: data.chartHistory.map((item) => ({
                    x: item.xVal,
                    y: item.yVal,
                    volumeBuy: item.volumeBuy,
                    volumeSell: item.volumeSell,
                  })),
                  fill: false,
                  backgroundColor: "rgba(75,192,192,0.4)",
                  borderColor: "rgba(75,192,192,1)",
                  borderWidth: 1, // Make the line thinner
                  pointRadius: data.chartHistory.map((item) =>
                    (item.volumeBuy ?? 0) > 0 || (item.volumeSell ?? 0) > 0
                      ? 7
                      : 0,
                  ), // Add marker if volumeBuy > 0 or volumeSell > 0
                  pointBackgroundColor: data.chartHistory.map((item) =>
                    (item.volumeBuy ?? 0) > 0
                      ? "blue"
                      : (item.volumeSell ?? 0) > 0
                        ? "red"
                        : "rgba(75,192,192,0.4)",
                  ), // Set marker color to blue if volumeBuy > 0, red if volumeSell > 0
                  pointBorderWidth: 0, // No border
                },
              ],
            }}
            options={{
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false, // Remove legend
                },
              },
            }}
          />
        </Box>
      )}
    </QueryLoader>
  );
}

/**
 * A wrapper component for displaying the price history chart based on the provided ISIN code.
 * It retrieves the ISIN code from the URL parameters using the `useParams` hook.
 * If no ISIN code is provided, it displays an error message.
 * @returns The price history chart component or an error message.
 */
export default function ChartPriceHistoryWrapper(): JSX.Element {
  const { isinCode } = useParams<{ isinCode: string }>();

  if (!isinCode) {
    return <div>Error: No ISIN code provided</div>;
  }

  return <ChartPriceHistory isinCode={isinCode} />;
}
