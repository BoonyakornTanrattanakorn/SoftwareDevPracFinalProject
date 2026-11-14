// Send emails through the Resend email API (POST https://api.resend.com/emails)
// Docs: https://resend.com/docs/api-reference/emails/send-email

const TIMEOUT_MS = 5000;

// Escape text before putting it into the HTML email
const escapeHtml = (text) =>
  String(text).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );

const sendEmail = async ({ to, subject, text, html }) => {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    throw new Error("RESEND_API_KEY is not set in config/config.env");
  }

  const response = await fetch(
    process.env.RESEND_API_URL || "https://api.resend.com/emails",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        // Without a verified domain, Resend only allows onboarding@resend.dev as the sender
        from:
          process.env.EMAIL_FROM ||
          "Co-working Space Reservation <onboarding@resend.dev>",
        to: [to],
        subject,
        text,
        html,
      }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    },
  );

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Resend responded with status ${response.status}: ${detail}`);
  }
};

// Send the reservation confirmation email to the user who made the reservation
exports.sendReservationConfirmation = async (user, reservation, coworkingSpace) => {
  const date = new Date(reservation.reservationDate).toLocaleDateString(
    "en-GB",
    {
      timeZone: "Asia/Bangkok",
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    },
  );
  const subject = `Reservation confirmed: ${coworkingSpace.name} on ${date}`;

  const text = [
    `Hello ${user.name},`,
    "",
    "Your co-working space reservation is confirmed.",
    "",
    `Reservation ID: ${reservation._id}`,
    `Date: ${date}`,
    `Co-working space: ${coworkingSpace.name}`,
    `Address: ${coworkingSpace.address}`,
    `Telephone: ${coworkingSpace.tel}`,
    `Open: ${coworkingSpace.openTime} - ${coworkingSpace.closeTime}`,
    "",
    "Thank you for using our service.",
  ].join("\n");

  const html = `
    <p>Hello ${escapeHtml(user.name)},</p>
    <p>Your co-working space reservation is <b>confirmed</b>.</p>
    <table cellpadding="4">
      <tr><td>Reservation ID</td><td>${escapeHtml(reservation._id)}</td></tr>
      <tr><td>Date</td><td>${escapeHtml(date)}</td></tr>
      <tr><td>Co-working space</td><td>${escapeHtml(coworkingSpace.name)}</td></tr>
      <tr><td>Address</td><td>${escapeHtml(coworkingSpace.address)}</td></tr>
      <tr><td>Telephone</td><td>${escapeHtml(coworkingSpace.tel)}</td></tr>
      <tr><td>Open</td><td>${escapeHtml(coworkingSpace.openTime)} - ${escapeHtml(coworkingSpace.closeTime)}</td></tr>
    </table>
    <p>Thank you for using our service.</p>`;

  await sendEmail({ to: user.email, subject, text, html });
};