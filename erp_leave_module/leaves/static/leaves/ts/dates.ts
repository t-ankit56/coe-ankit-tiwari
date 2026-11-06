const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const SHORT_WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const LONG_WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

interface CalendarDate {
  year: number;
  month: number; // 0-11
  day: number;
  weekday: number; // 0 = Sunday
}

function parse(isoDate: string): CalendarDate {
  const [year, month, day] = isoDate.slice(0, 10).split("-").map(Number);
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay();
  return { year, month: month - 1, day, weekday };
}

/** "11 Nov 2026", "24 – 28 Dec 2026", "30 Nov – 1 Dec 2026" or "31 Dec 2026 – 1 Jan 2027". */
export function formatDateRange(startIso: string, endIso: string): string {
  const start = parse(startIso);
  const end = parse(endIso);
  if (startIso === endIso) return `${start.day} ${MONTHS[start.month]} ${start.year}`;
  if (start.year !== end.year) {
    return `${start.day} ${MONTHS[start.month]} ${start.year} – ${end.day} ${MONTHS[end.month]} ${end.year}`;
  }
  if (start.month !== end.month) {
    return `${start.day} ${MONTHS[start.month]} – ${end.day} ${MONTHS[end.month]} ${end.year}`;
  }
  return `${start.day} – ${end.day} ${MONTHS[end.month]} ${end.year}`;
}

/** "Wednesday" for one day, "Thu to Mon" for a range. */
export function describeWeekdays(startIso: string, endIso: string): string {
  const start = parse(startIso);
  if (startIso === endIso) return LONG_WEEKDAYS[start.weekday];
  return `${SHORT_WEEKDAYS[start.weekday]} to ${SHORT_WEEKDAYS[parse(endIso).weekday]}`;
}

/** "2 Nov" */
export function formatShortDate(isoDate: string): string {
  const date = parse(isoDate);
  return `${date.day} ${MONTHS[date.month]}`;
}

/** "Mon 23 Nov" */
export function formatDayLabel(isoDate: string): string {
  const date = parse(isoDate);
  return `${SHORT_WEEKDAYS[date.weekday]} ${date.day} ${MONTHS[date.month]}`;
}
