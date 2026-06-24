import { env } from '$env/dynamic/private';
import type { RequestHandler } from "./$types";

// https://grantyap.com/blog/forwarding-requests-to-api-endpoints-in-sveltekit-without-a-reverse-proxy
const handle: RequestHandler = async ({ url, params, request, fetch }) => {
	const { endpoint } = params;

	let api_url = `http://${env.BACKEND_HOST}:${env.BACKEND_PORT}/${params.endpoint}`;
    const search_params = url.searchParams.toString();
    if (search_params) {
        api_url = api_url + `?${search_params}`;
    }

	// Keep the exact same request with a different URL.
	const newRequest = new Request(api_url, request);

	// Important!
	// The original request's `Host` value is *this* server. If this header
	// does not match the server that it's intended for, then `fetch` will
	// 404 and throw an `UNABLE_TO_VERIFY_LEAF_SIGNATURE` error. To avoid this,
	// we simply remove the `Host` header.
	// newRequest.headers.delete('host');

	// console.log("newRequest", newRequest);

	return await fetch(newRequest);
};

export {
	handle as GET,
	handle as POST,
	handle as DELETE,
	handle as PUT,
	handle as PATCH,
	handle as OPTIONS,
};
