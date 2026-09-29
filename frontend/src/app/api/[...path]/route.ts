type RouteContext = {
  params: {
    path: string[];
  };
};

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

  const requestOptions: RequestInit = {
    method: request.method,
    headers: requestHeaders,
    cache: 'no-store',
  };

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    requestOptions.body = await request.arrayBuffer();
  }

  try {
    const backendResponse = await fetch(backendUrl, requestOptions);
    const responseHeaders = new Headers(backendResponse.headers);
    responseHeaders.delete('connection');
    responseHeaders.delete('transfer-encoding');

    return new Response(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });
  } catch {
    return Response.json({ detail: 'Backend service is unavailable' }, { status: 502 });
  }
}

export const GET = proxy;
export const HEAD = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;