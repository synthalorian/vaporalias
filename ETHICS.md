# Ethics: self-scan only

Vaporalias exists so you can see what the internet links to **your own** identity
before somebody else connects the dots. It is a mirror. Point it at yourself.

## The rules

1. **Scan only yourself.** The alias and real name you enter must both be
   yours. The `--i-am-this-person` flag is your statement that this is true.
   The tool won't run without it.
2. **Don't use it to deanonymize, stalk, harass or "dox" anyone.** Running it
   against another person defeats the whole point of the tool, and in many
   places it may also be illegal.
3. **Offline by default.** Without `--live` it builds URLs and prints them,
   and sends nothing. With `--live` it sends one plain GET to each listed
   profile page for your alias, and nothing more. It doesn't log in, scrape
   search engines, get around rate limits, or follow links.
4. **Nothing leaves your machine.** No telemetry, no uploads. Results go to
   your terminal and nowhere else.
5. **Respect the sites you query.** Live mode is meant for occasional manual
   runs, not loops, cron jobs or bulk lists.

## Helping someone else

If a friend or client wants a scan, they run it themselves on their own
machine with their own details. Walk them through it, but don't run it for
them on your machine.

## Limits

A clean result doesn't mean you're invisible. The site list is short, profile
pages can hide names behind JavaScript or logins, and data brokers change
their opt-out pages all the time. Treat the output as a starting point and
don't rely on it as a guarantee.
