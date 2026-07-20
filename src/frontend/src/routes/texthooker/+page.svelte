<script lang="ts">
    import { browser } from "$app/environment";
    import { page } from "$app/state";
    import { getJikuErrorsContext } from "$lib/utils/context.svelte.js";
    import { setTextHookerOptionsContext } from "./context.js";
    import TexthookerLine from "$lib/components/TexthookerLine.svelte";
    import TopBar from "./TopBar.svelte";
    import OptionPanel from "./OptionPanel.svelte";
	import { goto, invalidateAll } from "$app/navigation";
	import { api_fetch } from "$lib/utils/requests.js";

    let { data } = $props();
    let lines = $derived(data.lines);
    let status_map = $derived(data.status_map);
    let new_lines: any[] = $state([]);
    let ws: WebSocket | null = null;
    let ws_connected = $state(false);


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

    let options = $state(loadOptions(preset_name));


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
            })
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
            const res = await api_fetch("texthooker/new_line", {
                method: "POST",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    text: new_line,
                    preset: preset_name,
                })
                }, {
                    err_msg: "Failed to fetch new line",
                    err_context: errors,
            });

            let { id, tokens, line_status_map } = await res.json();
            // console.log(tokens);
            status_map = {...status_map, ...line_status_map};
            return {id, tokens};
        } catch (error) {
            throw error;
        }

    }

    async function deleteLine(line_id: number) {
        await api_fetch(`texthooker/line/${line_id}`, {
                method: "DELETE",
            }, {
                err_msg: "Failed to delete line",
                err_context: errors
        });
    }

    async function clearAllLines() {
        await api_fetch(`texthooker/clear_lines/${preset_name}`, {
                method: "DELETE",
            }, {
                err_msg: "Failed to clear lines",
                err_context: errors,
        });
        
        invalidateAll();
        new_lines = [];

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
</script>

<TopBar {toggleWebSocket} {ws_connected} {clearAllLines} toggleOptions={() => {show_options = !show_options}}/>

{#if show_options}
    <OptionPanel presets={data.presets} bind:preset_name={preset_name} onoutsideclick={() => {show_options = false}}/>
{/if}

<div class="fixed bottom-1 left-[50%] -translate-x-[50%] z-9 flex items-center justify-between gap-4 text-xs text-neutral-500 bg-neutral-800 px-2 rounded-full">
    <label for="preset">Preset:</label>
    <select id="preset" bind:value={preset_name}
        onchange={(event) => {
            const new_preset = (event.target as HTMLSelectElement).value;
            window.location.href = `?preset=${new_preset}`;
            // goto(`?preset=${new_preset}`);
            // options = loadOptions(new_preset);
        }}
    >
        {#each data.presets as preset}
            <option value={preset}>{preset}</option>
        {/each}
    </select>
</div>


<div bind:this={text_container} class="relative pt-10 pb-6 w-full h-screen overflow-scroll {options.vertical? "vert-rl pl-5 pr-2": ""}"
    style="line-height: {options.line_height}"
>
    <!-- last session lines -->
    {#each lines as line}
        <TexthookerLine {line} status_map={status_map}
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
            <TexthookerLine {line} status_map={status_map}
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

