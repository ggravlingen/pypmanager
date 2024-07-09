/**
 * Extracts the value from an object based on a dot-notated field path.
 * @param rowData - The object from which to extract the value.
 * @param fieldPath - The dot-notated path to the value in the object.
 * @returns - The value at the specified field path, or undefined if not found.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function extractDataFromRecord(rowData: any, fieldPath: string): any {
  // Split the fieldPath into an array of keys.
  const keys = fieldPath.split(".");

  // Iterate over the keys array, reducing the record to the nested value.
  return keys.reduce((acc, key) => {
    // Check if acc is an object and has the key, if not return undefined.
    return acc && typeof acc === "object" ? acc[key] : undefined;
  }, rowData);
}
