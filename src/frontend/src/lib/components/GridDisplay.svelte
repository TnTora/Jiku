<script lang="ts">
    import BookGridItem from "./BookGridItem.svelte";
    let { items, item_min_w = null } = $props();

</script>


<div class="grid-container px-2 py-2 items-center" style="{item_min_w? `--item-min-w: ${item_min_w};`: ""}">
    {#each items as item}
        <div class="relative h-[calc(var(--item-min-w)*1.34)] w-full text-center flex items-center justify-center">
            <BookGridItem {item}/>
        </div>
    {/each}
</div>


<style>

.grid-container {
    --item-min-w: 12.5rem;
    display: grid;
    /* grid-template-columns: repeat(auto-fit, minmax(var(--item-min-w), 1fr)); */
    grid-template-columns: repeat(auto-fit, var(--item-min-w));
    gap: 1rem;
    justify-content: space-evenly;
}

</style>