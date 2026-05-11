<script lang="ts">
	import { title } from "process";

    let collections = [
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7",
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7",
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7",
        "Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7"
    ];
    let authors = ["Author 1", "Author 2", "Author 3"];

    let tab: "collections" | "authors" = $state("collections");

    let editing: boolean = $state(false);

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
            <li class="flex items-center justify-between {editing? "editing": ""}">
                <button>
                    {collection}
                </button>
            {#if editing}
                <div class="flex gap-1">
                    <button title="Rename"
                        class="hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                        onclick={(e) => {
                            e.stopPropagation();
                        }}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                            <path fill="currentColor" d="M14.5 2a.48.48 0 0 1 .352.148A.48.48 0 0 1 15 2.5a.48.48 0 0 1-.148.352A.48.48 0 0 1 14.5 3H13v14h1.5a.48.48 0 0 1 .352.148a.48.48 0 0 1 .148.352a.48.48 0 0 1-.148.352a.48.48 0 0 1-.352.148h-4a.48.48 0 0 1-.352-.148A.48.48 0 0 1 10 17.5a.48.48 0 0 1 .148-.352A.48.48 0 0 1 10.5 17H12V3h-1.5a.48.48 0 0 1-.352-.148A.48.48 0 0 1 10 2.5a.48.48 0 0 1 .148-.352A.48.48 0 0 1 10.5 2zM11 5H5q-.414 0-.773.156a2.1 2.1 0 0 0-.641.43a1.9 1.9 0 0 0-.43.633Q3.008 6.579 3 7v6q0 .414.156.773q.157.36.43.641t.633.43T5 15h6v1H5q-.625 0-1.164-.234a3.1 3.1 0 0 1-.953-.641A2.95 2.95 0 0 1 2 13V7q0-.617.234-1.164a3 3 0 0 1 .641-.953q.406-.406.953-.649Q4.375 3.992 5 4h6zm4-1q.618 0 1.164.234a3 3 0 0 1 1.602 1.602Q18.008 6.39 18 7v6q0 .625-.234 1.164q-.235.54-.641.953q-.406.414-.96.649A3 3 0 0 1 15 16h-1v-1h1q.414 0 .773-.156a2.1 2.1 0 0 0 .641-.43a1.9 1.9 0 0 0 .43-.633q.148-.36.156-.781V7a1.9 1.9 0 0 0-.156-.773a2.1 2.1 0 0 0-.43-.641a1.9 1.9 0 0 0-.633-.43Q15.421 5.008 15 5h-1V4zM7.5 6a.5.5 0 0 1 .454.292l2.75 6a.5.5 0 1 1-.908.416l-.784-1.71L9 11H6l-.013-.002l-.783 1.71a.5.5 0 1 1-.908-.416l2.75-6l.034-.063A.5.5 0 0 1 7.5 6m-1.055 4h2.11L7.5 7.698z" />
                        </svg>
                    </button>
                    <button title="Delete"
                        class="text-red-500 hover:text-red-800 active:text-red-400 hover:cursor-pointer"
                        onclick={(e) => {
                            e.stopPropagation();
                        }}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                            <path fill="currentColor" d="M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6zm2.46-7.12l1.41-1.41L12 12.59l2.12-2.12l1.41 1.41L13.41 14l2.12 2.12l-1.41 1.41L12 15.41l-2.12 2.12l-1.41-1.41L10.59 14zM15.5 4l-1-1h-5l-1 1H5v2h14V4z" />
                        </svg>
                    </button>
                </div>
            {/if}
            </li>
        {/each}
        </ul>

        <div class="fixed bottom-0 w-80 bg-neutral-800 border-neutral-700 border-t flex items-center justify-between">
            <div class="px-5 py-1 flex items-center gap-4">
            {#if editing}
                <button
                    title="Cancel Edit"
                    class="text-sm text-red-700 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                    onclick={() => { editing = false; }}
                >
                    Cancel
                </button>
                <button
                    title="Confirm Edit"
                    class="text-sm text-neutral-400 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                    onclick={() => { editing = false; }}
                >
                    Confirm
                </button>
            {:else}
                <button
                    title="Edit Collection"
                    class="text-sm text-neutral-500 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer"
                    onclick={() => { editing = true; }}
                >
                    Edit Collections
                </button>
            {/if}
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

li:not(.editing):active {
    background-color: #1A1A1A;
}

</style>