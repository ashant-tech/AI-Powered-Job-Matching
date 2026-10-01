type RouteContext = {
  params: {
    path: string[];
  };
};

// Render free web services sleep after inactivity; the first request pays for a
// cold start. Retry upstream failures that indicate "waking up" so a login
// right after idle succeeds instead of erroring.
const RETRYABLE_STATUS = new Set([502, 503, 504]);
const MAX_ATTEMPTS = 4;
const BACKOFF_MS = [1000, 3000, 6000];

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function proxy(request: Request, { params }: RouteContext) {
  const backendHost = process.env.BACKEND_HOST;

  if (!backendHost) {
    return Response.json({ detail: 'Backend host is not configured' }, { status: 500 });
  }

  const protocol = process.env.BACKEND_PROTOCOL || 'https';
  const requestUrl = new URL(request.url);
  const backendUrl = `${protocol}://${backendHost}/api/${params.path.join('/')}${requestUrl.search}`;
  const requestHeaders = new Headers(request.headers);
  requestHeaders.delete('connection');
  requestHeaders.delete('host');

  const body = request.method !== 'GET' && request.method !== 'HEAD'
    ? await request.arrayBuffer()
    : undefined;

  let lastStatus = 502;
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    try {
      const backendResponse = await fetch(backendUrl, {
        method: request.method,
        headers: requestHeaders,
        cache: 'no-store',
        body,
      });

      if (RETRYABLE_STATUS.has(backendResponse.status) && attempt < MAX_ATTEMPTS - 1) {
        lastStatus = backendResponse.status;
        await backendResponse.body?.cancel().catch(() => {});
        await sleep(BACKOFF_MS[attempt]);
        continue;
      }

      const responseHeaders = new Headers(backendResponse.headers);
      responseHeaders.delete('connection');
      responseHeaders.delete('content-encoding');
      responseHeaders.delete('content-length');
      responseHeaders.delete('transfer-encoding');

      return new Response(backendResponse.body, {
        status: backendResponse.status,
        statusText: backendResponse.statusText,
        headers: responseHeaders,
      });
    } catch {
      lastStatus = 502;
      if (attempt < MAX_ATTEMPTS - 1) {
        await sleep(BACKOFF_MS[attempt]);
      }
    }
  }

  return Response.json(
    { detail: 'Backend service is starting up or unavailable. Please try again in a moment.' },
    { status: lastStatus }
  );
}

export const GET = proxy;
export const HEAD = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;
