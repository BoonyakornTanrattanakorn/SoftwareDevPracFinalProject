// Check Thai public holidays in real time with the Calendarific API
// Docs: https://calendarific.com/api-documentation

// Give up on the holiday API after 2 seconds (the whole request must answer within 3 seconds)
const TIMEOUT_MS = 2000;

// Date (year, month, day) of a reservation in Thailand time (UTC+7)
const toThaiDate = (date) => {
  const thaiTime = new Date(date.getTime() + 7 * 60 * 60 * 1000);
  return {
    year: thaiTime.getUTCFullYear(),
    month: thaiTime.getUTCMonth() + 1,
    day: thaiTime.getUTCDate(),
    iso: thaiTime.toISOString().slice(0, 10),
  };
};

// Return the holiday if the date is a Thai public holiday, otherwise null.
// Throw an error if the holiday API cannot be used (no API key, network error, timeout, ...)
exports.findThaiPublicHoliday = async (date) => {
  const apiKey = process.env.CALENDARIFIC_API_KEY;
  if (!apiKey) {
    throw new Error("CALENDARIFIC_API_KEY is not set in config/config.env");
  }

  const { year, month, day, iso } = toThaiDate(date);
  const url = new URL(
    process.env.HOLIDAY_API_URL || "https://calendarific.com/api/v2/holidays",
  );
  url.search = new URLSearchParams({
    api_key: apiKey,
    country: "TH",
    year,
    month,
    day,
    type: "national", // public and bank holidays only (no observances)
  });

  const response = await fetch(url, {
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  if (!response.ok) {
    throw new Error(`Holiday API responded with status ${response.status}`);
  }

  const data = await response.json();
  const holidays = (data.response && data.response.holidays) || [];

  return (
    holidays.find((holiday) => holiday.date.iso.slice(0, 10) === iso) || null
  );
};