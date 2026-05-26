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

    async function deleteBook(book_id: number) {
        try {
            const res = await fetch(`http://127.0.0.1:8000/books/delete_book/${book_id}`, {
                method: "DELETE",
            });
            items = items.filter( e => e.id != book_id);
        } catch (error) {
            console.error(`Error deleting book ${book_id}`, error);
            errors.push({
                short: `Error deleting book ${book_id}`,
                details: error,
            });
            throw error;
        }
    }

</script>


<GridDisplay {items} bind:selecting={selecting} bind:selected={selected}>
    {#snippet children(item: any)}
        <BookGridItem
            {item}
            deleteBook={async () => {
                await deleteBook(item.id);
            }}
        />
    {/snippet}
</GridDisplay>


<style>

</style>