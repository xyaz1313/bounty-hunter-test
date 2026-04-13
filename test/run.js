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

// Updated implementations matching src/format.ts
function formatCurrency(amount, currency = "USD") {
  const symbols = { USD: "$", EUR: "€", GBP: "£" };
  const symbol = symbols[currency] || currency + " ";

  const isNegative = amount < 0;
  const absAmount = Math.abs(amount);

  // Always show 2 decimal places with proper thousand separators
  const parts = absAmount.toFixed(2).split(".");
  const intPart = Number(parts[0]).toLocaleString("en-US");
  const formatted = `${intPart}.${parts[1]}`;

  return isNegative ? `-${symbol}${formatted}` : `${symbol}${formatted}`;
}

function parseCurrency(str) {
  const cleaned = str
    .replace(/[$€£]/g, "")
    .replace(/[^\d.,\-]/g, "")
    .replace(/,/g, "");
  return parseFloat(cleaned);
}

// --- Existing tests ---
console.log("formatCurrency tests:");
assert(formatCurrency(1234.56) === "$1,234.56", "formats basic amount");
assert(formatCurrency(1000, "EUR") === "€1,000.00", "formats EUR");
assert(formatCurrency(0) === "$0.00", "formats zero");

console.log("\nparseCurrency tests:");
assert(parseCurrency("$1,234.56") === 1234.56, "parses basic amount");
assert(parseCurrency("$0") === 0, "parses zero");

// --- New tests for fixed bugs ---
console.log("\nformatCurrency negative number tests:");
assert(formatCurrency(-50) === "-$50.00", "formats negative number");
assert(formatCurrency(-1234.56) === "-$1,234.56", "formats negative with thousand separator");
assert(formatCurrency(-0.99) === "-$0.99", "formats negative decimal");

console.log("\nformatCurrency decimal places tests:");
assert(formatCurrency(100) === "$100.00", "always shows 2 decimal places");
assert(formatCurrency(1) === "$1.00", "single digit shows 2 decimals");
assert(formatCurrency(0.5) === "$0.50", "half dollar shows 2 decimals");

console.log("\nparseCurrency multi-symbol tests:");
assert(parseCurrency("€1,234.56") === 1234.56, "parses EUR symbol");
assert(parseCurrency("£999.99") === 999.99, "parses GBP symbol");
assert(parseCurrency("€0.01") === 0.01, "parses EUR small amount");
assert(parseCurrency("-$50.00") === -50, "parses negative USD");
assert(parseCurrency("-€100.50") === -100.5, "parses negative EUR");

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
