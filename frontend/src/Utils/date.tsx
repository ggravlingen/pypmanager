import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

/**
 * Formats a given date as a string in the format of "yyyy-mm-dd".
 * If the input is `undefined`, returns `null`.
 * @param dateInput - The date to format, or `undefined`.
 * @param isRelative - If `true`, returns the relative time from now.
 * @returns The formatted date as "yyyy-mm-dd", or `null` if input is `undefined`.
 */
export function formatDate(
  dateInput: Date | undefined,
  isRelative: boolean = false,
): string | null {
  if (!dateInput) {
    return null;
  }

  const date = new Date(dateInput);
  if (isRelative) {
    return dayjs(date).fromNow();
  }

  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");

  return `${year}-${month}-${day}`;
}
