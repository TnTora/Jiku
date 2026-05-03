<script lang="ts">
    import { onMount } from "svelte";
    let { content, onMountCallback} = $props();

    onMount(() => {
        onMountCallback();
    })

</script>

{@html content}

