/**
 * Formats a number to a specified number of decimal places or returns null.
 * @param value The number to format or null.
 * @param decimals The number of decimal places.
 * @returns The formatted number or null.
 */
export function formatNumber(
  value: number | undefined,
  decimals: number = 1,
): string | null {
  if (value === null || value === undefined || value === 0) {
    return null;
  }

  return value.toLocaleString("sv-SE", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
    useGrouping: true,
  });
}
