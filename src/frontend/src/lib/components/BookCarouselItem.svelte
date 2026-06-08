<script lang="ts">
    let { item } = $props();
</script>


<a href="{`/books/${item.id}`}" class="h-full w-full">
    <div
        class="book-item border border-neutral-600 active:border-neutral-400 active:border-2 bg-neutral-700 w-full h-full rounded-lg overflow-hidden cursor-pointer"
        style="{item.thumb? `background-image: url(${item.static_url}/${item.id}/images/${item.thumb});`: ""}"
    >
        <div class="relative h-full flex flex-col justify-between {item.thumb? "opacity-0 hover:opacity-100": ""} transition-opacity duration-100">
            <div class="bg-neutral-700/80 text-neutral-300 text-sm h-fit p-1">
                {item.title}
            </div>
        
            <div class="bg-neutral-700/80 text-neutral-300 text-xs h-fit p-1">
                {#each item.creators as creator}
                    {creator};
                {/each}
            </div>
        </div>
        
    </div>
</a>

<style>

.book-item {
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}

</style>