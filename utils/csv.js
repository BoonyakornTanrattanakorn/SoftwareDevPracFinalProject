// Build CSV text (RFC 4180) from a header row and data rows

// Quote a value when it contains a comma, quote or new line.
// Values starting with = + - @ are prefixed with ' so spreadsheet apps do not run them as formulas.
const toCsvValue = (value) => {
  let text = value === undefined || value === null ? "" : String(value);
  if (/^[=+\-@]/.test(text)) text = `'${text}`;
  if (/[",\r\n]/.test(text)) text = `"${text.replace(/"/g, '""')}"`;
  return text;
};

exports.toCsv = (header, rows) => {
  const lines = [header, ...rows].map((row) => row.map(toCsvValue).join(","));
  // Start with a BOM so Excel opens Thai text as UTF-8
  return "\uFEFF" + lines.join("\r\n") + "\r\n";
};