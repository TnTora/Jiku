
export const load = async () => {
    const res = await fetch("http://127.0.0.1:8000/texthooker/last_session");
	const {lines, status_map} = await res.json();
    console.log(lines, status_map)
	return { lines, status_map };
};