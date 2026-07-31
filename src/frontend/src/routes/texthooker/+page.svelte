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
	import type { LineBase, LineCreate, LineResponse, PresetUpdate } from "$lib/api_types/texthooker.js";
	import VirtualList from "$lib/components/VirtualList.svelte";
	import { tick } from "svelte";

    interface TmpLine {
        id: number,
        raw: string,
        line: Promise<LineBase>,
    }

    let { data } = $props();
    // let lines = $derived(data.lines);
    let status_map = $derived(data.status_map);
    // svelte-ignore state_referenced_locally
    let new_lines: (LineBase|TmpLine)[] = $state(data.lines);
    let ws: WebSocket | null = null;
    let ws_connected = $state(false);

    let line_counter: number = $derived(new_lines.length);


    function isTmpLine(line: LineBase | TmpLine): line is TmpLine {
        return (line as TmpLine).line !== undefined;
    }


    // svelte-ignore non_reactive_update
    let preset_name: string = page.url.searchParams.get("preset")?? "";

    if (browser) {
        // svelte-ignore state_referenced_locally
        if (!preset_name || !data.presets.includes(preset_name)) {
            goto(`/texthooker?preset=Default`);
        }
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
        const line_idx = new_lines.findIndex(e => e.id === line_id);
        if (line_idx > -1) {
            vlist.deleteItem(line_idx);
        }
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

    function addNewLine(new_line: string) {
        let tmp = {
            id: -1,
            raw: new_line,
            line: processNewLine(new_line),
        };
        new_lines.push(tmp);

        // tick().then(scrollToLast);
        if (isNearLast()) {
            tick().then(scrollToLast);
        }

        tmp.line.then((line) => {
            tmp.id = line.id;
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

</script>

<TopBar {toggleWebSocket} {ws_connected} {clearAllLines} {scrollToLast} toggleOptions={() => {show_options = !show_options}}/>

{#if show_options}
    <OptionPanel presets={data.presets} bind:preset_name={preset_name} onoutsideclick={() => {show_options = false}}/>
{/if}


<div class="fixed w-full bottom-0 pt-0.5 pb-1 flex items-center justify-end gap-4 text-xs text-neutral-500 bg-neutral-800 z-10">   
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
    class="relative pt-10 pb-6 w-full h-screen overflow-auto {options.vertical? "vert-rl pl-5 pr-2": ""}"
    style="line-height: {options.line_height};"
>
    {#snippet render_item(line, index)}
        {#if isTmpLine(line)}
            <!-- line added during current session -->
            {#await line.line}
                <p
                    class="my-1 py-1 px-5 whitespace-pre-wrap"
                    style="font-size: {options.font_size}px;"
                >
                    {line.raw}
                </p>
            {:then line} 
                <TexthookerLine {line} status_map={status_map}
                    delete_func={ () => { 
                        deleteLine(line.id);
                    } }
                />
            {/await}
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

<style>
    
</style>

