// Backend timestamps are UTC but serialized without a zone suffix.
export function parseTimestamp(value: string): Date {
  return new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(value) ? value : `${value}Z`);
}

export function minutesSince(value: string, now: number): number {
  return Math.max(0, Math.floor((now - parseTimestamp(value).getTime()) / 60000));
}

export function ordinal(n: number): string {
  const mod100 = n % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${n}th`;
  return `${n}${{ 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] ?? 'th'}`;
}
