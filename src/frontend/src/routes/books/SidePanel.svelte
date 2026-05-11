<script lang="ts">
    let collections = [
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7",
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7",
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7",
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7"
    ];
    let authors = ["Author 1", "Author 2", "Author 3"];

    let tab: "collections" | "authors" = $state("collections");

</script>

<div
    class="relative w-80 border-neutral-600 border-r h-full overflow-scroll z-20"
>
    
    <div id="tabs" class="mb-4 mx-2 py-3 bg-[#1B1B1B] rounded-md border border-neutral-900 sticky top-0 flex items-center justify-evenly gap-5 font-semibold text-sm">
        <button title="Collections" onclick={() => { tab = "collections" }} class="{(tab == "collections")?"underline underline-offset-4":""}">
            Collections
        </button>

        <button title="Authors" onclick={() => { tab = "authors" }} class="{(tab == "authors")?"underline underline-offset-4":""}">
            Authors
        </button>
    </div>

    {#if tab == "collections"}
        <ul>
        {#each collections as collection}
            <li>
                <button>
                    {collection}
                </button>
            </li>
        {/each}
        </ul>

        <div class="fixed bottom-0 w-80 bg-neutral-800 border-neutral-700 border-t flex items-center justify-between">
            <div class="px-2 py-1 flex items-center">
                <button
                    title="Edit Collection"
                    class="text-sm text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                >
                    Edit Collections
                </button>
            </div>
            <div class="flex items-center">
                <button
                    title="Delete Collection"
                    class="aspect-square h-7 text-sm bg-neutral-900 border-neutral-700 hover:bg-neutral-950 active:bg-[#353535] border"
                >
                    -
                </button>
                <button
                    title="New Collection"
                    class="aspect-square h-7 text-sm bg-neutral-900 border-neutral-700 hover:bg-neutral-950 active:bg-[#353535] border"
                >
                    +
                </button>
            </div>
        </div>

    {:else if tab == "authors"}
        <ul>
        {#each authors as author}
            <li>
                <button>
                    {author}
                </button>
            </li>
        {/each}
        </ul>
    {/if}
</div>


<style>

button {
    cursor: pointer;
}

li > button {
    width: 100%;
    text-align: left;
}

ul {
    padding-bottom: 1.5rem;
}

li {
    padding-inline: 1.5rem;
    padding-block: 0.25rem;
    cursor: pointer;
}

li:hover {
    background-color: #333;
}

li:active {
    background-color: #1A1A1A;
}

</style>