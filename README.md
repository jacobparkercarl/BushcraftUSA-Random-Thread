# BushcraftUSA-Random-Thread

One-click random thread redirect for [bushcraftusa.com](https://bushcraftusa.com), a XenForo forum. Thread IDs are just an incrementing counter and `/threads/{id}` resolves to the canonical URL, so this picks a random ID and 302s you there, retrying server-side if it lands on a deleted or restricted thread.

## How it works

`lambda_function.py` is the Lambda handler behind a public Function URL. It picks a random ID in `[MIN_ID, MAX_ID]`, does a server-side GET to confirm it resolves, retries up to `MAX_ATTEMPTS` times, then falls back to a known-good thread ID if nothing resolves.

## Deploy

1. Create a Lambda function, Python 3.13+ runtime (stdlib only, no dependencies/layers).
2. Paste in `lambda_function.py`.
3. Code tab -> Runtime settings -> Edit -> set Handler to `lambda_function.handler`.
4. Configuration -> General configuration -> set Timeout to 10s (the default 3s isn't enough for the retry loop).
5. Configuration -> Function URL -> create, Auth type `NONE`.
6. Configuration -> Concurrency -> reserve 1-2. Optional, but worth it on a public unauthenticated endpoint.
7. Bookmark the Function URL.

## Zero-infra alternative

A bookmarklet does the same thing client-side with no retry, if you'd rather skip AWS entirely:

```javascript
javascript:location.href='https://bushcraftusa.com/threads/'+(Math.floor(Math.random()*407500)+1)
```

## Maintenance

`MAX_ID` needs bumping every few months, the forum adds roughly 35 threads a day. Check the current highest thread ID on the site's "New posts" page and update the constant.

## Debugging

Each attempt logs `id=... status=...` or `id=... http_error=...` to CloudWatch under `/aws/lambda/<function-name>`. If every attempt is failing (redirecting straight to the fallback thread), it's usually the site's bot protection rejecting the request, check the User-Agent header first.
