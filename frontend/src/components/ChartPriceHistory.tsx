import { QueryLoader, SecurityInfo, useQueryChartHistory } from "@Api";
import { LocalStorageKey } from "@Const";
import { StandardCard } from "@Generic";
import { Box, Button, Divider, Typography, useTheme } from "@mui/material";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  TimeScale,
  Title,
  Tooltip,
  TooltipItem,
} from "chart.js";
import { Chart, ChartDataset, ChartMeta } from "chart.js";
import dayjs, { Dayjs } from "dayjs";
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { useParams } from "react-router-dom";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Title,
  Tooltip,
  Legend,
);

/**
 * Callback function to format the tooltip label.
 * @param context - The tooltip context.
 * @returns An array of strings to display in the tooltip.
 */
function tooltipLabelCallback(context: TooltipItem<"line">): string[] {
  const item = context.raw as {
    x: string;
    y: number;
    volumeBuy?: number;
    volumeSell?: number;
  };
  const volumeBuy = item.volumeBuy ?? 0;
  const volumeSell = item.volumeSell ?? 0;
  const volumeLabel =
    volumeBuy > 0
      ? `Volume bought: ${volumeBuy}`
      : volumeSell > 0
        ? `Volume sold: ${volumeSell}`
        : "";

  return [`${context.dataset.label}: ${item.y}`, volumeLabel];
}

const customPluginShowBuySellMarkers = {
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
ChartJS.register(customPluginShowBuySellMarkers);

interface DateRangePickerProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
}

const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}) => {
  const [start, setStart] = useState<Dayjs | null>(dayjs(startDate));
  const [end, setEnd] = useState<Dayjs | null>(dayjs(endDate));

  const handleStartDateChange = (date: Dayjs | null) => {
    setStart(date);
    if (date) {
      onStartDateChange(date.format("YYYY-MM-DD"));
    }
  };

  const handleEndDateChange = (date: Dayjs | null) => {
    setEnd(date);
    if (date) {
      onEndDateChange(date.format("YYYY-MM-DD"));
    }
  };

  const handleYTDClick = () => {
    const startOfYear = dayjs().startOf("year");
    const today = dayjs();
    setStart(startOfYear);
    setEnd(today);
    onStartDateChange(startOfYear.format("YYYY-MM-DD"));
    onEndDateChange(today.format("YYYY-MM-DD"));
  };

  const handleLastCalendarYearClick = () => {
    const oneYearAgo = dayjs().subtract(1, "year");
    const today = dayjs();
    setStart(oneYearAgo);
    setEnd(today);
    onStartDateChange(oneYearAgo.format("YYYY-MM-DD"));
    onEndDateChange(today.format("YYYY-MM-DD"));
  };

  const handleLastThreeYearsClick = () => {
    const threeYearsAgo = dayjs().subtract(3, "year");
    const today = dayjs();
    setStart(threeYearsAgo);
    setEnd(today);
    onStartDateChange(threeYearsAgo.format("YYYY-MM-DD"));
    onEndDateChange(today.format("YYYY-MM-DD"));
  };

  const handleLastFiveYearsClick = () => {
    const fiveYearsAgo = dayjs().subtract(5, "year");
    const today = dayjs();
    setStart(fiveYearsAgo);
    setEnd(today);
    onStartDateChange(fiveYearsAgo.format("YYYY-MM-DD"));
    onEndDateChange(today.format("YYYY-MM-DD"));
  };

  /**
   * A button component with a label.
   * @param props - The component props.
   * @param props.label - The label for the button.
   * @param props.handleClick - The function to call when the button is clicked.
   * @returns The rendered button component.
   */
  function ButtonWithLabel({
    label,
    handleClick,
  }: {
    label: string;
    handleClick: () => void;
  }): JSX.Element {
    return (
      <Button
        variant="contained"
        onClick={handleClick}
        sx={{
          height: "46px",
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "center",
        }}
      >
        <Typography variant="button" sx={{ display: "flex" }}>
          {label}
        </Typography>
      </Button>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <StandardCard
        height={"85px"}
        sx={{
          paddingTop: "6px",
          marginTop: "5px",
          display: "flex",
          gap: 2,
          alignItems: "center",
        }}
      >
        <DatePicker
          label="Start date"
          value={start}
          onChange={handleStartDateChange}
          format="YYYY-MM-DD"
          slotProps={{
            textField: {
              fullWidth: true,
            },
          }}
        />
        <DatePicker
          label="End date"
          value={end}
          onChange={handleEndDateChange}
          format="YYYY-MM-DD"
          slotProps={{
            textField: {
              fullWidth: true,
            },
          }}
        />
        <ButtonWithLabel label="YTD" handleClick={handleYTDClick} />
        <ButtonWithLabel
          label="Last year"
          handleClick={handleLastCalendarYearClick}
        />
        <ButtonWithLabel
          label="Last 3 years"
          handleClick={handleLastThreeYearsClick}
        />
        <ButtonWithLabel
          label="Last 5 years"
          handleClick={handleLastFiveYearsClick}
        />
      </StandardCard>
    </LocalizationProvider>
  );
};

interface SecurityInfoCardProps {
  securityInfo: SecurityInfo | null;
  isinCode: string;
}

/**
 * A component to display security information.
 * If `securityInfo` is provided, it displays the name on the left and the ISIN code on the right.
 * If `securityInfo` is not provided, it displays an error message.
 * @param props - The component props.
 * @param props.securityInfo - The security information object containing name and ISIN code.
 * @param props.isinCode - The ISIN code to display if `securityInfo` is not provided.
 * @returns The rendered component.
 */
function SecurityInfoCard({
  securityInfo,
  isinCode,
}: SecurityInfoCardProps): JSX.Element {
  return (
    <StandardCard
      height={"40px"}
      sx={{ paddingTop: "11px", marginBottom: "3px" }}
    >
      {securityInfo ? (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
          }}
        >
          <Typography variant="h1" gutterBottom>
            {securityInfo.name}
          </Typography>
          <Divider
            orientation="vertical"
            flexItem
            sx={{
              mx: 1.5,
              borderColor: `text.primary`,
              height: "20px",
            }}
          />
          <Typography variant="h1" gutterBottom>
            {securityInfo.isinCode}
          </Typography>
        </Box>
      ) : (
        <Typography variant="h6" gutterBottom>
          {`${isinCode} does not exist in security database`}
        </Typography>
      )}
    </StandardCard>
  );
}

/**
 * Component to display the price history chart for a given ISIN code.
 * @param props - The component props.
 * @param props.isinCode - The ISIN code for which to fetch and display the price history.
 * @returns The rendered component.
 * @example
 * <ChartPriceHistory isinCode="US0378331005" />
 */
function ChartPriceHistory({ isinCode }: { isinCode: string }) {
  const theme = useTheme();
  const [startDate, setStartDate] = useState(
    localStorage.getItem(LocalStorageKey.CHART_START_DATE) ||
      new Date(new Date().setFullYear(new Date().getFullYear() - 1))
        .toISOString()
        .split("T")[0],
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0],
  );

  useEffect(() => {
    localStorage.setItem(LocalStorageKey.CHART_START_DATE, startDate);
  }, [startDate]);

  useEffect(() => {
    localStorage.setItem(LocalStorageKey.CHART_END_DATE, endDate);
  }, [endDate]);

  const variables = {
    isinCode: isinCode,
    startDate: startDate,
    endDate: endDate,
  };

  const { loading, error, data } = useQueryChartHistory(variables);

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      {data && (
        <>
          <SecurityInfoCard
            securityInfo={data.securityInfo}
            isinCode={isinCode}
          />
          <StandardCard
            height={"560px"}
            sx={{ marginTop: "5px", marginBottom: "0px", paddingLeft: "16px" }}
          >
            <Line
              data={{
                labels: data.chartHistory.map((item) => item.xVal),
                datasets: [
                  {
                    label: "Average cost",
                    data: data.chartHistory.map((item) => ({
                      x: item.xVal,
                      y:
                        item.costPriceAverage !== 0 && item.costPriceAverage
                          ? parseFloat(item.costPriceAverage.toFixed(4))
                          : null,
                    })),
                    fill: false,
                    borderColor: theme.palette.secondary.main, // Use secondary theme color
                    borderWidth: 3,
                    pointRadius: 0, // No points
                  },
                  {
                    label: "Close",
                    data: data.chartHistory.map((item) => ({
                      x: item.xVal,
                      y: item.yVal ? parseFloat(item.yVal.toFixed(4)) : null,
                      volumeBuy: item.volumeBuy,
                      volumeSell: item.volumeSell,
                    })),
                    fill: false,
                    borderColor: theme.palette.text.primary, // Use theme color
                    borderWidth: 1, // Make the line thinner
                    pointRadius: data.chartHistory.map((item) =>
                      (item.volumeBuy ?? 0) > 0 || (item.volumeSell ?? 0) > 0
                        ? 9
                        : 0,
                    ), // Add marker if volumeBuy > 0 or volumeSell > 0
                    pointBackgroundColor: data.chartHistory.map(
                      (item) =>
                        (item.volumeBuy ?? 0) > 0
                          ? theme.palette.info.main // Use theme color for buy
                          : (item.volumeSell ?? 0) > 0
                            ? theme.palette.error.main // Use theme color for sell
                            : theme.palette.text.primary, // Use theme color for default
                    ), // Set marker color based on theme
                    pointBorderWidth: 0, // No border
                  },
                ],
              }}
              options={{
                maintainAspectRatio: false,
                interaction: {
                  mode: "index",
                  intersect: false,
                },
                scales: {
                  x: {
                    ticks: {
                      maxTicksLimit: 12, // Reduce the number of ticks
                      color: theme.palette.text.primary, // Set tick labels to primary color
                    },
                    grid: {
                      display: false, // Hide x-axis grid lines
                    },
                  },
                  y: {
                    ticks: {
                      maxTicksLimit: 10, // Reduce the number of ticks
                      callback: function (value) {
                        return value.toLocaleString(); // Format the tick labels
                      },
                      color: theme.palette.text.primary, // Set tick labels to primary color
                    },
                    grid: {
                      display: false, // Hide x-axis grid lines
                    },
                    title: {
                      display: !!data.securityInfo.currency,
                      text: data.securityInfo.currency,
                      align: "center",
                      color: theme.palette.text.primary,
                    },
                  },
                },
                plugins: {
                  legend: {
                    display: true, // Show legend
                    position: "bottom", // Position the legend below the x-axis
                    labels: {
                      usePointStyle: true, // Use point style
                      pointStyle: "line", // Set point style to line
                      color: theme.palette.text.primary, // Set text color to primary text color
                    },
                  },
                  tooltip: {
                    callbacks: {
                      label: tooltipLabelCallback,
                    },
                  },
                },
              }}
            />
          </StandardCard>
        </>
      )}
      <DateRangePicker
        startDate={startDate}
        endDate={endDate}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
      />
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
