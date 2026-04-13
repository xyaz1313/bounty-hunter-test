/**
 * Format a number as a currency string.
 * 
 * @param amount - The amount to format
 * @param currency - Currency code (default: "USD")
 * @returns Formatted string like "$1,234.56"
 */
export function formatCurrency(amount: number, currency: string = "USD"): string {
  const symbols: Record<string, string> = {
    USD: "$",
    EUR: "€",
    GBP: "£",
  };
  const symbol = symbols[currency] || currency + " ";
  
  const isNegative = amount < 0;
  const absAmount = Math.abs(amount);

  // Always show 2 decimal places with proper thousand separators
  const parts = absAmount.toFixed(2).split(".");
  const intPart = Number(parts[0]).toLocaleString("en-US");
  const formatted = `${intPart}.${parts[1]}`;

  return isNegative ? `-${symbol}${formatted}` : `${symbol}${formatted}`;
}

/**
 * Parse a currency string back to a number.
 * 
 * @param str - String like "$1,234.56"
 * @returns The numeric value
 */
export function parseCurrency(str: string): number {
  // Strip any known currency symbol and common ones
  const cleaned = str
    .replace(/[$€£]/g, "")
    .replace(/[^\d.,\-]/g, "")
    .replace(/,/g, "");
  return parseFloat(cleaned);
}
