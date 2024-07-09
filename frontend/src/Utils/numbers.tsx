/**
 * Formats a number to a specified number of decimal places or returns null.
 * @param value The number to format or null.
 * @param decimals The number of decimal places.
 * @param isPercentage Whether the number should be formatted as a percentage.
 * @returns The formatted number or null.
 */
export function formatNumber(
  value: number | undefined,
  decimals: number = 1,
  isPercentage: boolean = false,
): string | null {
  if (value === null || value === undefined || value === 0) {
    return null;
  }

  const formattedValue = isPercentage ? value * 100 : value;

  return formattedValue.toLocaleString("sv-SE", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
    useGrouping: true,
  });
}
