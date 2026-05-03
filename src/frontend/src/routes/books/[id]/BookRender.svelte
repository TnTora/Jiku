<script lang="ts">
    import { tick } from "svelte";
    let { content, onUpdateCallback} = $props();

    $effect.pre(() => {
        if (!content) { return };
        tick().then(() => {
            onUpdateCallback();
        });
    });

</script>

{@html content}

