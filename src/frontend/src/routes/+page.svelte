<script lang="ts">
    import KnownBar from "$lib/components/KnownBar.svelte";
    import BookCarousel from "$lib/components/BookCarousel.svelte";

    let { data } = $props();
    let btn_shared = "bg-neutral-700 hover:bg-neutral-900 active:bg-neutral-950 cursor-pointer";
</script>

{#snippet delete_button(delFunc)}
    <button class="mx-2 hover:text-red-700 active:text-red-500 hover:cursor-pointer" style="grid-area:close" title="Hide Tasks" onclick={delFunc}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6" viewBox="0 0 15 15">
            <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
        </svg>
    </button>
{/snippet}

<div class="flex justify-center">
    <div class="px-4 max-w-full w-4xl flex flex-col items-center">
        <KnownBar />

        <div class="w-full flex justify-between items-baseline">
            <h1>Recently Opened Books</h1>
            <a href="/books" class="text-nowrap">Show All Books</a>
        </div>

        <BookCarousel books={data.books}/>

        <h1>TextHooker</h1>

        <ul class="w-[calc(100%-1rem)] p-3 bg-neutral-700 rounded-md flex flex-col gap-3">
            <li class="flex justify-between">
                <a href="">Default: <span class="text-neutral-400">[ http://localhost:6000 ]</span></a>
                {@render delete_button(() => {})}
            </li>
            
            <li class="flex justify-between">
                <a href="">Custom: <span class="text-neutral-400">[ http://localhost:9000 ]</span></a>
                {@render delete_button(() => {})}
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
                    value={data.anki_settings.port}
                    min="0"
                    max="65535"
                    class="w-auto bg-neutral-600 rounded-sm text-center hide-input-spinners"
                >
                <button class="w-auto {btn_shared} py-1 px-2 rounded-sm">
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
                    <tr>
                        <td>
                            <select name="rule-1-deck">
                                <option>Test 1</option>
                                <option>Test 2</option>
                            </select>
                        </td>
                        <td>
                            <select name="rule-1-notetype">
                                <option>Test 1</option>
                                <option>Test 2</option>
                            </select>
                        </td>
                        <td>
                            <select name="rule-1-textfield">
                                <option>Test 1</option>
                                <option>Test 2</option>
                            </select>
                        </td>
                        <td>
                            {@render delete_button(() => {})}
                        </td>
                    </tr>
                    <tr class="h-10"></tr>

                    <tr>
                        <td colspan="4" class="bg-neutral-700 p-0!">
                            <button class="w-full py-1 px-2 {btn_shared}">Add Rule</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <button class="w-full px-2 py-1 my-5 bg-sky-500 hover:bg-sky-600 active:bg-sky-700 cursor-pointer rounded-md">
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