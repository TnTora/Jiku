<script lang="ts">
    import { browser } from "$app/environment";
    import { page } from "$app/state";
    import { getJikuErrorsContext } from "$lib/utils/context.svelte.js";
    import { setTextHookerOptionsContext, type TextHookerOptions } from "./context.js";
    import TexthookerLine from "$lib/components/TexthookerLine.svelte";
    import TopBar from "./TopBar.svelte";
    import OptionPanel from "./OptionPanel.svelte";
	import { goto, invalidateAll } from "$app/navigation";
	import { api_fetch } from "$lib/utils/requests.js";
	import type { KnownStatus, LineBase, LineCreate, LineResponse, PresetUpdate, TexthookerStreamedLineResponse } from "$lib/api_types/texthooker.js";
	import VirtualList from "$lib/components/VirtualList.svelte";
	import { onMount, tick } from "svelte";

    interface TmpLine {
        id: number,
        raw: string,
        line: Promise<LineBase> | LineBase,
    }


    interface FetchLinesRequest {
        preset: string,
        limit: number,
        offset: number
    }


    let { data } = $props();
    let status_map: {[k: string]: KnownStatus} = $state({});
    let new_lines: (LineBase|TmpLine|number)[] = $state(Array.from({ length: data.lines_count }, () => 30+Math.floor(Math.random()*60)));
    // let new_lines: (LineBase|TmpLine)[] = $state(Array(data.lines_count));
    let load_failed = $state(false);

    // $effect(() => {
    //     $inspect(new_lines);
    //     $inspect(status_map);
    // })

    // svelte-ignore non_reactive_update
    let preset_name: string = page.url.searchParams.get("preset")?? "";

    if (browser) {
        // svelte-ignore state_referenced_locally
        if (!preset_name || !data.presets.includes(preset_name)) {
            goto(`/texthooker?preset=Default`);
        }
    }

    async function fetchLines ({preset, limit, offset}: FetchLinesRequest) {
        const res = await api_fetch(`/texthooker/lines_stream?preset=${preset}&limit=${limit}&offset=${offset}`, {headers: {"Accept": "application/jsonl"}});
        const reader = res.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) { return; }

        let buffer = ""

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                return;
            }

            buffer += decoder.decode(value, { stream: true });

            // console.log("value", buffer);
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
                const parsed: TexthookerStreamedLineResponse = JSON.parse(line);
                // console.log(parsed);
                new_lines[parsed.idx] = parsed.line;
                vlist.updateLengthMap(parsed.idx, undefined);
            }

        }
    }


    function loadLastSession() {
        data.status_map.then(
            (res) => { status_map = res; },
            (err) => {
                console.error(err);
                alert("Failed to load status map");
            }
        );

        for (let chunk of data.lines_chunks) {
            chunk.then(
                (res) => { new_lines.splice(res.start, res.length, ...res.lines); },
                () => { load_failed = true; } 
            );
        }
    }

    loadLastSession();

    let ws: WebSocket | null = null;
    let ws_connected = $state(false);

    let line_counter: number = $derived(new_lines.length);


    function isTmpLine(line: LineBase | TmpLine): line is TmpLine {
        return (line as TmpLine).line !== undefined;
    }

    function isLineBase(line: LineBase | Promise<LineBase>): line is LineBase {
        return (line as LineBase).tokens !== undefined;
    }


    function loadOptions(name: string) {
            let stored;

            if (browser) {
                stored = localStorage.getItem(`texthooker_preset_${name}`);
            }
            
            if (stored) {
                return JSON.parse(stored);
            } else {
                return {
                    websocket_url: "ws://localhost:6677",
                    font_size: 22,
                    line_height: 1.75,
                    vertical: false,
                }
            }

        }

    let options: TextHookerOptions = $state(loadOptions(preset_name));


    $effect(() => {
        // console.log(options);
        if (preset_name && options.websocket_url) {
            console.log(`update local storage: texthooker_preset_${preset_name}`);
            localStorage.setItem(`texthooker_preset_${preset_name}`, JSON.stringify(options));
        }
    });


    async function updateWS() {
        await api_fetch("texthooker/update_preset", {
            method: "PUT",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: preset_name,
                ws_url: options.websocket_url
            } as PresetUpdate)
        }, {
            err_msg: "Failed to update preset",
            err_context: errors,
        });
        console.log("ws_url updated in db");
    }


    let ws_update: ReturnType<typeof setTimeout> | undefined;


    $effect(() => {
        if (options.websocket_url) {
            if (ws_update === undefined) {
                ws_update = setTimeout(updateWS, 1000);
            } else {
                clearTimeout(ws_update);
                ws_update = setTimeout(updateWS, 1000);
            }
        }
    });


    setTextHookerOptionsContext(options);

    let show_options = $state(false);

    const errors = getJikuErrorsContext();

    // svelte-ignore non_reactive_update
    let text_container: HTMLDivElement;


    function isNearBottom(threshold = 100) {
        const rect = text_container.getBoundingClientRect();
        const scrollBottom = text_container.scrollTop + rect.height;
        console.log(scrollBottom, text_container.scrollHeight);
        return scrollBottom + threshold >= text_container.scrollHeight;
    }

    function isNearLeftMost(threshold = 100) {
        const rect = text_container.getBoundingClientRect();
        const scrollRight = text_container.scrollLeft - rect.width;
        // console.log(scrollRight);
        return -scrollRight + threshold >= text_container.scrollWidth;
    }

    let isNearLast = $derived(options.vertical? isNearLeftMost: isNearBottom);

    let getOffsetLength = $derived(
        options.vertical?
        () => { return text_container.offsetWidth; }:
        () => { return text_container.offsetHeight; }
    );

    let getScrollPosition = $derived(
        options.vertical?
        () => { return -text_container.scrollLeft; }:
        () => { return text_container.scrollTop; }
    );

    let getScrollLength = $derived(
        options.vertical?
        () => { return text_container.scrollWidth; }:
        () => { return text_container.scrollHeight; }
    );


    async function processNewLine(new_line: string) {
        const res = await api_fetch("texthooker/new_line", {
            method: "POST",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                text: new_line,
                preset: preset_name,
            } as LineCreate)
            }, {
                err_msg: "Failed to fetch new line",
                err_context: errors,
        });

        let { id, text, tokens, line_status_map } = <LineResponse> await res.json();
        // console.log(tokens);
        status_map = {...status_map, ...line_status_map};
        return {id, text, tokens};
    }

    async function deleteLine(line_id: number) {
        await api_fetch(`texthooker/line/${line_id}`, {
                method: "DELETE",
            }, {
                err_msg: "Failed to delete line",
                err_context: errors
        });
        const line_idx = new_lines.findIndex((e) => (e as LineBase|TmpLine).id === line_id);
        vlist.deleteItem(line_idx);
    }

    async function clearAllLines() {
        await api_fetch(`texthooker/clear_lines/${preset_name}`, {
                method: "DELETE",
            }, {
                err_msg: "Failed to clear lines",
                err_context: errors,
        });
        
        // new_lines.length = 0;
        vlist.clearItems();
        invalidateAll();
        // new_lines = [];

    }

    let new_line_tmp_id = -1;

    function addNewLine(new_line: string) {
        let tmp: TmpLine = $state({
            id: new_line_tmp_id,
            raw: new_line,
            line: processNewLine(new_line),
        });
        const curr_tmp_id = new_line_tmp_id;
        new_line_tmp_id--;
        
        const near_last: boolean = isNearLast();
        new_lines.push(tmp);

        // tick().then(scrollToLast);
        if (near_last) {
            tick().then(scrollToLast);
        }

        (tmp.line as Promise<LineBase>).then((line) => {
            tmp.line = line;
            tmp.id = line.id;
        }, () => {
            const index = new_lines.findIndex((el) => (el as LineBase|TmpLine).id === curr_tmp_id );
            vlist.deleteItem(index);
        });
    }

    function toggleWebSocket() {
        if (!options.websocket_url) {
            errors.push({
                short: "No WebSocket URL set in options"
            });
            return;
        };

        if (ws == null) {
            ws = new WebSocket(options.websocket_url);

            ws.addEventListener('open', () => {
                console.log("websocket opened");
                ws_connected = true;
            });

            ws.addEventListener('close', () => {
                console.log("websocket closed");
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
                });
                ws = null;
            });

        } else {
            ws.close();
            ws = null;
        }

    }


    // Virtual List
    // svelte-ignore non_reactive_update
    let vlist: ReturnType<typeof VirtualList>;
    
    let vertical = $derived(options.vertical);
    let guessed_item_size = $derived(options.font_size * options.line_height);

    let start: number = $state(0);
    let end: number = $state(0);
    let buffer = 5;

    function scrollToLast() {
        vlist.scrollToIndex(-1);
        
        setTimeout(() => {
            const scroll_length = getScrollLength();
            const scroll_pos = getScrollPosition();
            const container_offlength = getOffsetLength();

            if ((scroll_pos + container_offlength) >= scroll_length) {
                return;
            }

            const target = options.vertical? 
                {left: -scroll_length} :
                {top: scroll_length} ;

            text_container.scrollTo(target);

        }, 100);
    }


    onMount(() => {
        if (data.lines_count > 2*data.chunk_size) {
            fetchLines({preset: preset_name, limit: data.lines_count-data.chunk_size, offset: data.chunk_size});
        }
    });

</script>

<TopBar {toggleWebSocket} {ws_connected} {clearAllLines} {scrollToLast} toggleOptions={() => {show_options = !show_options}}/>

{#if show_options}
    <OptionPanel presets={data.presets} bind:preset_name={preset_name} onoutsideclick={() => {show_options = false}}/>
{/if}

<div class="h-screen flex flex-col">
    {#if load_failed}
        <p
            class="pt-10"
            style="line-height: {options.line_height}; font-size: {options.font_size}px"
        >
            Failed to load lines
        </p>
    {:else}
        <VirtualList
            bind:this={vlist}
            bind:container={text_container}
            bind:start_idx={start}
            bind:end_idx={end}
            items={new_lines}
            {vertical}
            {guessed_item_size}
            {buffer}
            id="texthooker-container"
            class="relative pt-10 pb-6 w-full grow overflow-auto {options.vertical? "vert-rl pl-5 pr-2": ""}"
            style="line-height: {options.line_height};"
        >
            {#snippet render_item(line, index)}
                {#if typeof line === 'number' }
                    <div
                        class="my-4 mx-5 shimmer rounded-full"
                        style="height: {options.font_size}px; width: {line}%"
                    ></div>
                {:else if isTmpLine(line)}
                    <!-- line added during current session -->
                    <!-- avoid await block as it resulted in jumps due to wrong size being detected -->
                    {#if line.id < 0}
                        <p
                            class="my-1 py-1 px-5 whitespace-pre-wrap"
                            style="font-size: {options.font_size}px;"
                            // {@attach (el: HTMLParagraphElement) => {
                            //     console.log("p offset", el.parentElement?.offsetHeight)
                            //     const parent_length = el.parentElement?.offsetHeight;
                            //     if (parent_length !== undefined) {
                            //         vlist.updateLengthMap(index, parent_length);
                            //     }
                            // }}
                        >
                            {line.raw}
                        </p>
                    {:else if isLineBase(line.line)} 
                        <TexthookerLine line={line.line} status_map={status_map}
                            delete_func={ () => { 
                                deleteLine(line.id);
                            } }
                            {@attach (el: HTMLDivElement) => {
                                // console.log("div offset", el.parentElement?.offsetHeight);
                                const parent_length = el.parentElement?.offsetHeight;
                                if (parent_length !== undefined) {
                                    vlist.updateLengthMap(index, parent_length);
                                }
                            }}
                        />
                    {/if}
                {:else}
                    <!-- last session line -->
                    <TexthookerLine {line} status_map={status_map}
                        delete_func={() => {
                            deleteLine(line.id);
                        }}
                    />
                {/if}
            {/snippet}
        </VirtualList>
    {/if}

    <div class="grow-0 shrink-0 w-full bottom-0 pt-0.5 pb-1 flex items-center justify-end gap-4 text-xs text-neutral-500 border-t border-neutral-700 bg-neutral-800 z-10">   
        <div class="absolute left-[50%] -translate-x-[50%] flex items-center justify-between gap-4 px-2">
            <label for="preset">Preset:</label>
            <select id="preset" bind:value={preset_name}
                class="max-w-40"
                onchange={(event) => {
                    const new_preset = (event.target as HTMLSelectElement).value;
                    window.location.href = `?preset=${new_preset}`;
                }}
            >
                {#each data.presets as preset}
                    <option value={preset}>{preset}</option>
                {/each}
            </select>
        </div>
    
        <span class="mr-4">Lines: {start+1}-{end}/{line_counter}</span>
    </div>

</div>

<style>
    .shimmer {
        background: linear-gradient(to right, #3e3e3e 30%,#DCDCDC 50%,#3e3e3e 70%);
        background-size: 400%;
        animation: shimmer 1.5s infinite linear;
    }

    @keyframes shimmer {
	0% {
		background-position: 100%;
	}
	100% {
		background-position: 0%;
	}
}
</style>

