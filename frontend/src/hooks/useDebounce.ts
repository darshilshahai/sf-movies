import { useEffect, useState } from "react";

/**
 * Custom hook that delays updating a value until after a specified delay period has elapsed
 * since the last time the value changed. Helps prevent rapid API calls during typing.
 *
 * @param value The value to be debounced.
 * @param delay Delay in milliseconds (default: 300ms).
 * @returns The debounced value.
 */
export function useDebounce<T>(value: T, delay = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
