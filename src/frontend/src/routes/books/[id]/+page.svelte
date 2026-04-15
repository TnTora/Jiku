<script lang="ts">
    import BookRenderer from "$lib/components/BookRenderer.svelte";
    let { params } = $props();
    console.log(params.id);
</script>

<BookRenderer />