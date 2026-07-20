
export const load = async ({ fetch, url }) => {
    let res = await fetch(`/api_bridge/texthooker/last_session?${url.searchParams.toString()}`);
	const {lines, status_map} = await res.json();
    res = await fetch("/api_bridge/texthooker/presets");
    const presets = await res.json();
    // console.log(lines, status_map);
	return { lines, status_map, presets };
};