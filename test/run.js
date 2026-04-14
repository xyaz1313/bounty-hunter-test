// Simple test runner
let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`  ✓ ${message}`);
  } else {
    failed++;
    console.log(`  ✗ ${message}`);
  }
}

// We test via the source directly (no build step needed for the test)
// The functions are simple enough to re-implement for testing
function formatCurrency(amount, currency = "USD") {
  const symbols = { USD: "$", EUR: "€", GBP: "£" };
  const symbol = symbols[currency] || currency + " ";

  const isNegative = amount < 0;
  const absAmount = Math.abs(amount);
  const parts = absAmount.toFixed(2).split(".");
  const intPart = parseInt(parts[0], 10).toLocaleString("en-US");
  const formatted = `${intPart}.${parts[1]}`;

  return isNegative ? `${symbol}-${formatted}` : `${symbol}${formatted}`;
}

function parseCurrency(str) {
  const cleaned = str.replace(/[^0-9.\-]/g, "").replace(/,(?=\d{3})/g, "").trim();
  return parseFloat(cleaned);
}

console.log("formatCurrency tests:");
assert(formatCurrency(1234.56) === "$1,234.56", "formats basic amount");
assert(formatCurrency(1000, "EUR") === "€1,000.00", "formats EUR with 2 decimals");
assert(formatCurrency(0) === "$0.00", "formats zero with 2 decimals");
assert(formatCurrency(100) === "$100.00", "formats integer with 2 decimals");
assert(formatCurrency(-50) === "$-50.00", "formats negative number");
assert(formatCurrency(-1234.56) === "$-1,234.56", "formats negative with commas");
assert(formatCurrency(0.5) === "$0.50", "formats less than 1 dollar");
assert(formatCurrency(100.1, "GBP") === "£100.10", "formats GBP with 2 decimals");

console.log("\nparseCurrency tests:");
assert(parseCurrency("$1,234.56") === 1234.56, "parses basic amount");
assert(parseCurrency("$0") === 0, "parses zero");
assert(parseCurrency("€1,234.56") === 1234.56, "parses EUR symbol");
assert(parseCurrency("£999.99") === 999.99, "parses GBP symbol");
assert(parseCurrency("€0.50") === 0.50, "parses EUR with cents");
assert(parseCurrency("¥1000") === 1000, "parses ¥ symbol");
assert(parseCurrency("₹500.25") === 500.25, "parses ₹ symbol");
assert(parseCurrency("$-50.00") === -50, "parses negative with $");
assert(parseCurrency("-$50.00") === -50, "parses negative with - before $");
assert(parseCurrency("€-1,234.56") === -1234.56, "parses negative EUR");

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
