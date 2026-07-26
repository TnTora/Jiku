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
	import { onMount, tick } from "svelte";

    interface TmpLine {
        id: number,
        raw: string,
        line: Promise<LineBase>,
    }

    let { data } = $props();
    // let lines = $derived(data.lines);
    let status_map = $derived(data.status_map);
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

    let text_container: HTMLDivElement;
    let text_container_offheight: number = $state(0);
    let text_container_offwidth: number = $state(0);


    $effect(() => {
        console.log(text_container_offheight, text_container_offwidth);
    });


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
            // console.log("scrollBottom");
        }
    }

    function scrollLeft () {
        if (isNearLeftMost()) {
            text_container?.scrollTo(-text_container.scrollWidth, 0);
            // console.log("scrollLeft");
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
                } as LineCreate)
                }, {
                    err_msg: "Failed to fetch new line",
                    err_context: errors,
            });

            let { id, text, tokens, line_status_map } = <LineResponse> await res.json();
            // console.log(tokens);
            status_map = {...status_map, ...line_status_map};
            return {id, text, tokens};
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


    // Virtual List
    let visible_html_elements: HTMLDivElement[] = $state([]);
    let height_map: number[] = [];
    let seen_items_count = 0;
    let average_item_height = $state(options.font_size * options.line_height);
    // let estimated_scroll_heigth: number = $derived(average_item_height*new_lines.length);
    let start: number = $state(0);
    let end: number = $state(0);
    let buffer = 5;

    // $effect(() => {
    //     $inspect(visible_lines);
    //     $inspect(visible_html_elements);
    // });

    let top_spacing = $state(0);

    let rendered_height = $state(0);

    let bottom_spacing: number = $derived(
        (end < new_lines.length)? (new_lines.length-end)*average_item_height:
        0
    );

    let visible_lines: (LineBase|TmpLine)[] = $derived.by(() => {
        return new_lines.slice(start, end);
    });

    $effect(() => {
        for (let j = 0; j < visible_html_elements.length; j++) {
            if (!visible_html_elements[j]) { continue; }

            if (height_map[start + j] === undefined) {
                height_map[start + j] = visible_html_elements[j].offsetHeight;
                average_item_height = ((average_item_height*seen_items_count)+visible_html_elements[j].offsetHeight)/(seen_items_count+1);
                seen_items_count++;
            }
		}
        // console.log(height_map);
    });

    $effect(() => { refreshVisibles(new_lines, text_container_offheight); });

    async function refreshVisibles(items: any[], container_offheight?: number) {
        if (!container_offheight) { return; }

        if (!items) {
            start = 0;
            end = 0;
            return;
        }

		const { scrollTop } = text_container;

        console.log("scrollTop refresh: ", scrollTop);

		await tick(); 

		let visible_height = top_spacing - scrollTop;

        if (visible_height+rendered_height > container_offheight+average_item_height) {
            return;
        }

		let i = start;

		while (visible_height < container_offheight && i < items.length) {
			let el = visible_html_elements[i - start];

			if (!el) {
				end = i + 1;
				await tick(); // await render of new element
				el = visible_html_elements[i - start];
			}

			visible_height += el.offsetHeight;
			i += 1;
		}

		end = i;

	}

    async function handle_scroll() {
		const { scrollTop } = text_container;

        console.log("scrollTop handle_scroll: ", scrollTop);

		let i = 0;
		let y = 0;
        let content_height = 0;

        await tick();

		while (i < new_lines.length) {
			const item_height = height_map[i] || average_item_height;
			if (y + item_height > scrollTop) {

                // apply buffer
                let start_buffer = i;
                let y_buffer = y;
                let j = 1;

                while (j <= buffer && start_buffer > 0) {
                    start_buffer--;
                    y_buffer = y_buffer - (height_map[i-j] || average_item_height);
                    j++;
                }

                start = start_buffer;
                top_spacing = y_buffer;

                content_height += item_height;
				break;

			}

			y += item_height;
			i += 1;
		}

		while (i < new_lines.length) {
            const item_height = height_map[i] || average_item_height;
            content_height += item_height;
			y += item_height;
			i += 1;

			if (y > scrollTop + text_container_offheight) break;
		}

		end = Math.min(i+buffer, new_lines.length);
        rendered_height = content_height;
	}

    // onMount(() => {
    //     visible_html_elements = text_container?.getElementsByTagName("div");;
    // });

</script>

<TopBar {toggleWebSocket} {ws_connected} {clearAllLines} toggleOptions={() => {show_options = !show_options}}/>

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
                // goto(`?preset=${new_preset}`);
                // options = loadOptions(new_preset);
            }}
        >
            {#each data.presets as preset}
                <option value={preset}>{preset}</option>
            {/each}
        </select>
    </div>

    <span class="mr-4">Lines: {start+1}-{end}/{line_counter}</span>
</div>


<div
    bind:this={text_container}
    bind:offsetHeight={text_container_offheight}
    bind:offsetWidth={text_container_offwidth}
    id="texthooker-container"
    class="relative pt-10 pb-6 w-full h-screen overflow-auto {options.vertical? "vert-rl pl-5 pr-2": ""}"
    style="line-height: {options.line_height};"
    onscroll={handle_scroll}
>
    <div style="padding-top: {top_spacing}px; padding-bottom: {bottom_spacing}px;">
        {#each visible_lines as line, index}
            <div bind:this={visible_html_elements[index]}>
                {#if isTmpLine(line)}
                    <!-- line added during current session -->
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
                {:else}
                    <!-- last session line -->
                    <TexthookerLine {line} status_map={status_map}
                        delete_func={() => {
                            new_lines = new_lines.filter( e => e.id !== line.id);
                            deleteLine(line.id);
                        }}
                    />
                {/if}
            </div>
        {/each}
    </div>
    
</div>

<style>
    
</style>

