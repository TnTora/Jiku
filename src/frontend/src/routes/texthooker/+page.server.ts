
export const load = async ({ fetch, url }) => {
    const res = await fetch(`/api_bridge/texthooker/last_session?${url.searchParams.toString()}`);
	const {lines, status_map} = await res.json();
    // console.log(lines, status_map);
	return { lines, status_map };
};