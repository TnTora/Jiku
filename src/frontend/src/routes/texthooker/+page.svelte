<script lang="ts">
import { getJikuErrorsContext } from "$lib/utils/context.js";
import { setTextHookerOptionsContext } from "./context.js";
import TexthookerLine from "$lib/components/TexthookerLine.svelte";
import TopBar from "./TopBar.svelte";
import OptionPanel from "./OptionPanel.svelte";

let { data } = $props();
let lines = $state(data.lines);
let status_map = $state(data.status_map);
let new_lines: any[] = $state([]);
let ws: WebSocket | null = null;
let ws_connected = $state(false);

let options = $state({
    preset_name: "Default",
    websocket_url: "ws://localhost:6677",
    font_size: 22,
    vertical: false,
});

setTextHookerOptionsContext(options);

let line_counter = $derived(lines.length+new_lines.length);

let show_options = $state(false);

const errors = getJikuErrorsContext();

let text_container: HTMLDivElement | undefined;

function isNearBottom(threshold = 100) {
    if (!text_container) { return false };
    const rect = text_container.getBoundingClientRect();
    const scrollBottom = text_container.scrollTop + rect.height;
    return scrollBottom + threshold >= text_container.scrollHeight;
}

function isNearLeftMost(threshold = 100) {
    if (!text_container) { return false };
    const rect = text_container.getBoundingClientRect();
    const scrollRight = text_container.scrollLeft - rect.width;
    // console.log(scrollRight);
    return -scrollRight + threshold >= text_container.scrollWidth;
}

function scrollBottom () {
    if (isNearBottom()) {
        text_container?.scrollTo(0, text_container.scrollHeight);
        console.log("scrollBottom");
    }
}

function scrollLeft () {
    if (isNearLeftMost()) {
        text_container?.scrollTo(-text_container.scrollWidth, 0);
        console.log("scrollLeft");
    }
}

let scrollToLast = $derived(options.vertical? scrollLeft: scrollBottom);

async function processNewLine(new_line: string) {
    try {
        const res = await fetch("http://127.0.0.1:8000/texthooker/new_line", {
            method: "POST",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({text: new_line})
        });

        let { id, tokens, line_status_map } = await res.json();
        // console.log(tokens);
        status_map = {...status_map, ...line_status_map};
        return {id, tokens};
    } catch (error) {
        console.error("Error fetching new line: ", error);
        errors.push({
            short: "Error fetching new line",
            details: error,
        });
        throw error;
    }

}

async function deleteLine(line_id: number) {
    try {
        const res = await fetch(`http://127.0.0.1:8000/texthooker/line/${line_id}`, {
            method: "DELETE",
        });
    } catch (error) {
        console.error("Error deleting line: ", error);
        errors.push({
            short: "Error deleting line",
            details: error,
        });
        throw error;
    }

}

async function clearAllLines(line_id: number) {
    try {
        const res = await fetch(`http://127.0.0.1:8000/texthooker/clear_lines`, {
            method: "DELETE",
        });
    } catch (error) {
        console.error("Error clearing lines: ", error);
        errors.push({
            short: "Error clearing lines",
            details: error,
        });
        throw error;
    }

}

function addNewLine(new_line: string) {
    let tmp = {
        id: -1,
        raw: new_line,
        line: processNewLine(new_line),
    };
    new_lines.push(tmp);
    tmp.line.then((line) => {
        tmp.id = line.id;
    });
}

function toggleWebSocket() {
    if (!options.websocket_url) {
        // TODO: inform user that no websocket is found in options.
        return;
    };

    if (ws == null) {
        ws = new WebSocket(options.websocket_url);

        ws.addEventListener('open', () => {
            ws_connected = true;
        });

        ws.addEventListener('close', () => {
            ws_connected = false;
        });

        ws.addEventListener("message", (event) => {
            let line = JSON.parse(event.data)?.sentence?? event.data;
            // console.log(line);
            addNewLine(line);
        })

        ws.addEventListener('error', (err) => {
            console.error('WS error: ', err);
            errors.push({
                short: "WebSocket Error",
                details: err,
            });
        });

    } else {
        ws.close();
        ws = null;
    }

}
</script>

<TopBar {toggleWebSocket} {ws_connected} {clearAllLines} toggleOptions={() => {show_options = !show_options}}/>

{#if show_options}
    <OptionPanel onoutsideclick={() => {show_options = false}}/>
{/if}

<div class="fixed bottom-1 left-[50%] -translate-x-[50%] z-9 flex items-center justify-between gap-4 text-xs text-neutral-500 bg-neutral-800 px-2 rounded-full">
    <label for="preset">Preset:</label>
    <select id="preset" bind:value={options.preset_name}>
        <option value="Default">Default</option>
    </select>
</div>


<div bind:this={text_container} class="relative pt-10 pb-6 w-full h-screen overflow-scroll {options.vertical? "vert-rl pl-5 pr-2": ""}">
    <!-- last session lines -->
    {#each lines as line}
        <TexthookerLine {line} {status_map}
            delete_func={() => {
                lines = lines.filter( e => e.id !== line.id);
                deleteLine(line.id);
            }} />
    {/each}

    <!-- lines added during current session -->
    {#each new_lines as line}
        {#await line.line}
            <p 
            {@attach () => { scrollToLast() }}
            class="my-1 py-1 px-5 whitespace-pre-wrap"
            style="font-size: {options.font_size}px;">{line.raw}</p>
        {:then line} 
            <TexthookerLine {line} {status_map} 
                delete_func={ () => { 
                    new_lines = new_lines.filter( e => e.id !== line.id );
                    deleteLine(line.id);
                } }
            />
        {/await}
    {/each}
</div>

<style>
    
</style>

