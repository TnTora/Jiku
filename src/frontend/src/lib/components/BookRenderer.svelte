<script lang="ts">
    let xhtml_content: string;

</script>

<svelte:head>
    <link href="../style/book-style.css" rel="stylesheet" type="text/css"/>

</svelte:head>

<div class="overflow-scroll! w-full! h-screen! px-4! bg-neutral-800!" style="column-width:40vw; column-gap: 3rem;">
    {@html xhtml_content}
</div>
