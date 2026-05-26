<script lang="ts">
    import { SvelteSet } from "svelte/reactivity";
    import { getJikuErrorsContext } from "$lib/utils/context";

    const errors = getJikuErrorsContext();

    let { items, selecting = $bindable(false), selected = $bindable(new SvelteSet()), item_min_w = null, children } = $props();

    function onItemClickCapture(item: any) {
        return (e: Event) => {
            if (!selecting) { return; }

            console.log("selected", selected);

            e.stopPropagation();
            e.preventDefault();

            if (selected.has(item)){
                selected.delete(item);
            } else {
                selected.add(item);
            }
        }
    };

</script>


<div class="grid-container px-2 py-2 items-center" style="{item_min_w? `--item-min-w: ${item_min_w};`: ""}">
    {#each items as item}
        <div 
            class="{(selected?.has(item))? "selected":""} relative h-[calc(var(--item-min-w)*1.34)] w-full text-center flex items-center justify-center"
            onclickcapture={onItemClickCapture(item)}
        >
            {@render children(item)}
        </div>
    {/each}
</div>


<style>

div.selected {
    border: 2px solid;
    border-color: var(--color-sky-600);
    border-radius: var(--radius-lg) /* 0.375rem = 6px */;
}

.grid-container {
    --item-min-w: 12.5rem;
    display: grid;
    /* grid-template-columns: repeat(auto-fit, minmax(var(--item-min-w), 1fr)); */
    grid-template-columns: repeat(auto-fit, var(--item-min-w));
    gap: 1rem;
    justify-content: space-evenly;
}

</style>