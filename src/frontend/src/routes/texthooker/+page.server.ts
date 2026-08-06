import type { StatusMapResponse, TexthookerLinesResponse } from '$lib/api_types/texthooker';

export const load = async ({ fetch, url }) => {
    
    // const fetchLastSession = async () => {
    //     let res = await fetch(`/api_bridge/texthooker/last_session?${url.searchParams.toString()}`);
	//     const {lines, status_map} = <LastSessionResponse> await res.json();
    //     return {lines, status_map};
    // }
    const curr_preset = url.searchParams.get("preset")?? "";

    const fetchLinesCount = async () => {
        let res = await fetch(`/api_bridge/texthooker/lines_count?${url.searchParams.toString()}`);
	    return <number> await res.json();
    }

    const fetchLines = async (limit: number, offset: number) => {
        let res = await fetch(`/api_bridge/texthooker/lines?${url.searchParams.toString()}&limit=${limit}&offset=${offset}`);
	    const {lines, start, length } = <TexthookerLinesResponse> await res.json();
        return {lines, start, length};
    }

    const fetchStatusMap = async () => {
        let res = await fetch(`/api_bridge/texthooker/status_map?${url.searchParams.toString()}`);
	    const { status_map } = <StatusMapResponse> await res.json();
        return status_map;
    }

    const fetchPresets = async () => {
        const res = await fetch("/api_bridge/texthooker/presets");
        const presets: string[] = await res.json();
        return presets;
    }

    const lines_count = await fetchLinesCount();
    // const chunk_size = Math.ceil(lines_count/5);
    const chunk_size = 50;
    // const chunks = Math.ceil(lines_count/chunk_size);
    // const lines_chunks = Array.from({ length: chunks }, (_, i) => fetchLines({preset: curr_preset, limit: chunk_size, offset: i*chunk_size, priority: (i === 0 || i == chunks-1)? "high" : "auto"}));
    
    // Load just first 50 lines and last 50 lines for a fast response. The rest will be loaded after the page is mounted.
    
    const lines_chunks = [fetchLines(chunk_size, 0)];

    if (lines_count-chunk_size > 0) {
        lines_chunks.push(fetchLines(chunk_size, Math.max(chunk_size, lines_count-chunk_size)));
    }

	return {
        status_map: fetchStatusMap(),
        lines_chunks: lines_chunks,
        lines_count: lines_count,
        chunk_size: chunk_size,
        presets: await fetchPresets(),
    };
};