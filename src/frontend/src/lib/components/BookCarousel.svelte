<script lang="ts">
	import type { BookInfoResponse } from "$lib/api_types/books";
    import BookCarouselItem from "./BookCarouselItem.svelte";

    let { books }: {books: BookInfoResponse[]} = $props();

</script>

<ul class="w-full flex gap-3 overflow-x-scroll" style="--item-w:12.5rem">
    {#each books as book}
        <li class="h-[calc(var(--item-w)*1.34)] w-50 shrink-0">
            <BookCarouselItem item={book} />
        </li>
    {/each}
</ul>