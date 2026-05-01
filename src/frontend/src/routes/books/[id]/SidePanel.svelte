<script lang="ts">
    import { clickOutside } from "$lib/utils/clickOutside";
    import { fly } from "svelte/transition";

    let { book, onoutsideclick } = $props();

    let tab: "toc" | "spine" | "bookmarks" = $state("toc");

</script>

<div transition:fly={{x:-320, duration:200, opacity:0.5}} use:clickOutside={"button[title=TOC]"} {onoutsideclick} class="absolute top-11 w-80 bg-neutral-800 border-neutral-600 h-[calc(100vh-2.75rem)] overflow-scroll z-20">
    <div id="tabs" class="mt-4 mb-4 mx-4 py-3 bg-[#1B1B1B] rounded-full border border-neutral-900 sticky top-0 flex items-center justify-evenly gap-5 font-semibold text-sm">
        <button title="TOC" onclick={() => { tab = "toc" }} class="{(tab == "toc")?"underline underline-offset-4":""}">
            TOC
        </button>

        <button title="Spine" onclick={() => { tab = "spine" }} class="{(tab == "spine")?"underline underline-offset-4":""}">
            Spine
        </button>

        <button title="Bookmarks" onclick={() => { tab = "bookmarks" }} class="{(tab == "bookmarks")?"underline underline-offset-4":""}">
            Bookmarks
        </button>
    </div>
    {#if tab == "toc"}
        <ul>
        {#each book.toc as entry}
            <li>{entry.title}</li>
        {/each}
        </ul>
    {:else if tab == "spine"}
        <ul>
        {#each book.spine as entry}
            <li>{entry}</li>
        {/each}
        </ul>
    {:else}
        <ul>
        {#each book.bookmarks as entry}
            <li>{entry.name}</li>
        {/each}
        </ul>
    {/if}
</div>


<style>

button {
    cursor: pointer;
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