import type { LastSessionResponse } from '$lib/api_types/texthooker.js';

export const load = async ({ fetch, url }) => {
    let res = await fetch(`/api_bridge/texthooker/last_session?${url.searchParams.toString()}`);
	const {lines, status_map} = <LastSessionResponse> await res.json();
    res = await fetch("/api_bridge/texthooker/presets");
    const presets: string[] = await res.json();
    // console.log(lines, status_map);
	return { lines, status_map, presets };
};