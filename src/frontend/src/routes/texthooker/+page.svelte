<script lang="ts">
import { getContext } from "svelte";
import TexthookerLine from "$lib/components/TexthookerLine.svelte";
import TopBar from "./TopBar.svelte";

let { data } = $props();
let lines = $state(data.lines);
let status_map = $state(data.status_map);
let new_lines: any[] = $state([]);
let ws: WebSocket | null = null;
let ws_connected = $state(false);
let vertical = $state(true);

const errors = getContext("errors");

let text_container: HTMLDivElement | undefined;

function isNearBottom(threshold = 50) {
    if (!text_container) { return false };
    const rect = text_container.getBoundingClientRect();
    const scrollBottom = text_container.scrollTop + rect.height;
    return scrollBottom + threshold >= text_container.scrollHeight;
}

function isNearLeftMost(threshold = 50) {
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

function addNewLine(new_line: string) {
    let preprocessed_line = new_line.replaceAll("\n", " ");
    let tmp = {
        id: -1,
        raw: preprocessed_line,
        line: processNewLine(preprocessed_line),
    };
    new_lines.push(tmp);
    tmp.line.then((line) => {
        tmp.id = line.id;
    });
}

function toggleWebSocket() {
    if (ws == null) {
        ws = new WebSocket("ws://localhost:6677");

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

<TopBar {toggleWebSocket} {ws_connected} />

<div bind:this={text_container} class="relative pt-10 pb-5 w-full h-screen overflow-scroll {vertical? "vert-rl pl-5 pr-2": ""}">
    <!-- last session lines -->
    {#each lines as line}
        <TexthookerLine {line} {status_map} delete_func={() => { lines = lines.filter( e => e.id !== line.id)}} />
    {/each}

    <!-- lines added during current session -->
    {#each new_lines as line}
        {#await line.line}
            <p 
            {@attach () => { scrollToLast() }}
            class="my-1 py-1 px-5 text-[22px]"
            style="font-size: {options.font_size}px;">{line.raw}</p>
        {:then line} 
            <TexthookerLine {line} {status_map} delete_func={ () => { new_lines = new_lines.filter( e => e.id !== line.id )} }/>
        {/await}
    {/each}
</div>

<style>
    
</style>

