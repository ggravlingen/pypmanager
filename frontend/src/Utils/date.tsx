/**
 * Formats a given date as a string in the format of "yyyy-mm-dd".
 * If the input is `undefined`, returns `null`.
 *
 * @param {Date | undefined} dateInput - The date to format, or `undefined`.
 * @returns {string | null} The formatted date as "yyyy-mm-dd", or `null` if input is `undefined`.
 */
export function formatDate(dateInput: Date | undefined): string | null {
  if (!dateInput) {
    return null;
  }

  const date = new Date(dateInput);
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  return `${year}-${month}-${day}`;
}
