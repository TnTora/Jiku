
export const load = async ({ fetch }) => {
    const res = await fetch("/api_bridge/texthooker/last_session");
	const {lines, status_map} = await res.json();
    // console.log(lines, status_map);
	return { lines, status_map };
};