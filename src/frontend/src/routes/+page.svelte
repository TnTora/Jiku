<script lang="ts">
    import { browser } from "$app/environment";
    import KnownBar from "$lib/components/KnownBar.svelte";
    import BookCarousel from "$lib/components/BookCarousel.svelte";

    let { data } = $props();
    let btn_shared = "bg-neutral-700 hover:bg-neutral-900 active:bg-neutral-950 cursor-pointer";

    interface PresetInfo {
        name: string,
        ws_url: string,
    }

    let presets: string[] = $state([]);
    let presets_name_ws: PresetInfo[] = $state([]);
    let adding_preset: boolean = $state(false);
    let preset_base = {
        font_size: 22,
        vertical: false,
    };

    let anki_port: number = $state(data.anki_settings.port);
    let anki_decks: string[] = $state([]);
    let anki_note_types: string[] = $state([]);
    let rules = $state(data.anki_settings.to_analyze);

    $effect(() => {
        console.log(rules);
    });

    if (browser) {
        presets = JSON.parse(localStorage.getItem("texthooker_presets")?? "[]");
        for (const preset_name of presets) {
            const stored = localStorage.getItem(`texthooker_preset_${preset_name}`);
            if (stored) {
                const preset = JSON.parse(stored);
                presets_name_ws.push({
                    name: preset_name,
                    ws_url: preset.websocket_url
                })
            }
        }

        anki_decks = JSON.parse(localStorage.getItem("anki_decks")?? "[]");
        anki_note_types = JSON.parse(localStorage.getItem("anki_note_types")?? "[]");
    }

    $effect(() => {
        if (presets) {
            localStorage.setItem("texthooker_presets", JSON.stringify(presets));
        }
    });

    function addPreset() {
        let preset_name = (document.querySelector("input[name='preset-name']") as HTMLInputElement)?.value;
        let preset_ws = (document.querySelector("input[name='preset-ws']") as HTMLInputElement)?.value;
        
        if (!(preset_name && preset_ws)) {
            alert("name or WS not set.")
            return;
        }

        presets.push(preset_name);

        let new_preset = {
            websocket_url: preset_ws,
            font_size: preset_base.font_size,
            vertical: preset_base.vertical,
        }
        localStorage.setItem(`texthooker_preset_${preset_name}`, JSON.stringify(new_preset));
    
        presets_name_ws.push({
            name: preset_name,
            ws_url: new_preset.websocket_url
        });
    }

    function deletePreset(name: string) {
        if (!presets.includes(name)) { return; }

        if (presets.length == 1) {
            alert("Cannot delete last preset.")
            return;
        }

        presets = presets.filter(item => item != name);
        presets_name_ws = presets_name_ws.filter(item => item.name != name);
        localStorage.removeItem(`texthooker_preset_${name}`);
    }

    async function loadAnkiData() {
        try {
            const res = await fetch("http://127.0.0.1:8000/anki/anki_decks_info");
            const anki_info = await res.json();

            anki_decks = anki_info.decks;
            anki_note_types = anki_info.note_types;

            localStorage.setItem("anki_decks", JSON.stringify(anki_decks));
            localStorage.setItem("anki_note_types", JSON.stringify(anki_note_types));

            for (let [note_type, fields] of Object.entries(anki_info.note_types_fields)) {
                localStorage.setItem(`anki_note_type_${note_type}`, JSON.stringify(fields));
            }
            

        } catch (error) {
            alert(error);
        }
    }

    function get_fields(note_type: string) {
        if (browser) {
            return JSON.parse(localStorage.getItem(`anki_note_type_${note_type}`)?? "[]");
        } else {
            return [];
        }
        
    }

    async function updateAnkiSettings() {
        const new_settings = {
            port: anki_port,
            to_analyze: rules
        }

        try {
            const res = await fetch("http://127.0.0.1:8000/options/anki_settings",{
                method: "PUT",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(new_settings)
            });

        } catch (error) {
            alert(error);
        }
    }



</script>

{#snippet delete_button(delFunc: () => any)}
    <button class="mx-2 hover:text-red-700 active:text-red-500 hover:cursor-pointer" style="grid-area:close" title="Hide Tasks" onclick={delFunc}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6" viewBox="0 0 15 15">
            <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
        </svg>
    </button>
{/snippet}

<div class="flex justify-center">
    <div class="px-4 max-w-full w-4xl flex flex-col items-center">
        <KnownBar known_morphemes={data.known_morphemes}/>

        <div class="w-full flex justify-between items-baseline">
            <h1>Recently Opened Books</h1>
            <a href="/books" class="text-nowrap">Show All Books</a>
        </div>

        <BookCarousel books={data.books}/>

        <h1>TextHooker</h1>

        <ul class="w-[calc(100%-1rem)] p-3 bg-neutral-700 rounded-md flex flex-col gap-3">

            {#each presets_name_ws as preset_info}
                <li class="flex justify-between">
                    <a href={`/texthooker?preset=${preset_info.name}`}>{preset_info.name}: <span class="text-neutral-400">[ {preset_info.ws_url} ]</span></a>
                    {@render delete_button(() => {deletePreset(preset_info.name)})}
                </li>
            {/each}

            {#if adding_preset}
                <li class="flex justify-between gap-3">
                    <div class="flex justify-end gap-3 items-center grow">
                        <label for="preset-name">Name</label>
                        <input class="bg-neutral-600 rounded-md px-2 grow w-0" name="preset-name" type="text"/>
                    </div>
                    
                    <div class="flex justify-end gap-3 items-center grow">
                        <label for="preset-ws">WS</label>
                        <input class="bg-neutral-600 rounded-md px-2 grow w-0" name="preset-ws" type="text"/>
                    </div>

                    <div class="flex justify-end gap-3 grow-0">
                        <button class="{btn_shared} py-1 px-2 rounded-md" onclick={addPreset}>Confirm</button>
                        <button class="{btn_shared} py-1 px-2 rounded-md" onclick={() => { adding_preset = false; }}>Cancel</button>
                    </div>
                </li>
            {/if}

            <li>
                <button
                    class="hover:text-sky-700 active:text-sky-600 cursor-pointer"
                    onclick={() => { adding_preset = true; }}
                >
                    Add preset
                </button>
            </li>
        </ul>

        <h1>Anki Settings</h1>

        <div class="w-[calc(100%-1rem)]">
            <div class="flex justify-between w-full gap-2">
                <label for="AnkiPort" class="grow">AnkiConnect PORT</label>
                <input
                    name="AnkiPort"
                    type="number"
                    defaultValue="8765"
                    bind:value={anki_port}
                    min="0"
                    max="65535"
                    class="w-auto bg-neutral-600 rounded-sm text-center hide-input-spinners"
                >
                <button class="w-auto {btn_shared} py-1 px-2 rounded-sm" onclick={loadAnkiData}>
                    Connect
                </button>
            </div>

            <h2 class="w-full mt-4">Morphemes Sources:</h2>
            <p class="w-full text-sm text-neutral-400">Connect to Anki to retrieve decks and note types data before adding rules.</p>
       
            <table class="w-full mt-4 rounded-md border-separate border-spacing-0 border border-neutral-900 overflow-hidden">
                
                <thead class="bg-neutral-700">
                    <tr>
                        <th>Deck</th>
                        <th>Note Type</th>
                        <th>Text Field</th>
                        <th class="w-4"></th>
                    </tr>
                </thead>

                <tbody>
                    {#each rules as rule, i}
                        <tr>
                            <td>
                                <select name={`rule-${i}-deck`} bind:value={rule.deck}>
                                    {#each anki_decks as deck}
                                        <option value={deck}>{deck}</option>
                                    {/each}
                                </select>
                            </td>
                            <td>
                                <select name={`rule-${i}-notetype`} bind:value={rule.note_type}>
                                    {#each anki_note_types as note_type}
                                        <option value={note_type}>{note_type}</option>
                                    {/each}
                                </select>
                            </td>
                            <td>
                                <select name={`rule-${i}-textfield`} bind:value={rule.text_field}>
                                    {#each get_fields(rule.note_type) as field}
                                        <option value={field}>{field}</option>
                                    {/each}
                                </select>
                            </td>
                            <td>
                                {@render delete_button(() => {rules.splice(i, 1)})}
                            </td>
                        </tr>
                    {/each}
                    <tr class="h-10"></tr>

                    <tr>
                        <td colspan="4" class="bg-neutral-700 p-0!">
                            <button
                                class="w-full py-1 px-2 {btn_shared}"
                                onclick={() => {
                                    rules.push({
                                        deck: "",
                                        note_type: "",
                                        text_field: "",
                                    });
                                }}    
                            >
                                Add Rule
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <button
            class="w-full px-2 py-1 my-5 bg-sky-500 hover:bg-sky-600 active:bg-sky-700 cursor-pointer rounded-md"
            onclick={updateAnkiSettings}
        >
            Apply and Save
        </button>

    </div>
</div>

<style>

    h1 {
        width: 100%;
        font-size: 1.5rem;
        margin-top: 1.25rem;
        margin-bottom: 0.75rem;
    }

    th {
        padding-inline: 0.25rem;
        padding-block: 0.25rem;
    }

    td {
        padding-inline: 0.25rem;
        padding-block: 0.5rem;
        border-color: #191919;
        border-left: 0.10rem;
        border-right: 0.10rem;
    }

    tr {
        margin-block: 1rem;
    }

    tr:last-child {
        width: fit-content;
    }

    select {
        width: 100%;
        padding:0.25rem;
        background-color: #191919;
        border-radius: 0.25rem;
    }

    a:hover {
        color: var(--color-sky-700);
    }

    a:active {
        color: var(--color-sky-600);
    }

</style>