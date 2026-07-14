<script lang="ts">
    import GridDisplay from "$lib/components/GridDisplay.svelte";
    import BookGridItem from "./BookGridItem.svelte";
    import { SvelteSet } from "svelte/reactivity";
    import { getJikuErrorsContext } from "$lib/utils/context";

    const errors = getJikuErrorsContext();

    interface Props<T> {
        items: Array<T>,
        selecting: boolean,
        selected: SvelteSet<T>,
        item_min_w: string | null
    }

    let { items, selecting = $bindable(false), selected = $bindable(new SvelteSet()), item_min_w = null }: Props<any> = $props();

</script>


<GridDisplay {items} bind:selecting={selecting} bind:selected={selected} {item_min_w}>
    {#snippet children(item: any)}
        <BookGridItem {item}/>
    {/snippet}
</GridDisplay>


<style>

</style>