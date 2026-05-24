<script lang="ts">
    import BookGridItem from "./BookGridItem.svelte";
    import { getJikuErrorsContext } from "$lib/utils/context";

    const errors = getJikuErrorsContext();

    let { items, onItemClickCapture, selected = null, item_min_w = null } = $props();

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


<div class="grid-container px-2 py-2 items-center" style="{item_min_w? `--item-min-w: ${item_min_w};`: ""}">
    {#each items as item}
        <div 
            class="{(selected?.has(item))? "selected":""} relative h-[calc(var(--item-min-w)*1.34)] w-full text-center flex items-center justify-center"
            onclickcapture={onItemClickCapture(item)}
        >
            <BookGridItem
                {item}
                deleteBook={async () => {
                    await deleteBook(item.id);
                }}
            />
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