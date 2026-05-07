<script lang="ts">
    import GridDisplay from "$lib/components/GridDisplay.svelte";
    let { data } = $props();
</script>

<div class="flex flex-col h-screen">
    <div class="shrink-0 h-11 w-full bg-neutral-900">Test</div>

    <GridDisplay items={data.books} item_min_w={"12.5rem"}/>
</div>

<style>


</style>